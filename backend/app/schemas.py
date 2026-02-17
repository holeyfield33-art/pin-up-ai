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
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class CollectionPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class CollectionOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    created_at: int = 0
    updated_at: int = 0

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
