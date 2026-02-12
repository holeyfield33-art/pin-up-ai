"""API routers."""

from fastapi import APIRouter

from app.routers import health, snippets, tags, collections, search, mcp

api_router = APIRouter()

# Include all routers
api_router.include_router(health.router)
api_router.include_router(snippets.router)
api_router.include_router(tags.router)
api_router.include_router(collections.router)
api_router.include_router(search.router)
api_router.include_router(mcp.router)

__all__ = ["api_router"]
