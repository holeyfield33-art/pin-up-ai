"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from app.auth import ensure_token
from app.security import setup_logging, RequestIDMiddleware, RateLimitMiddleware
from app.routers import api_router

setup_logging()
logger = logging.getLogger(__name__)

# Will be set on first startup
_install_token: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _install_token
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    # Ensure install token
    db = SessionLocal()
    try:
        _install_token = ensure_token(db)
        if _install_token:
            logger.info("*** INSTALL TOKEN (save this): %s ***", _install_token)
    finally:
        db.close()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    is_prod = settings.environment == "production"
    app = FastAPI(
        title="Pin-Up AI API",
        version=settings.app_version,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)

    # Standard error envelope
    @app.exception_handler(Exception)
    async def _global_exc(request: Request, exc: Exception):
        logger.error("Unhandled: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={
            "code": "DB_ERROR", "message": str(exc), "details": None
        })

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.pinup_port,
        reload=settings.debug,
        log_level=settings.pinup_log_level.lower(),
    )
