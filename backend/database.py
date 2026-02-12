import os
import sqlite3
from pathlib import Path
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("PINUP_DB", "./pinup.db")).resolve()


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                language TEXT,
                source TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snippet_tags (
                snippet_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (snippet_id, tag_id),
                FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snippet_collections (
                snippet_id INTEGER NOT NULL,
                collection_id INTEGER NOT NULL,
                PRIMARY KEY (snippet_id, collection_id),
                FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts
            USING fts5(title, body, content='snippets', content_rowid='id')
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS snippets_ai AFTER INSERT ON snippets
            BEGIN
                INSERT INTO snippets_fts(rowid, title, body)
                VALUES (new.id, new.title, new.body);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS snippets_ad AFTER DELETE ON snippets
            BEGIN
                INSERT INTO snippets_fts(snippets_fts, rowid, title, body)
                VALUES ('delete', old.id, old.title, old.body);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS snippets_au AFTER UPDATE ON snippets
            BEGIN
                INSERT INTO snippets_fts(snippets_fts, rowid, title, body)
                VALUES ('delete', old.id, old.title, old.body);
                INSERT INTO snippets_fts(rowid, title, body)
                VALUES (new.id, new.title, new.body);
            END
            """
        )
        conn.commit()
    finally:
        conn.close()
