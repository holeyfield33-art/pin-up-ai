"""Backup / Restore router per backup-restore-spec.md."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.services import backup_service as svc

router = APIRouter(prefix="/backup", tags=["backup"], dependencies=[Depends(verify_token)])


@router.post("/run")
def run_backup(db: Session = Depends(get_db)):
    """Run a manual backup now."""
    try:
        info = svc.run_backup(db)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "DB_ERROR", "message": str(e)})


@router.get("/list")
def list_backups():
    """List available backups."""
    return {"items": svc.list_backups()}


@router.post("/restore/{name}")
def restore_backup(name: str):
    """Restore from a named backup. Backend restart required after."""
    ok = svc.restore_backup(name)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Backup '{name}' not found"})
    return {"ok": True, "message": "Restored. Please restart the backend."}
