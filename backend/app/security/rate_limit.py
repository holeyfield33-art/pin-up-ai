"""Rate limiting middleware."""

import logging
from time import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests: int, period: int):
        """Initialize rate limiter.
        
        Args:
            requests: Number of requests allowed
            period: Time period in seconds
        """
        self.requests = requests
        self.period = period
        self.clients = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request."""
        now = time()
        
        # Remove old timestamps outside the period
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if now - timestamp < self.period
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_id]) >= self.requests:
            return False
        
        # Add current timestamp
        self.clients[client_id].append(now)
        return True

    def evict_stale(self) -> int:
        """Remove clients with no recent activity. Returns number evicted."""
        now = time()
        stale = [cid for cid, ts in self.clients.items() if not ts or now - ts[-1] >= self.period]
        for cid in stale:
            del self.clients[cid]
        return len(stale)


# Global rate limiter
rate_limiter = RateLimiter(
    requests=settings.rate_limit_requests,
    period=settings.rate_limit_period,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Periodic eviction — every 1000 requests
        rate_limiter._call_count = getattr(rate_limiter, '_call_count', 0) + 1
        if rate_limiter._call_count % 1000 == 0:
            rate_limiter.evict_stale()

        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
            )

        return await call_next(request)
