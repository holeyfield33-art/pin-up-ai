"""License router per license-subsystem-spec.md."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import LicenseStatus, LicenseActivate, OkResponse
from app.services import license_service as svc

router = APIRouter(prefix="/license", tags=["license"], dependencies=[Depends(verify_token)])


@router.get("/status", response_model=LicenseStatus)
def get_license_status(db: Session = Depends(get_db)):
    return svc.get_license_status(db)


@router.post("/activate", response_model=LicenseStatus)
def activate_license(body: LicenseActivate, db: Session = Depends(get_db)):
    result = svc.activate_license(db, body.license_key)
    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail={"code": "LICENSE_ERROR", "message": result["error"]},
        )
    return result


@router.post("/deactivate", response_model=OkResponse)
def deactivate_license(db: Session = Depends(get_db)):
    svc.deactivate_license(db)
    return {"ok": True}
