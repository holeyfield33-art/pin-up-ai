import logging
from fastapi import APIRouter, HTTPException, Query, status

from ..database import get_db
from ..models import CollectionIn, CollectionOut

logger = logging.getLogger(__name__)
router = APIRouter()


def _row_to_collection(row, conn=None) -> CollectionOut:
    """Convert database row to CollectionOut model."""
    count = 0
    if conn:
        try:
            result = conn.execute(
                "SELECT COUNT(*) as cnt FROM snippet_collections WHERE collection_id = ?",
                (row["id"],),
            ).fetchone()
            count = result["cnt"] if result else 0
        except Exception as e:
            logger.warning(f"Failed to get collection count: {e}")
    
    return CollectionOut(id=row["id"], name=row["name"], description=row.get("description"), count=count)


@router.get("/", response_model=list[CollectionOut], tags=["collections"], summary="List collections")
def list_collections(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    """List all collections with snippet count."""
    with get_db() as conn:
        try:
            rows = conn.execute(
                "SELECT * FROM collections ORDER BY name ASC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [_row_to_collection(row, conn) for row in rows]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise HTTPException(status_code=500, detail="Failed to list collections")


@router.post("/", response_model=CollectionOut, status_code=status.HTTP_201_CREATED, tags=["collections"], summary="Create collection")
def create_collection(payload: CollectionIn):
    """Create a new collection."""
    with get_db() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO collections (name, description) VALUES (?, ?)",
                (payload.name, payload.description),
            )
            row = conn.execute(
                "SELECT * FROM collections WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
            return _row_to_collection(row, conn)
        except Exception as e:
            if "UNIQUE" in str(e):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection already exists")
            logger.error(f"Error creating collection: {e}")
            raise HTTPException(status_code=500, detail="Failed to create collection")


@router.get("/{collection_id}", response_model=CollectionOut, tags=["collections"], summary="Get collection")
def get_collection(collection_id: int):
    """Get a collection by ID."""
    with get_db() as conn:
        try:
            row = conn.execute(
                "SELECT * FROM collections WHERE id = ?", (collection_id,)
            ).fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
            return _row_to_collection(row, conn)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting collection {collection_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get collection")


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["collections"], summary="Delete collection")
def delete_collection(collection_id: int):
    """Delete a collection by ID."""
    with get_db() as conn:
        try:
            existing = conn.execute(
                "SELECT id FROM collections WHERE id = ?", (collection_id,)
            ).fetchone()
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
            conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting collection {collection_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete collection")
