"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.security import setup_logging, setup_cors, RequestIDMiddleware, RateLimitMiddleware
from app.routers import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database
    init_db()
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.app_version,
        docs_url=settings.api_docs_url,
        redoc_url=settings.api_redoc_url,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # Setup CORS
    setup_cors(app)

    # Add middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all exceptions globally."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Include routers
    app.include_router(api_router, prefix=settings.api_prefix)

    logger.info("FastAPI application configured")
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
