"""SQLAlchemy ORM models matching db-schema.sql.md spec."""

import hashlib
import time
import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Table, Index
from sqlalchemy.orm import relationship
from app.database import Base


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> str:
    return str(uuid.uuid4())


def _content_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


# ── join tables ─────────────────────────────────────────────────────────
snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", String, ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
Index("idx_snippet_tags_tag", snippet_tags.c.tag_id)

snippet_collections = Table(
    "snippet_collections",
    Base.metadata,
    Column("snippet_id", String, ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("collection_id", String, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
)
Index("idx_snippet_collections_collection", snippet_collections.c.collection_id)


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(String, primary_key=True, default=_new_id)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    language = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    pinned = Column(Integer, nullable=False, default=0)
    archived = Column(Integer, nullable=False, default=0)
    content_hash = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=_now_ms)
    updated_at = Column(Integer, nullable=False, default=_now_ms)

    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets", lazy="selectin")
    collections = relationship("Collection", secondary=snippet_collections, back_populates="snippets", lazy="selectin")


Index("idx_snippets_created_at", Snippet.created_at)
Index("idx_snippets_updated_at", Snippet.updated_at)
Index("idx_snippets_pinned", Snippet.pinned)
Index("idx_snippets_archived", Snippet.archived)
Index("idx_snippets_hash", Snippet.content_hash)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(Text, nullable=False, unique=True)
    color = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False, default=_now_ms)

    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags", lazy="selectin")


Index("idx_tags_name", Tag.name)


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(Text, nullable=True, default="📁")
    color = Column(Text, nullable=True, default="#7C5CFC")
    created_at = Column(Integer, nullable=False, default=_now_ms)
    updated_at = Column(Integer, nullable=False, default=_now_ms)

    snippets = relationship("Snippet", secondary=snippet_collections, back_populates="collections", lazy="selectin")


Index("idx_collections_name", Collection.name)
