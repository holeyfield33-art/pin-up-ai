import logging
from fastapi import APIRouter, HTTPException, Query, status

from ..database import get_db
from ..models import TagIn, TagOut

logger = logging.getLogger(__name__)
router = APIRouter()


def _row_to_tag(row, conn=None) -> TagOut:
    """Convert database row to TagOut model."""
    count = 0
    if conn:
        try:
            result = conn.execute(
                "SELECT COUNT(*) as cnt FROM snippet_tags WHERE tag_id = ?",
                (row["id"],),
            ).fetchone()
            count = result["cnt"] if result else 0
        except Exception as e:
            logger.warning(f"Failed to get tag count: {e}")
    
    return TagOut(id=row["id"], name=row["name"], count=count)


@router.get("/", response_model=list[TagOut], tags=["tags"], summary="List tags")
def list_tags(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    """List all tags with usage count."""
    with get_db() as conn:
        try:
            rows = conn.execute(
                "SELECT * FROM tags ORDER BY name ASC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [_row_to_tag(row, conn) for row in rows]
        except Exception as e:
            logger.error(f"Error listing tags: {e}")
            raise HTTPException(status_code=500, detail="Failed to list tags")


@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED, tags=["tags"], summary="Create tag")
def create_tag(payload: TagIn):
    """Create a new tag."""
    with get_db() as conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO tags (name) VALUES (?)", (payload.name,))
            row = conn.execute("SELECT * FROM tags WHERE id = ?", (cur.lastrowid,)).fetchone()
            return _row_to_tag(row, conn)
        except Exception as e:
            if "UNIQUE" in str(e):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
            logger.error(f"Error creating tag: {e}")
            raise HTTPException(status_code=500, detail="Failed to create tag")


@router.get("/{tag_id}", response_model=TagOut, tags=["tags"], summary="Get tag")
def get_tag(tag_id: int):
    """Get a tag  by ID."""
    with get_db() as conn:
        try:
            row = conn.execute("SELECT * FROM tags WHERE id = ?", (tag_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
            return _row_to_tag(row, conn)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tag {tag_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get tag")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tags"], summary="Delete tag")
def delete_tag(tag_id: int):
    """Delete a tag by ID."""
    with get_db() as conn:
        try:
            existing = conn.execute("SELECT id FROM tags WHERE id = ?", (tag_id,)).fetchone()
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
            conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting tag {tag_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete tag")
