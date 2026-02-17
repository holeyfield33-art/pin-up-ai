"""Settings router per api-contract.md."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token, rotate_token
from app.schemas import SettingsOut, SettingsPatch, RotateTokenResponse

router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[Depends(verify_token)])

_DEFAULTS = {
    "dedupe_enabled": "false",
    "backup_enabled": "false",
    "backup_schedule": "manual",
}


def _get_settings(db: Session) -> dict:
    result = {}
    for key, default in _DEFAULTS.items():
        row = db.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": key}).fetchone()
        val = row[0] if row else default
        if key in ("dedupe_enabled", "backup_enabled"):
            result[key] = val.lower() in ("true", "1", "yes")
        else:
            result[key] = val
    return result


def _set_setting(db: Session, key: str, value: str):
    existing = db.execute(text("SELECT 1 FROM settings WHERE key=:k"), {"k": key}).fetchone()
    if existing:
        db.execute(text("UPDATE settings SET value=:v WHERE key=:k"), {"k": key, "v": value})
    else:
        db.execute(text("INSERT INTO settings(key,value) VALUES(:k,:v)"), {"k": key, "v": value})


@router.get("", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return _get_settings(db)


@router.patch("", response_model=SettingsOut)
def update_settings(body: SettingsPatch, db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    for key, val in data.items():
        if val is not None:
            _set_setting(db, key, str(val).lower())
    db.commit()
    return _get_settings(db)


@router.post("/rotate-token", response_model=RotateTokenResponse)
def do_rotate_token(db: Session = Depends(get_db)):
    token = rotate_token(db)
    return {"token": token}
