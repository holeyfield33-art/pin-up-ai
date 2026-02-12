from fastapi import APIRouter, HTTPException, Query

from ..database import get_connection
from ..models import CollectionIn, CollectionOut

router = APIRouter()


def _row_to_collection(row) -> CollectionOut:
    return CollectionOut(id=row["id"], name=row["name"])


@router.get("/", response_model=list[CollectionOut])
def list_collections(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM collections ORDER BY name ASC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [_row_to_collection(row) for row in cur.fetchall()]
    finally:
        conn.close()


@router.post("/", response_model=CollectionOut, status_code=201)
def create_collection(payload: CollectionIn):
    conn = get_connection()
    try:
        try:
            cur = conn.execute("INSERT INTO collections (name) VALUES (?)", (payload.name,))
            conn.commit()
        except Exception:
            raise HTTPException(status_code=409, detail="Collection already exists")
        row = conn.execute(
            "SELECT * FROM collections WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return _row_to_collection(row)
    finally:
        conn.close()
