"""SQLAlchemy ORM models for database entities."""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


# Association tables for many-to-many relationships
snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", String(36), ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

snippet_collections = Table(
    "snippet_collections",
    Base.metadata,
    Column("snippet_id", String(36), ForeignKey("snippets.id", ondelete="CASCADE"), primary_key=True),
    Column("collection_id", String(36), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
)


class Snippet(Base):
    """Code snippet model."""

    __tablename__ = "snippets"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    body = Column(Text, nullable=False)
    language = Column(String(50), nullable=True, default="plaintext")
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False, index=True)

    # Relationships
    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets")
    collections = relationship("Collection", secondary=snippet_collections, back_populates="snippets")

    def __repr__(self):
        return f"<Snippet(id={self.id}, title={self.title})>"


class Tag(Base):
    """Tag model for organizing snippets."""

    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True, default="#6366F1")  # Hex color
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class Collection(Base):
    """Collection model for grouping snippets."""

    __tablename__ = "collections"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True, default="#3B82F6")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    snippets = relationship("Collection", secondary=snippet_collections, back_populates="collections")

    def __repr__(self):
        return f"<Collection(id={self.id}, name={self.name})>"
