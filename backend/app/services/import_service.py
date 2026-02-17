"""Import service — import from JSON bundle per export-import-spec.md."""

import json
import logging
import uuid
from typing import Optional

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from app.models import Snippet, Tag, Collection, _now_ms
from app.database import rebuild_fts_for_snippet

logger = logging.getLogger(__name__)


def import_bundle(db: Session, data: dict) -> dict:
    """Import from the v1 JSON structure.

    Returns: {"ok": True, "imported": {...}, "merged": {...}}
    """
    version = data.get("version", "1")
    snippets_data = data.get("snippets", [])
    tags_data = data.get("tags", [])
    collections_data = data.get("collections", [])
    snippet_tags_data = data.get("snippet_tags", [])
    snippet_collections_data = data.get("snippet_collections", [])

    imported = {"snippets": 0, "tags": 0, "collections": 0}
    merged = {"tags": 0, "collections": 0}

    # Build ID remap tables
    tag_remap: dict[str, str] = {}  # old_id → new_id
    col_remap: dict[str, str] = {}
    snippet_remap: dict[str, str] = {}

    # ── Tags ────────────────────────────────────────────────────────────
    for td in tags_data:
        old_id = td["id"]
        name = td.get("name", "").strip().lower()
        existing = db.query(Tag).filter(func.lower(Tag.name) == name).first()
        if existing:
            tag_remap[old_id] = existing.id
            merged["tags"] += 1
        else:
            new_id = str(uuid.uuid4())
            tag = Tag(
                id=new_id,
                name=name,
                color=td.get("color"),
                created_at=td.get("created_at", _now_ms()),
            )
            db.add(tag)
            tag_remap[old_id] = new_id
            imported["tags"] += 1

    db.flush()

    # ── Collections ─────────────────────────────────────────────────────
    for cd in collections_data:
        old_id = cd["id"]
        name = cd.get("name", "").strip()
        existing = db.query(Collection).filter(func.lower(Collection.name) == func.lower(name)).first()
        if existing:
            col_remap[old_id] = existing.id
            merged["collections"] += 1
        else:
            new_id = str(uuid.uuid4())
            col = Collection(
                id=new_id,
                name=name,
                description=cd.get("description"),
                created_at=cd.get("created_at", _now_ms()),
            )
            db.add(col)
            col_remap[old_id] = new_id
            imported["collections"] += 1

    db.flush()

    # ── Snippets ────────────────────────────────────────────────────────
    for sd in snippets_data:
        old_id = sd["id"]
        # Check conflict
        existing = db.query(Snippet).filter(Snippet.id == old_id).first()
        if existing:
            new_id = str(uuid.uuid4())
            snippet_remap[old_id] = new_id
        else:
            new_id = old_id
            snippet_remap[old_id] = old_id

        s = Snippet(
            id=new_id,
            title=sd.get("title", "Untitled"),
            body=sd.get("body", ""),
            language=sd.get("language"),
            source=sd.get("source"),
            source_url=sd.get("source_url"),
            pinned=sd.get("pinned", 0),
            archived=sd.get("archived", 0),
            content_hash=sd.get("content_hash"),
            created_at=sd.get("created_at", _now_ms()),
            updated_at=sd.get("updated_at", _now_ms()),
        )
        db.add(s)
        imported["snippets"] += 1

    db.flush()

    # ── Joins ───────────────────────────────────────────────────────────
    for st in snippet_tags_data:
        sid = snippet_remap.get(st["snippet_id"], st["snippet_id"])
        tid = tag_remap.get(st["tag_id"], st["tag_id"])
        try:
            db.execute(
                text("INSERT OR IGNORE INTO snippet_tags(snippet_id, tag_id) VALUES(:sid, :tid)"),
                {"sid": sid, "tid": tid},
            )
        except Exception:
            pass

    for sc in snippet_collections_data:
        sid = snippet_remap.get(sc["snippet_id"], sc["snippet_id"])
        cid = col_remap.get(sc["collection_id"], sc["collection_id"])
        try:
            db.execute(
                text("INSERT OR IGNORE INTO snippet_collections(snippet_id, collection_id) VALUES(:sid, :cid)"),
                {"sid": sid, "cid": cid},
            )
        except Exception:
            pass

    db.flush()

    # Rebuild FTS for imported snippets
    for old_id in snippet_remap:
        new_id = snippet_remap[old_id]
        rebuild_fts_for_snippet(db, new_id)

    db.commit()

    return {"ok": True, "imported": imported, "merged": merged}
