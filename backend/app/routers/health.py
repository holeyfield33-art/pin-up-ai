"""Health check router — no auth required."""

import os
from fastapi import APIRouter
from sqlalchemy import text
from app.config import settings
from app.database import get_uptime_ms, SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "db_path": settings.get_database_path(),
        "uptime_ms": get_uptime_ms(),
    }


@router.get("/health/ready")
def health_ready():
    """Readiness check — verifies DB is accessible."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1")).fetchone()
        return {
            "status": "ready",
            "database": "connected",
            "version": settings.app_version,
        }
    except Exception as exc:
        return {
            "status": "not_ready",
            "database": "error",
            "error": str(exc),
        }
    finally:
        db.close()


@router.get("/health/live")
def health_live():
    """Liveness check — confirms the process is running."""
    return {
        "status": "alive",
        "uptime_ms": get_uptime_ms(),
    }
