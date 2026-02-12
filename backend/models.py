from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SnippetIn(BaseModel):
    """Create or update a snippet."""
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=50000)
    language: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=500)
    tags: list[int] = Field(default_factory=list)
    collection_id: Optional[int] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Sanitize title."""
        return v.strip()

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: str) -> str:
        """Sanitize body."""
        return v.strip()


class SnippetOut(BaseModel):
    """Full snippet response."""
    id: int
    title: str
    body: str
    language: Optional[str]
    source: Optional[str]
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
    collection_id: Optional[int] = None

    class Config:
        from_attributes = True


class TagIn(BaseModel):
    """Create a tag."""
    name: str = Field(..., min_length=1, max_length=64)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Sanitize tag name."""
        return v.strip().lower()


class TagOut(BaseModel):
    """Tag response."""
    id: int
    name: str
    count: int = 0

    class Config:
        from_attributes = True


class CollectionIn(BaseModel):
    """Create a collection."""
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Sanitize collection name."""
        return v.strip()


class CollectionOut(BaseModel):
    """Collection response."""
    id: int
    name: str
    description: Optional[str]
    count: int = 0

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """Search parameters."""
    q: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
