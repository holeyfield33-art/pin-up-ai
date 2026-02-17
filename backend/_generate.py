#!/usr/bin/env python3
"""Generate all backend source files for Pin-Up AI."""
import os, pathlib

BASE = pathlib.Path("/workspaces/pin-up-ai/backend")

def write(rel_path: str, content: str):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"  wrote {rel_path}")

# ── models.py ───────────────────────────────────────────────────────────
write("app/models.py", '''\
"""SQLAlchemy ORM models matching db-schema.sql.md spec."""

import hashlib
import time
import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Table, Index
from sqlalchemy.orm import relationship
from app.database import Base


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> str:
    return str(uuid.uuid4())


def _content_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


# ── join tables ─────────────────────────────────────────────────────────
snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", String, ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
Index("idx_snippet_tags_tag", snippet_tags.c.tag_id)

snippet_collections = Table(
    "snippet_collections",
    Base.metadata,
    Column("snippet_id", String, ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("collection_id", String, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
)
Index("idx_snippet_collections_collection", snippet_collections.c.collection_id)


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(String, primary_key=True, default=_new_id)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    language = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    pinned = Column(Integer, nullable=False, default=0)
    archived = Column(Integer, nullable=False, default=0)
    content_hash = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=_now_ms)
    updated_at = Column(Integer, nullable=False, default=_now_ms)

    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets", lazy="selectin")
    collections = relationship("Collection", secondary=snippet_collections, back_populates="snippets", lazy="selectin")


Index("idx_snippets_created_at", Snippet.created_at)
Index("idx_snippets_updated_at", Snippet.updated_at)
Index("idx_snippets_pinned", Snippet.pinned)
Index("idx_snippets_archived", Snippet.archived)
Index("idx_snippets_hash", Snippet.content_hash)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(Text, nullable=False, unique=True)
    color = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=_now_ms)

    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags", lazy="selectin")


Index("idx_tags_name", Tag.name)


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=_now_ms)

    snippets = relationship("Snippet", secondary=snippet_collections, back_populates="collections", lazy="selectin")


Index("idx_collections_name", Collection.name)
''')

# ── schemas.py ──────────────────────────────────────────────────────────
write("app/schemas.py", '''\
"""Pydantic v2 schemas matching api-contract.md exactly."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Error envelope ──────────────────────────────────────────────────────
class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: dict | None = None


# ── Tags ────────────────────────────────────────────────────────────────
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class TagPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class TagOut(BaseModel):
    id: str
    name: str
    color: str | None = None
    created_at: int = 0

class TagOutWithCount(TagOut):
    count: int = 0


# ── Collections ─────────────────────────────────────────────────────────
class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class CollectionPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None

class CollectionOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    created_at: int = 0

class CollectionOutWithCount(CollectionOut):
    count: int = 0


# ── Snippets ────────────────────────────────────────────────────────────
class SnippetCreate(BaseModel):
    title: Optional[str] = None
    body: str = Field(..., min_length=1)
    source: Optional[str] = None
    source_url: Optional[str] = None
    language: Optional[str] = None
    tags: list[str] = Field(default_factory=list)          # tag names
    collections: list[str] = Field(default_factory=list)   # collection names
    pinned: bool = False

class SnippetPatch(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[list[str]] = None
    collections: Optional[list[str]] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None

class SnippetOut(BaseModel):
    id: str
    title: str
    body: str
    language: str | None = None
    source: str | None = None
    source_url: str | None = None
    tags: list[TagOut] = Field(default_factory=list)
    collections: list[CollectionOut] = Field(default_factory=list)
    pinned: int = 0
    archived: int = 0
    created_at: int = 0
    updated_at: int = 0

class SnippetListResponse(BaseModel):
    items: list[SnippetOut]
    total: int

class TagListResponse(BaseModel):
    items: list[TagOutWithCount]
    total: int

class CollectionListResponse(BaseModel):
    items: list[CollectionOutWithCount]
    total: int


# ── Search ──────────────────────────────────────────────────────────────
class SearchResultItem(BaseModel):
    id: str
    title: str
    preview: str
    tags: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)
    source: str | None = None
    language: str | None = None
    created_at: int = 0
    updated_at: int = 0

class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int


# ── Health ──────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    db_path: str
    uptime_ms: int


# ── Export / Import ─────────────────────────────────────────────────────
class ExportRequest(BaseModel):
    format: str = "json"   # json | markdown | bundle
    scope: str = "all"     # all | collection | snippet
    ids: list[str] = Field(default_factory=list)

class ImportResponse(BaseModel):
    ok: bool
    imported: dict
    merged: dict


# ── Stats ───────────────────────────────────────────────────────────────
class StatsResponse(BaseModel):
    totals: dict
    top_tags: list[dict]
    top_collections: list[dict]
    created_counts: dict
    recent_activity: list[dict]
    vault: dict


# ── Settings ────────────────────────────────────────────────────────────
class SettingsOut(BaseModel):
    dedupe_enabled: bool = False
    backup_enabled: bool = False
    backup_schedule: str = "manual"

class SettingsPatch(BaseModel):
    dedupe_enabled: Optional[bool] = None
    backup_enabled: Optional[bool] = None
    backup_schedule: Optional[str] = None

class RotateTokenResponse(BaseModel):
    token: str


# ── License ─────────────────────────────────────────────────────────────
class LicenseStatus(BaseModel):
    status: str   # trial_active | trial_expired | licensed_active | grace_period
    days_left: int = 0
    entitled: bool = False
    plan: str = "trial"  # trial | pro | pro_plus

class LicenseActivate(BaseModel):
    license_key: str

class OkResponse(BaseModel):
    ok: bool = True


# ── Backup ──────────────────────────────────────────────────────────────
class BackupInfo(BaseModel):
    name: str
    created_at: int
    db_size_bytes: int
    app_version: str
''')

# ── auth.py ─────────────────────────────────────────────────────────────
write("app/auth.py", '''\
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
''')

# ── main.py ─────────────────────────────────────────────────────────────
write("app/main.py", '''\
"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from app.auth import ensure_token
from app.security import setup_logging, RequestIDMiddleware, RateLimitMiddleware
from app.routers import api_router

setup_logging()
logger = logging.getLogger(__name__)

# Will be set on first startup
_install_token: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _install_token
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    # Ensure install token
    db = SessionLocal()
    try:
        _install_token = ensure_token(db)
        if _install_token:
            logger.info("*** INSTALL TOKEN (save this): %s ***", _install_token)
    finally:
        db.close()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pin-Up AI API",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)

    # Standard error envelope
    @app.exception_handler(Exception)
    async def _global_exc(request: Request, exc: Exception):
        logger.error("Unhandled: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={
            "code": "DB_ERROR", "message": str(exc), "details": None
        })

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.pinup_port,
        reload=settings.debug,
        log_level=settings.pinup_log_level.lower(),
    )
''')

print("Core files written.")
