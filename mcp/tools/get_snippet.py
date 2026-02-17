"""Get snippet tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    __file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import snippet_service


def get_snippet(snippet_id: str) -> dict | None:
    """Get a single snippet by ID with full content."""
    init_db()
    db = SessionLocal()
    try:
        s = snippet_service.get_snippet(db, snippet_id)
        if not s:
            return None
        return snippet_service.snippet_to_dict(s)
    finally:
        db.close()
