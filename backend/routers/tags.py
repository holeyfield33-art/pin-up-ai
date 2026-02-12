from fastapi import APIRouter, HTTPException, Query

from ..database import get_connection
from ..models import TagIn, TagOut

router = APIRouter()


def _row_to_tag(row) -> TagOut:
    return TagOut(id=row["id"], name=row["name"])


@router.get("/", response_model=list[TagOut])
def list_tags(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM tags ORDER BY name ASC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [_row_to_tag(row) for row in cur.fetchall()]
    finally:
        conn.close()


@router.post("/", response_model=TagOut, status_code=201)
def create_tag(payload: TagIn):
    conn = get_connection()
    try:
        try:
            cur = conn.execute("INSERT INTO tags (name) VALUES (?)", (payload.name,))
            conn.commit()
        except Exception:
            raise HTTPException(status_code=409, detail="Tag already exists")
        row = conn.execute("SELECT * FROM tags WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row_to_tag(row)
    finally:
        conn.close()
