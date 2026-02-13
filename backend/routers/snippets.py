import re
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from ..database import get_db
from ..models import SnippetIn, SnippetOut

logger = logging.getLogger(__name__)
router = APIRouter()

# Characters with special meaning in FTS5 query syntax
_FTS5_SPECIAL = re.compile(r'["\*\(\)\-\+\^:]')


def _sanitize_fts_query(raw: str) -> str:
    """Escape FTS5 special characters to prevent query injection.

    Wraps each whitespace-delimited token in double quotes so that
    special characters are treated as literals by the FTS5 MATCH engine.
    """
    tokens = raw.strip().split()
    if not tokens:
        return '""'
    # Quote each token individually; interior double quotes are doubled per FTS5 spec
    return " ".join(f'"{t.replace(chr(34), chr(34)+chr(34))}"' for t in tokens)


def _row_to_snippet(row, conn=None) -> SnippetOut:
    """Convert database row to SnippetOut model."""
    if row is None:
        return None

    tags = []
    collection_id = None
    if conn:
        try:
            tag_rows = conn.execute(
                "SELECT t.name FROM tags t JOIN snippet_tags st ON t.id = st.tag_id WHERE st.snippet_id = ?",
                (row["id"],),
            ).fetchall()
            tags = [t["name"] for t in tag_rows]
        except Exception as e:
            logger.warning(f"Failed to fetch tags for snippet {row['id']}: {e}")

        try:
            col_row = conn.execute(
                "SELECT collection_id FROM snippet_collections WHERE snippet_id = ? LIMIT 1",
                (row["id"],),
            ).fetchone()
            if col_row:
                collection_id = col_row["collection_id"]
        except Exception as e:
            logger.warning(f"Failed to fetch collection for snippet {row['id']}: {e}")

    return SnippetOut(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        language=row["language"],
        source=row["source"],
        created_at=datetime.fromisoformat(row["created_at"]),
        tags=tags,
        collection_id=collection_id,
    )


@router.get("/", response_model=list[SnippetOut], tags=["snippets"], summary="List snippets")
def list_snippets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    collection_id: int | None = Query(None),
):
    """List all snippets with pagination and optional collection filter."""
    with get_db() as conn:
        try:
            if collection_id:
                rows = conn.execute(
                    """SELECT s.* FROM snippets s JOIN snippet_collections sc ON s.id = sc.snippet_id
                       WHERE sc.collection_id = ? ORDER BY s.created_at DESC LIMIT ? OFFSET ?""",
                    (collection_id, limit, offset),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM snippets ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()

            return [_row_to_snippet(row, conn) for row in rows]
        except Exception as e:
            logger.error(f"Error listing snippets: {e}")
            raise HTTPException(status_code=500, detail="Failed to list snippets")


@router.post("/", response_model=SnippetOut, status_code=status.HTTP_201_CREATED, tags=["snippets"], summary="Create snippet")
def create_snippet(payload: SnippetIn):
    """Create a new snippet."""
    with get_db() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO snippets (title, body, language, source) VALUES (?, ?, ?, ?)",
                (payload.title, payload.body, payload.language, payload.source),
            )
            snippet_id = cur.lastrowid

            for tag_id in payload.tags:
                cur.execute(
                    "INSERT INTO snippet_tags (snippet_id, tag_id) VALUES (?, ?)",
                    (snippet_id, tag_id),
                )

            if payload.collection_id:
                cur.execute(
                    "INSERT INTO snippet_collections (snippet_id, collection_id) VALUES (?, ?)",
                    (snippet_id, payload.collection_id),
                )

            # No explicit conn.commit() — the get_db() context manager commits on success
            row = conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
            return _row_to_snippet(row, conn)
        except Exception as e:
            logger.error(f"Error creating snippet: {e}")
            raise HTTPException(status_code=500, detail="Failed to create snippet")


@router.get("/{snippet_id}", response_model=SnippetOut, tags=["snippets"], summary="Get snippet")
def get_snippet(snippet_id: int):
    """Get a specific snippet by ID."""
    with get_db() as conn:
        try:
            row = conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snippet not found")
            return _row_to_snippet(row, conn)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting snippet {snippet_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get snippet")


@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["snippets"], summary="Delete snippet")
def delete_snippet(snippet_id: int):
    """Delete a snippet by ID."""
    with get_db() as conn:
        try:
            existing = conn.execute("SELECT id FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snippet not found")
            conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting snippet {snippet_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete snippet")


@router.get("/search/query", response_model=list[SnippetOut], tags=["snippets"], summary="Search snippets")
def search_snippets(
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Full-text search snippets using FTS5."""
    with get_db() as conn:
        try:
            safe_query = _sanitize_fts_query(q)
            rows = conn.execute(
                """SELECT s.* FROM snippets_fts f JOIN snippets s ON s.id = f.rowid
                   WHERE snippets_fts MATCH ? ORDER BY rank LIMIT ? OFFSET ?""",
                (safe_query, limit, offset),
            ).fetchall()
            return [_row_to_snippet(row, conn) for row in rows]
        except Exception as e:
            logger.error(f"Error searching snippets: {e}")
            raise HTTPException(status_code=500, detail="Search failed")
