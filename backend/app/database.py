"""Database initialization and connection management."""

import logging
import sqlite3
import time
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = settings.get_database_url()

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": settings.database_check_same_thread},
        poolclass=StaticPool,
        echo=settings.debug,
    )
else:
    engine = create_engine(DATABASE_URL, echo=settings.debug)

_start_time = time.time()


def get_uptime_ms() -> int:
    return int((time.time() - _start_time) * 1000)


@event.listens_for(engine, "connect")
def set_sqlite_pragmas(dbapi_conn, connection_record):
    if isinstance(dbapi_conn, sqlite3.Connection):
        c = dbapi_conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("PRAGMA journal_mode = WAL")
        c.execute("PRAGMA synchronous = NORMAL")
        c.execute("PRAGMA temp_store = MEMORY")
        c.execute("PRAGMA busy_timeout = 5000")
        c.execute("PRAGMA cache_size = 10000")
        c.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _ensure_settings_table(conn):
    conn.exec_driver_sql(
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )


def _ensure_fts(conn):
    conn.exec_driver_sql(
        'CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5('
        'snippet_id UNINDEXED, title, body, tags, collections, source, language, '
        "tokenize='unicode61')"
    )
    # Triggers
    conn.exec_driver_sql(
        "CREATE TRIGGER IF NOT EXISTS snippets_ai "
        "AFTER INSERT ON snippets BEGIN "
        "INSERT INTO snippets_fts(snippet_id,title,body,tags,collections,source,language) "
        "VALUES(new.id,new.title,new.body,'','',new.source,new.language); "
        "END;"
    )
    conn.exec_driver_sql(
        "CREATE TRIGGER IF NOT EXISTS snippets_au "
        "AFTER UPDATE ON snippets BEGIN "
        "DELETE FROM snippets_fts WHERE snippet_id=old.id; "
        "INSERT INTO snippets_fts(snippet_id,title,body,tags,collections,source,language) "
        "VALUES(new.id,new.title,new.body,'','',new.source,new.language); "
        "END;"
    )
    conn.exec_driver_sql(
        "CREATE TRIGGER IF NOT EXISTS snippets_ad "
        "AFTER DELETE ON snippets BEGIN "
        "DELETE FROM snippets_fts WHERE snippet_id=old.id; "
        "END;"
    )


def init_db():
    logger.info("Initializing database...")
    import importlib
    if not Base.metadata.tables:
        models = importlib.import_module("app.models")
        if not Base.metadata.tables:
            importlib.reload(models)
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        _ensure_settings_table(conn)
        _ensure_fts(conn)
        # Rebuild FTS
        conn.exec_driver_sql("DELETE FROM snippets_fts")
        conn.exec_driver_sql(
            "INSERT INTO snippets_fts(snippet_id,title,body,tags,collections,source,language) "
            "SELECT s.id, s.title, s.body, "
            "COALESCE((SELECT GROUP_CONCAT(t.name,' ') FROM snippet_tags st JOIN tags t ON t.id=st.tag_id WHERE st.snippet_id=s.id),''), "
            "COALESCE((SELECT GROUP_CONCAT(c.name,' ') FROM snippet_collections sc JOIN collections c ON c.id=sc.collection_id WHERE sc.snippet_id=s.id),''), "
            "COALESCE(s.source,''), COALESCE(s.language,'') "
            "FROM snippets s"
        )
    logger.info("Database initialization complete")


def rebuild_fts_for_snippet(db: Session, snippet_id: str):
    """Rebuild FTS row for a single snippet with current tag/collection names."""
    db.execute(text("DELETE FROM snippets_fts WHERE snippet_id=:sid"), {"sid": snippet_id})
    db.execute(text(
        "INSERT INTO snippets_fts(snippet_id,title,body,tags,collections,source,language) "
        "SELECT s.id, s.title, s.body, "
        "COALESCE((SELECT GROUP_CONCAT(t.name,' ') FROM snippet_tags st JOIN tags t ON t.id=st.tag_id WHERE st.snippet_id=s.id),''), "
        "COALESCE((SELECT GROUP_CONCAT(c.name,' ') FROM snippet_collections sc JOIN collections c ON c.id=sc.collection_id WHERE sc.snippet_id=s.id),''), "
        "COALESCE(s.source,''), COALESCE(s.language,'') "
        "FROM snippets s WHERE s.id=:sid"
    ), {"sid": snippet_id})


def drop_db():
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
