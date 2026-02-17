"""List tags tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    __file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import tag_service


def list_tags() -> list[dict]:
    """List all tags with snippet counts."""
    init_db()
    db = SessionLocal()
    try:
        return tag_service.list_tags(db)
    finally:
        db.close()
