"""Backup service — WAL checkpoint + copy per backup-restore-spec.md."""

import json
import logging
import os
import shutil
import time
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings

logger = logging.getLogger(__name__)


def run_backup(db: Session) -> dict:
    """Run a manual backup: checkpoint WAL, copy DB file."""
    backup_dir = settings.get_backup_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    dest_dir = os.path.join(backup_dir, timestamp)
    os.makedirs(dest_dir, exist_ok=True)

    db_path = settings.get_database_path()

    # Checkpoint WAL
    try:
        db.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
    except Exception as e:
        logger.warning("WAL checkpoint warning: %s", e)

    # Copy DB
    dest_db = os.path.join(dest_dir, "pinup.db")
    shutil.copy2(db_path, dest_db)

    db_size = os.path.getsize(dest_db)

    # Write metadata
    meta = {
        "created_at": int(time.time() * 1000),
        "db_size_bytes": db_size,
        "app_version": settings.app_version,
    }
    meta_path = os.path.join(dest_dir, "backup.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info("Backup created: %s", dest_dir)
    return {
        "name": timestamp,
        "created_at": meta["created_at"],
        "db_size_bytes": db_size,
        "app_version": settings.app_version,
    }


def list_backups() -> list[dict]:
    """List existing backups."""
    backup_dir = settings.get_backup_dir()
    if not os.path.isdir(backup_dir):
        return []

    results = []
    for name in sorted(os.listdir(backup_dir), reverse=True):
        meta_path = os.path.join(backup_dir, name, "backup.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                results.append({
                    "name": name,
                    "created_at": meta.get("created_at", 0),
                    "db_size_bytes": meta.get("db_size_bytes", 0),
                    "app_version": meta.get("app_version", "unknown"),
                })
            except Exception:
                pass
    return results


def restore_backup(name: str) -> bool:
    """Restore from a named backup.

    WARNING: This replaces the current DB. Caller must restart the backend.
    """
    backup_dir = settings.get_backup_dir()
    src_db = os.path.join(backup_dir, name, "pinup.db")
    if not os.path.isfile(src_db):
        return False

    db_path = settings.get_database_path()

    # Safety: back up current DB before overwriting
    tmp_backup = db_path + ".pre_restore"
    if os.path.isfile(db_path):
        shutil.copy2(db_path, tmp_backup)

    try:
        shutil.copy2(src_db, db_path)
        # Remove WAL/SHM files to force clean start
        for ext in ["-wal", "-shm"]:
            p = db_path + ext
            if os.path.isfile(p):
                os.remove(p)
        logger.info("Restored from backup: %s", name)
        return True
    except Exception as e:
        logger.error("Restore failed: %s — reverting", e)
        if os.path.isfile(tmp_backup):
            shutil.copy2(tmp_backup, db_path)
        return False
