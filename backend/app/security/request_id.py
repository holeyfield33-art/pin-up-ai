"""Request ID middleware for tracking requests."""

import uuid
import logging
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for storing request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

logger = logging.getLogger(__name__)


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get("")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject request IDs."""

    async def dispatch(self, request: Request, call_next):
        """Process request and inject request ID."""
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in context
        token = request_id_var.set(request_id)
        
        # Add request ID to logger context
        logger_adapter = logging.LoggerAdapter(
            logger,
            {"request_id": request_id}
        )
        
        try:
            # Process request
            response = await call_next(request)
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Reset context
            request_id_var.reset(token)
