from pydantic import BaseModel, Field


class SnippetIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    language: str | None = None
    source: str | None = None


class SnippetOut(SnippetIn):
    id: int
    created_at: str


class TagIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class TagOut(TagIn):
    id: int


class CollectionIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CollectionOut(CollectionIn):
    id: int
