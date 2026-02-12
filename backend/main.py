import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import snippets, tags, collections
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pin-Up AI Backend",
    description="Local-first AI message highlighter",
    version="0.1.0",
)

# CORS Configuration for desktop app security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Include routers with proper prefixes and tags
app.include_router(snippets.router, prefix="/snippets", tags=["snippets"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(collections.router, prefix="/collections", tags=["collections"])


@app.get("/health", tags=["health"], summary="Health check")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "Pin-Up AI Backend"}
