"""Snippet service — CRUD, title/language inference, FTS sync, content hash."""

import hashlib
import logging
import re
import time
import uuid
from typing import Optional

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from app.models import Snippet, Tag, Collection, snippet_tags, snippet_collections, _now_ms
from app.database import rebuild_fts_for_snippet

logger = logging.getLogger(__name__)

# ── Language inference ──────────────────────────────────────────────────
_FENCE_RE = re.compile(r"```(\w+)")


def _infer_language(body: str) -> str:
    """Infer language from fenced code blocks; fallback plaintext."""
    m = _FENCE_RE.search(body)
    if m:
        return m.group(1).lower()
    return "plaintext"


def _infer_title(body: str) -> str:
    """First non-empty line, max 60 chars."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:60]
    return "Untitled"


def _content_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


# ── Upsert helpers for tag/collection by name ──────────────────────────
def _resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    """Upsert tags by normalized name, return ORM objects."""
    result = []
    for raw in names:
        name = raw.strip().lower()
        if not name:
            continue
        tag = db.query(Tag).filter(func.lower(Tag.name) == name).first()
        if not tag:
            tag = Tag(id=str(uuid.uuid4()), name=name, created_at=_now_ms())
            db.add(tag)
            db.flush()
        result.append(tag)
    return result


def _resolve_collections(db: Session, names: list[str]) -> list[Collection]:
    """Upsert collections by normalized name, return ORM objects."""
    result = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        col = db.query(Collection).filter(func.lower(Collection.name) == func.lower(name)).first()
        if not col:
            now = _now_ms()
            col = Collection(id=str(uuid.uuid4()), name=name, created_at=now, updated_at=now)
            db.add(col)
            db.flush()
        result.append(col)
    return result


# ── Limit + dedup helpers ───────────────────────────────────────────────
class SnippetLimitReached(Exception):
    """Free-tier snippet limit exceeded."""

class DuplicateContent(Exception):
    """Content hash already exists in vault."""

_FREE_SNIPPET_LIMIT = 100


def _check_snippet_limit(db: Session):
    """Raise if free tier limit reached."""
    from app.services.license_service import get_license_status
    status = get_license_status(db)
    if status.get("entitled") and status.get("plan") != "trial":
        return  # Pro/licensed users have no limit
    count = db.query(func.count(Snippet.id)).filter(Snippet.archived == 0).scalar() or 0
    if count >= _FREE_SNIPPET_LIMIT:
        raise SnippetLimitReached(
            f"Free tier is limited to {_FREE_SNIPPET_LIMIT} snippets. "
            "Upgrade to Pro for unlimited storage."
        )


def _check_dedupe(db: Session, body: str) -> None:
    """Raise if content hash already exists (when dedupe is enabled)."""
    from sqlalchemy import text as _text
    row = db.execute(_text("SELECT value FROM settings WHERE key='dedupe_enabled'")).fetchone()
    if not row or row[0] != "true":
        return
    h = _content_hash(body)
    existing = db.query(Snippet).filter(Snippet.content_hash == h, Snippet.archived == 0).first()
    if existing:
        raise DuplicateContent(
            f"Duplicate content detected (matches snippet '{existing.title}'). "
            "Disable dedup in settings to allow duplicates."
        )


# ── CRUD ────────────────────────────────────────────────────────────────
def create_snippet(db: Session, data: dict) -> Snippet:
    body = data["body"]
    _check_snippet_limit(db)
    _check_dedupe(db, body)
    title = data.get("title") or _infer_title(body)
    language = data.get("language") or _infer_language(body)
    now = _now_ms()
    snippet = Snippet(
        id=str(uuid.uuid4()),
        title=title,
        body=body,
        language=language,
        source=data.get("source"),
        source_url=data.get("source_url"),
        pinned=1 if data.get("pinned") else 0,
        archived=0,
        content_hash=_content_hash(body),
        created_at=now,
        updated_at=now,
    )
    db.add(snippet)
    db.flush()

    # Resolve tags/collections by name (upsert)
    if data.get("tags"):
        snippet.tags = _resolve_tags(db, data["tags"])
    if data.get("collections"):
        snippet.collections = _resolve_collections(db, data["collections"])

    db.flush()
    rebuild_fts_for_snippet(db, snippet.id)
    db.commit()
    db.refresh(snippet)
    return snippet


def get_snippet(db: Session, snippet_id: str) -> Optional[Snippet]:
    return db.query(Snippet).filter(Snippet.id == snippet_id).first()


def list_snippets(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    tag_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    pinned: Optional[bool] = None,
    archived: Optional[bool] = None,
    sort: str = "newest",
) -> tuple[list[Snippet], int]:
    q = db.query(Snippet)

    # Default: exclude archived
    if archived is None:
        q = q.filter(Snippet.archived == 0)
    elif archived is True:
        q = q.filter(Snippet.archived == 1)
    else:
        q = q.filter(Snippet.archived == 0)

    if pinned is not None:
        q = q.filter(Snippet.pinned == (1 if pinned else 0))

    if tag_id:
        q = q.filter(Snippet.tags.any(Tag.id == tag_id))

    if collection_id:
        q = q.filter(Snippet.collections.any(Collection.id == collection_id))

    total = q.count()

    if sort == "pinned":
        q = q.order_by(Snippet.pinned.desc(), Snippet.updated_at.desc())
    else:  # newest
        q = q.order_by(Snippet.created_at.desc())

    items = q.offset(offset).limit(limit).all()
    return items, total


def update_snippet(db: Session, snippet_id: str, data: dict) -> Optional[Snippet]:
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        return None

    if "title" in data and data["title"] is not None:
        snippet.title = data["title"]
    if "body" in data and data["body"] is not None:
        snippet.body = data["body"]
        snippet.content_hash = _content_hash(data["body"])
    if "language" in data and data["language"] is not None:
        snippet.language = data["language"]
    if "source" in data and data["source"] is not None:
        snippet.source = data["source"]
    if "source_url" in data and data["source_url"] is not None:
        snippet.source_url = data["source_url"]
    if "pinned" in data and data["pinned"] is not None:
        snippet.pinned = 1 if data["pinned"] else 0
    if "archived" in data and data["archived"] is not None:
        snippet.archived = 1 if data["archived"] else 0

    snippet.updated_at = _now_ms()

    if "tags" in data and data["tags"] is not None:
        snippet.tags = _resolve_tags(db, data["tags"])
    if "collections" in data and data["collections"] is not None:
        snippet.collections = _resolve_collections(db, data["collections"])

    db.flush()
    rebuild_fts_for_snippet(db, snippet.id)
    db.commit()
    db.refresh(snippet)
    return snippet


def delete_snippet(db: Session, snippet_id: str) -> bool:
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        return False
    # Hard delete (spec says DELETE => { ok: true })
    db.execute(text("DELETE FROM snippets_fts WHERE snippet_id=:sid"), {"sid": snippet_id})
    db.delete(snippet)
    db.commit()
    return True


def pin_snippet(db: Session, snippet_id: str) -> Optional[Snippet]:
    return update_snippet(db, snippet_id, {"pinned": True})


def unpin_snippet(db: Session, snippet_id: str) -> Optional[Snippet]:
    return update_snippet(db, snippet_id, {"pinned": False})


def archive_snippet(db: Session, snippet_id: str) -> Optional[Snippet]:
    return update_snippet(db, snippet_id, {"archived": True})


def unarchive_snippet(db: Session, snippet_id: str) -> Optional[Snippet]:
    return update_snippet(db, snippet_id, {"archived": False})


# ── Serialization helper ───────────────────────────────────────────────
def snippet_to_dict(s: Snippet) -> dict:
    """Convert Snippet ORM to SnippetOut dict."""
    return {
        "id": s.id,
        "title": s.title,
        "body": s.body,
        "language": s.language,
        "source": s.source,
        "source_url": s.source_url,
        "tags": [{"id": t.id, "name": t.name, "color": t.color, "created_at": t.created_at} for t in (s.tags or [])],
        "collections": [{"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at} for c in (s.collections or [])],
        "pinned": s.pinned,
        "archived": s.archived,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
    }
