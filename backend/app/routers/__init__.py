"""API routers — central registration."""

from fastapi import APIRouter

from app.routers import (
    health,
    snippets,
    tags,
    collections,
    search,
    export_import,
    backup,
    license,
    settings as settings_router,
    stats,
    mcp,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(snippets.router)
api_router.include_router(tags.router)
api_router.include_router(collections.router)
api_router.include_router(search.router)
api_router.include_router(export_import.router)
api_router.include_router(backup.router)
api_router.include_router(license.router)
api_router.include_router(settings_router.router)
api_router.include_router(stats.router)
api_router.include_router(mcp.router)

__all__ = ["api_router"]
