"""List collections tool — thin wrapper for direct invocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    __file__))), "backend"))

from app.database import SessionLocal, init_db
from app.services import collection_service


def list_collections() -> list[dict]:
    """List all collections with snippet counts."""
    init_db()
    db = SessionLocal()
    try:
        return collection_service.list_collections(db)
    finally:
        db.close()
