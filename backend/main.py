import os
import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from routers import snippets, tags, collections
from database import init_db, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment-driven configuration
ENV = os.getenv("PINUP_ENV", "production")
IS_DEV = ENV.lower() in ("development", "dev")

# CORS origins configurable via environment variable (comma-separated)
DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:3000"
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("PINUP_CORS_ORIGINS", DEFAULT_ORIGINS).split(",")
    if o.strip()
]

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("PINUP_RATE_LIMIT", "60"))  # per window
RATE_LIMIT_WINDOW = int(os.getenv("PINUP_RATE_WINDOW", "60"))  # seconds

# Request body size limit (default 1MB)
MAX_BODY_SIZE = int(os.getenv("PINUP_MAX_BODY_SIZE", str(1 * 1024 * 1024)))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter by client IP."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        cutoff = now - self.window_seconds

        # Prune old entries
        self._hits[client_ip] = [t for t in self._hits[client_ip] if t > cutoff]

        if len(self._hits[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(self.window_seconds)},
            )

        self._hits[client_ip].append(now)
        return await call_next(request)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies larger than the configured limit."""

    def __init__(self, app, max_size: int):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    yield


app = FastAPI(
    title="Pin-Up AI Backend",
    description="Local-first AI message highlighter",
    version="0.1.0",
    lifespan=lifespan,
    # Disable interactive API docs in production to reduce attack surface
    docs_url="/docs" if IS_DEV else None,
    redoc_url="/redoc" if IS_DEV else None,
)

# Middleware stack (order matters: outermost first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW,
)
app.add_middleware(BodySizeLimitMiddleware, max_size=MAX_BODY_SIZE)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler — never leak internal details to clients."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers with proper prefixes and tags
app.include_router(snippets.router, prefix="/snippets", tags=["snippets"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(collections.router, prefix="/collections", tags=["collections"])


@app.get("/health", tags=["health"], summary="Health check")
async def health():
    """Health check endpoint — verifies database connectivity."""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "service": "Pin-Up AI Backend"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "service": "Pin-Up AI Backend", "detail": "Database unreachable"},
        )
