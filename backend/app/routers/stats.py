"""Stats router per dashboard-spec.md."""

import os
import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.config import settings as app_settings

router = APIRouter(tags=["stats"], dependencies=[Depends(verify_token)])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Return dashboard stats per dashboard-spec.md."""
    now_ms = int(time.time() * 1000)
    seven_days_ago = now_ms - 7 * 24 * 60 * 60 * 1000
    thirty_days_ago = now_ms - 30 * 24 * 60 * 60 * 1000

    # Totals
    total_snippets = db.execute(text("SELECT COUNT(*) FROM snippets")).scalar() or 0
    total_tags = db.execute(text("SELECT COUNT(*) FROM tags")).scalar() or 0
    total_collections = db.execute(text("SELECT COUNT(*) FROM collections")).scalar() or 0
    total_pinned = db.execute(text("SELECT COUNT(*) FROM snippets WHERE pinned=1")).scalar() or 0
    total_archived = db.execute(text("SELECT COUNT(*) FROM snippets WHERE archived=1")).scalar() or 0

    # Top tags
    top_tags_rows = db.execute(text(
        "SELECT t.id, t.name, COUNT(st.snippet_id) as cnt "
        "FROM tags t LEFT JOIN snippet_tags st ON st.tag_id=t.id "
        "GROUP BY t.id ORDER BY cnt DESC LIMIT 10"
    )).fetchall()
    top_tags = [{"id": r[0], "name": r[1], "count": r[2]} for r in top_tags_rows]

    # Top collections
    top_cols_rows = db.execute(text(
        "SELECT c.id, c.name, COUNT(sc.snippet_id) as cnt "
        "FROM collections c LEFT JOIN snippet_collections sc ON sc.collection_id=c.id "
        "GROUP BY c.id ORDER BY cnt DESC LIMIT 10"
    )).fetchall()
    top_collections = [{"id": r[0], "name": r[1], "count": r[2]} for r in top_cols_rows]

    # Created counts
    last_7 = db.execute(text("SELECT COUNT(*) FROM snippets WHERE created_at >= :ts"), {"ts": seven_days_ago}).scalar() or 0
    last_30 = db.execute(text("SELECT COUNT(*) FROM snippets WHERE created_at >= :ts"), {"ts": thirty_days_ago}).scalar() or 0

    # Recent activity
    recent_rows = db.execute(text(
        "SELECT id, title, updated_at FROM snippets ORDER BY updated_at DESC LIMIT 10"
    )).fetchall()
    recent_activity = [{"id": r[0], "title": r[1], "updated_at": r[2]} for r in recent_rows]

    # Vault health
    db_path = app_settings.get_database_path()
    db_size = os.path.getsize(db_path) if os.path.isfile(db_path) else 0

    # Last backup
    backup_dir = app_settings.get_backup_dir()
    last_backup_at = 0
    backup_enabled = False
    if os.path.isdir(backup_dir):
        for name in sorted(os.listdir(backup_dir), reverse=True):
            meta_path = os.path.join(backup_dir, name, "backup.json")
            if os.path.isfile(meta_path):
                import json
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    last_backup_at = meta.get("created_at", 0)
                    backup_enabled = True
                    break
                except Exception:
                    pass

    return {
        "totals": {
            "snippets": total_snippets,
            "tags": total_tags,
            "collections": total_collections,
            "pinned": total_pinned,
            "archived": total_archived,
        },
        "top_tags": top_tags,
        "top_collections": top_collections,
        "created_counts": {
            "last_7_days": last_7,
            "last_30_days": last_30,
        },
        "recent_activity": recent_activity,
        "vault": {
            "db_size_bytes": db_size,
            "last_backup_at": last_backup_at,
            "backup_enabled": backup_enabled,
        },
    }
