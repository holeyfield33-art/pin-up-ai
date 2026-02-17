"""List snippets tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    __file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import snippet_service


def list_snippets(limit: int = 20, offset: int = 0, tag_id: str | None = None) -> dict:
    """List snippets with optional pagination and tag filter."""
    init_db()
    db = SessionLocal()
    try:
        items, total = snippet_service.list_snippets(db, limit=limit, offset=offset, tag_id=tag_id)
        return {
            "snippets": [snippet_service.snippet_to_dict(s) for s in items],
            "total": total,
        }
    finally:
        db.close()
