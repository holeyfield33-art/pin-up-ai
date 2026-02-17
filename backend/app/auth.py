"""Bearer-token authentication."""

import hashlib
import logging
import secrets
from fastapi import Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger(__name__)

_TOKEN_KEY = "install_token_hash"


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def ensure_token(db: Session) -> str:
    """Create install token if none exists. Returns the plaintext token (only on first run)."""
    row = db.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": _TOKEN_KEY}).fetchone()
    if row:
        return ""  # already exists, plaintext unknown
    token = secrets.token_urlsafe(32)
    db.execute(text("INSERT INTO settings(key,value) VALUES(:k,:v)"), {"k": _TOKEN_KEY, "v": _hash(token)})
    db.commit()
    logger.info("Install token created")
    return token


def rotate_token(db: Session) -> str:
    """Generate new token, store hash, return plaintext."""
    token = secrets.token_urlsafe(32)
    db.execute(text("DELETE FROM settings WHERE key=:k"), {"k": _TOKEN_KEY})
    db.execute(text("INSERT INTO settings(key,value) VALUES(:k,:v)"), {"k": _TOKEN_KEY, "v": _hash(token)})
    db.commit()
    return token


def verify_token(request: Request, db: Session = Depends(get_db)) -> None:
    """FastAPI dependency: verify bearer token. Skip for /api/health."""
    path = request.url.path
    if path.endswith("/health") or path.endswith("/health/ready") or path.endswith("/health/live"):
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "AUTH_INVALID", "message": "Missing bearer token"})
    token = auth[7:]
    row = db.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": _TOKEN_KEY}).fetchone()
    if not row or row[0] != _hash(token):
        raise HTTPException(status_code=401, detail={"code": "AUTH_INVALID", "message": "Invalid token"})
