"""Database initialization and connection management."""

import logging
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

# Database URL
DATABASE_URL = settings.get_database_url()

# Create engine with SQLite-specific configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": settings.database_check_same_thread},
        poolclass=StaticPool,
        echo=settings.debug,
    )
else:
    engine = create_engine(DATABASE_URL, echo=settings.debug)

# Event listeners for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragmas(dbapi_conn, connection_record):
    """Set SQLite pragmas for performance and reliability."""
    if isinstance(dbapi_conn, sqlite3.Connection):
        cursor = dbapi_conn.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        # WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Optimize performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Enable FTS5
        cursor.execute("PRAGMA compile_options")
        cursor.close()
        logger.debug("SQLite pragmas configured")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database transactions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database with all tables and FTS5 index."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    # Create FTS5 virtual table if using SQLite
    with engine.connect() as conn:
        # Check if FTS5 extension is available
        try:
            conn.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(title, body)"))
            conn.commit()
            logger.info("FTS5 index created")
        except Exception as e:
            logger.warning(f"FTS5 setup: {e}")
    
    logger.info("Database initialization complete")


def drop_db():
    """Drop all tables (for testing)."""
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")
