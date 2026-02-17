"""License service — state machine with Gumroad validation + offline grace.

Storage: DB settings table keys:
  license_status, trial_start_at, trial_days,
  license_entitlement, license_key, license_validated_at, grace_start_at
"""

import logging
import time
from typing import Optional

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings as app_settings

logger = logging.getLogger(__name__)

_TRIAL_DAYS_KEY = "trial_days"
_TRIAL_START_KEY = "trial_start_at"
_LICENSE_STATUS_KEY = "license_status"
_LICENSE_ENTITLEMENT_KEY = "license_entitlement"
_LICENSE_KEY = "license_key"
_LICENSE_VALIDATED_AT_KEY = "license_validated_at"
_GRACE_START_KEY = "grace_start_at"

_GRACE_PERIOD_DAYS = 7
_REVALIDATION_INTERVAL_MS = 24 * 60 * 60 * 1000  # 24 hours

GUMROAD_VERIFY_URL = "https://api.gumroad.com/v2/licenses/verify"


# ─── DB helpers ─────────────────────────────────────────────────────────


def _get_setting(db: Session, key: str) -> Optional[str]:
    row = db.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": key}).fetchone()
    return row[0] if row else None


def _set_setting(db: Session, key: str, value: str):
    existing = _get_setting(db, key)
    if existing is not None:
        db.execute(text("UPDATE settings SET value=:v WHERE key=:k"), {"k": key, "v": value})
    else:
        db.execute(text("INSERT INTO settings(key,value) VALUES(:k,:v)"), {"k": key, "v": value})


def _del_setting(db: Session, key: str):
    db.execute(text("DELETE FROM settings WHERE key=:k"), {"k": key})


def _now_ms() -> int:
    return int(time.time() * 1000)


def _ms_to_days(ms: int) -> float:
    return ms / (1000 * 60 * 60 * 24)


# ─── Trial ──────────────────────────────────────────────────────────────


def _ensure_trial(db: Session):
    """Initialize trial if no license state exists."""
    if _get_setting(db, _TRIAL_START_KEY) is None:
        now = _now_ms()
        _set_setting(db, _TRIAL_START_KEY, str(now))
        _set_setting(db, _TRIAL_DAYS_KEY, str(app_settings.trial_days))
        _set_setting(db, _LICENSE_STATUS_KEY, "trial_active")
        db.commit()


# ─── Gumroad validation ────────────────────────────────────────────────


def _validate_gumroad(license_key: str) -> dict:
    """Call Gumroad license verify API.

    Returns {"valid": True/False, "plan": str, "error": str|None}.
    If PINUP_GUMROAD_PRODUCT_ID is unset, falls back to offline (accepts key ≥8 chars).
    """
    product_id = app_settings.gumroad_product_id
    if not product_id:
        # Offline fallback — accept any 8+ char key (dev / self-hosted)
        if len(license_key) >= 8:
            return {"valid": True, "plan": "pro", "error": None}
        return {"valid": False, "plan": "trial", "error": "Invalid license key"}

    try:
        resp = httpx.post(
            GUMROAD_VERIFY_URL,
            data={"product_id": product_id, "license_key": license_key},
            timeout=10,
        )
        data = resp.json()
        if data.get("success"):
            purchase = data.get("purchase", {})
            variants = purchase.get("variants", "")
            plan = "pro_plus" if "plus" in variants.lower() else "pro"
            return {"valid": True, "plan": plan, "error": None}
        return {"valid": False, "plan": "trial", "error": data.get("message", "Invalid key")}
    except httpx.HTTPError as exc:
        logger.warning("Gumroad API unreachable: %s", exc)
        return {"valid": False, "plan": "trial", "error": "Could not reach license server"}


def _should_revalidate(db: Session) -> bool:
    """True if >24h since last successful validation."""
    last = _get_setting(db, _LICENSE_VALIDATED_AT_KEY)
    if not last:
        return True
    return (_now_ms() - int(last)) > _REVALIDATION_INTERVAL_MS


# ─── Grace period ──────────────────────────────────────────────────────


def _check_grace_period(db: Session) -> dict | None:
    """If in grace period, calculate days left. Returns status dict or None."""
    grace_start = _get_setting(db, _GRACE_START_KEY)
    if not grace_start:
        return None
    elapsed_days = _ms_to_days(_now_ms() - int(grace_start))
    days_left = max(0, int(_GRACE_PERIOD_DAYS - elapsed_days))
    if days_left > 0:
        return {
            "status": "grace_period",
            "days_left": days_left,
            "entitled": True,
            "plan": "pro",
        }
    # Grace period expired
    _set_setting(db, _LICENSE_STATUS_KEY, "trial_expired")
    _del_setting(db, _LICENSE_ENTITLEMENT_KEY)
    _del_setting(db, _LICENSE_KEY)
    _del_setting(db, _GRACE_START_KEY)
    db.commit()
    return None


def _enter_grace_period(db: Session):
    """Transition to grace_period state."""
    _set_setting(db, _LICENSE_STATUS_KEY, "grace_period")
    _set_setting(db, _GRACE_START_KEY, str(_now_ms()))
    db.commit()
    logger.info("License entered 7-day grace period")


# ─── Public API ─────────────────────────────────────────────────────────


def get_license_status(db: Session) -> dict:
    """Compute current license state with periodic revalidation."""
    _ensure_trial(db)

    status_raw = _get_setting(db, _LICENSE_STATUS_KEY) or "trial_active"
    entitlement = _get_setting(db, _LICENSE_ENTITLEMENT_KEY)
    stored_key = _get_setting(db, _LICENSE_KEY)

    # ── Licensed user path ──────────────────────────────────────────────
    if entitlement and status_raw in ("licensed_active", "grace_period"):
        # Grace period path
        if status_raw == "grace_period":
            grace = _check_grace_period(db)
            if grace:
                return grace
            # Grace expired — fall through to trial

        # Periodic revalidation (non-blocking)
        elif stored_key and _should_revalidate(db):
            result = _validate_gumroad(stored_key)
            if result["valid"]:
                _set_setting(db, _LICENSE_VALIDATED_AT_KEY, str(_now_ms()))
                db.commit()
                return {
                    "status": "licensed_active",
                    "days_left": 999,
                    "entitled": True,
                    "plan": result["plan"],
                }
            else:
                # Validation failed — enter grace period
                _enter_grace_period(db)
                return {
                    "status": "grace_period",
                    "days_left": _GRACE_PERIOD_DAYS,
                    "entitled": True,
                    "plan": "pro",
                }
        else:
            # No revalidation needed or no stored key (offline mode)
            return {
                "status": "licensed_active",
                "days_left": 999,
                "entitled": True,
                "plan": "pro",
            }

    # ── Trial path ──────────────────────────────────────────────────────
    trial_start = int(_get_setting(db, _TRIAL_START_KEY) or "0")
    trial_days = int(_get_setting(db, _TRIAL_DAYS_KEY) or str(app_settings.trial_days))
    elapsed_days = _ms_to_days(_now_ms() - trial_start)
    days_left = max(0, int(trial_days - elapsed_days))

    status = "trial_active" if days_left > 0 else "trial_expired"
    _set_setting(db, _LICENSE_STATUS_KEY, status)
    db.commit()

    return {
        "status": status,
        "days_left": days_left,
        "entitled": status == "trial_active",
        "plan": "trial",
    }


def activate_license(db: Session, license_key: str) -> dict:
    """Activate with a license key via Gumroad (or offline fallback)."""
    if not license_key or len(license_key) < 8:
        return {"error": "Invalid license key"}

    result = _validate_gumroad(license_key)
    if not result["valid"]:
        return {"error": result["error"] or "Invalid license key"}

    _set_setting(db, _LICENSE_KEY, license_key)
    _set_setting(db, _LICENSE_ENTITLEMENT_KEY, license_key)
    _set_setting(db, _LICENSE_STATUS_KEY, "licensed_active")
    _set_setting(db, _LICENSE_VALIDATED_AT_KEY, str(_now_ms()))
    # Clear any grace period
    _del_setting(db, _GRACE_START_KEY)
    db.commit()

    return get_license_status(db)


def deactivate_license(db: Session) -> bool:
    """Remove license entitlement, revert to trial state."""
    for key in (_LICENSE_ENTITLEMENT_KEY, _LICENSE_KEY, _LICENSE_VALIDATED_AT_KEY, _GRACE_START_KEY):
        _del_setting(db, key)
    _set_setting(db, _LICENSE_STATUS_KEY, "trial_expired")
    db.commit()
    return True
