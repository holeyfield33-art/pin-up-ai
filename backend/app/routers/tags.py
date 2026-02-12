"""Tags CRUD endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TagCreate, TagOut
from app.services import TagService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=dict)
async def list_tags(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all tags with snippet counts."""
    try:
        tags, total = TagService.list_tags(db, limit=limit, offset=offset)
        return {
            "data": tags,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tags")


@router.post("", response_model=TagOut, status_code=201)
async def create_tag(tag_create: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    try:
        tag = TagService.create_tag(db, name=tag_create.name, color=tag_create.color)
        return TagOut.model_validate(tag)
    except ValueError as e:
        logger.warning(f"Tag creation conflict: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tag")


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: str, db: Session = Depends(get_db)):
    """Get a tag by ID."""
    tag = TagService.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagOut.model_validate(tag)


@router.put("/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: str,
    name: str = Query(None),
    color: str = Query(None),
    db: Session = Depends(get_db),
):
    """Update a tag."""
    try:
        tag = TagService.update_tag(db, tag_id, name=name, color=color)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return TagOut.model_validate(tag)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating tag: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tag")


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    """Delete a tag."""
    success = TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
