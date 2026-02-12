"""Pydantic v2 schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import html


class TagBase(BaseModel):
    """Base tag schema."""

    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default="#6366F1", pattern="^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v):
        """Sanitize tag name."""
        return html.escape(v.strip())


class TagCreate(TagBase):
    """Tag creation schema."""

    pass


class TagOut(TagBase):
    """Tag output schema."""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CollectionBase(BaseModel):
    """Base collection schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default="#3B82F6", pattern="^#[0-9A-Fa-f]{6}$")

    @field_validator("name", "description")
    @classmethod
    def sanitize_text(cls, v):
        """Sanitize text fields."""
        if v is None:
            return v
        return html.escape(v.strip())


class CollectionCreate(CollectionBase):
    """Collection creation schema."""

    pass


class CollectionOut(CollectionBase):
    """Collection output schema."""

    id: str
    created_at: datetime
    updated_at: datetime
    snippet_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SnippetBase(BaseModel):
    """Base snippet schema."""

    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    language: str = Field(default="plaintext", max_length=50)
    source: Optional[str] = Field(default=None, max_length=255)

    @field_validator("title", "language", "source")
    @classmethod
    def sanitize_fields(cls, v):
        """Sanitize string fields."""
        if v is None:
            return v
        return html.escape(v.strip())

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        """Validate body content."""
        if len(v) > 1_000_000:  # 1MB limit
            raise ValueError("Snippet body exceeds maximum size")
        return v


class SnippetCreate(SnippetBase):
    """Snippet creation schema."""

    tag_ids: list[str] = Field(default_factory=list)
    collection_ids: list[str] = Field(default_factory=list)


class SnippetUpdate(BaseModel):
    """Snippet update schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    body: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=255)
    tag_ids: Optional[list[str]] = None
    collection_ids: Optional[list[str]] = None

    @field_validator("title", "language", "source")
    @classmethod
    def sanitize_fields(cls, v):
        """Sanitize string fields."""
        if v is None:
            return v
        return html.escape(v.strip())


class SnippetOut(SnippetBase):
    """Snippet output schema."""

    id: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool = False
    tags: list[TagOut] = []
    collections: list[CollectionOut] = []

    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    """Full-text search query schema."""

    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v):
        """Sanitize search query."""
        return v.strip()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    database: str


class ExportResponse(BaseModel):
    """Export response."""

    format: str
    size: int
    content: str
