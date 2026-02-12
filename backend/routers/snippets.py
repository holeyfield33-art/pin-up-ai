from fastapi import APIRouter, HTTPException, Query

from ..database import get_connection
from ..models import SnippetIn, SnippetOut

router = APIRouter()


def _row_to_snippet(row) -> SnippetOut:
    return SnippetOut(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        language=row["language"],
        source=row["source"],
        created_at=row["created_at"],
    )


@router.get("/", response_model=list[SnippetOut])
def list_snippets(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM snippets ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [_row_to_snippet(row) for row in cur.fetchall()]
    finally:
        conn.close()


@router.post("/", response_model=SnippetOut, status_code=201)
def create_snippet(payload: SnippetIn):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO snippets (title, body, language, source)
            VALUES (?, ?, ?, ?)
            """,
            (payload.title, payload.body, payload.language, payload.source),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM snippets WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_snippet(row)
    finally:
        conn.close()


@router.get("/{snippet_id}", response_model=SnippetOut)
def get_snippet(snippet_id: int):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Snippet not found")
        return _row_to_snippet(row)
    finally:
        conn.close()


@router.get("/search/", response_model=list[SnippetOut])
def search_snippets(q: str = Query(min_length=1), limit: int = Query(50, ge=1, le=200)):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT s.*
            FROM snippets_fts f
            JOIN snippets s ON s.id = f.rowid
            WHERE snippets_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (q, limit),
        )
        return [_row_to_snippet(row) for row in cur.fetchall()]
    finally:
        conn.close()
