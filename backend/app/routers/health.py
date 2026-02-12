"""Health check endpoints."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HealthResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.app_version,
        database=db_status,
    )


@router.get("/ready", response_model=dict)
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check endpoint."""
    try:
        db.execute("SELECT 1")
        return {"ready": True, "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "error": str(e)}


@router.get("/live", response_model=dict)
async def liveness_check():
    """Liveness check endpoint."""
    return {"alive": True, "version": settings.app_version}
