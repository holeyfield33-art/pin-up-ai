"""Create snippet tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    __file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import snippet_service


def create_snippet(
    body: str,
    title: str | None = None,
    language: str | None = None,
    source: str = "mcp",
    tags: list[str] | None = None,
    collections: list[str] | None = None,
) -> dict:
    """Create a new snippet in the user's library."""
    init_db()
    db = SessionLocal()
    try:
        data = {
            "body": body,
            "title": title,
            "language": language,
            "source": source,
            "tags": tags or [],
            "collections": collections or [],
        }
        s = snippet_service.create_snippet(db, data)
        return {"id": s.id, "title": s.title, "created_at": s.created_at}
    finally:
        db.close()
