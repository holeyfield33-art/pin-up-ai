"""Search snippets tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import search_service


def search_snippets(query: str, limit: int = 10) -> list[dict]:
    """Search snippets by query string using FTS5."""
    init_db()
    db = SessionLocal()
    try:
        results, total = search_service.search(db, q=query, limit=limit)
        return results
    finally:
        db.close()
