"""Collections CRUD endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CollectionCreate, CollectionOut
from app.services import CollectionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("", response_model=dict)
async def list_collections(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all collections with snippet counts."""
    try:
        collections, total = CollectionService.list_collections(db, limit=limit, offset=offset)
        return {
            "data": collections,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collections")


@router.post("", response_model=CollectionOut, status_code=201)
async def create_collection(
    collection_create: CollectionCreate,
    db: Session = Depends(get_db),
):
    """Create a new collection."""
    try:
        collection = CollectionService.create_collection(
            db,
            name=collection_create.name,
            description=collection_create.description,
            icon=collection_create.icon,
            color=collection_create.color,
        )
        return CollectionOut.model_validate(collection)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to create collection")


@router.get("/{collection_id}", response_model=CollectionOut)
async def get_collection(collection_id: str, db: Session = Depends(get_db)):
    """Get a collection by ID."""
    collection = CollectionService.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return CollectionOut.model_validate(collection)


@router.put("/{collection_id}", response_model=CollectionOut)
async def update_collection(
    collection_id: str,
    name: str = Query(None),
    description: str = Query(None),
    icon: str = Query(None),
    color: str = Query(None),
    db: Session = Depends(get_db),
):
    """Update a collection."""
    try:
        collection = CollectionService.update_collection(
            db, collection_id, name=name, description=description, icon=icon, color=color
        )
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return CollectionOut.model_validate(collection)
    except Exception as e:
        logger.error(f"Error updating collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to update collection")


@router.delete("/{collection_id}", status_code=204)
async def delete_collection(collection_id: str, db: Session = Depends(get_db)):
    """Delete a collection."""
    success = CollectionService.delete_collection(db, collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Collection not found")
    return None
