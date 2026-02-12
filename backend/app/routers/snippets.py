"""Snippets CRUD endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SnippetCreate, SnippetUpdate, SnippetOut
from app.services import SnippetService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/snippets", tags=["snippets"])


@router.get("", response_model=dict)
async def list_snippets(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    collection_id: str = Query(None),
    tag_id: str = Query(None),
    db: Session = Depends(get_db),
):
    """List all snippets with pagination."""
    try:
        snippets, total = SnippetService.list_snippets(
            db, limit=limit, offset=offset, collection_id=collection_id, tag_id=tag_id
        )
        return {
            "data": [SnippetOut.model_validate(s) for s in snippets],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing snippets: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch snippets")


@router.post("", response_model=SnippetOut, status_code=201)
async def create_snippet(
    snippet_create: SnippetCreate,
    db: Session = Depends(get_db),
):
    """Create a new snippet."""
    try:
        snippet = SnippetService.create_snippet(db, snippet_create)
        return SnippetOut.model_validate(snippet)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating snippet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create snippet")


@router.get("/{snippet_id}", response_model=SnippetOut)
async def get_snippet(snippet_id: str, db: Session = Depends(get_db)):
    """Get a snippet by ID."""
    snippet = SnippetService.get_snippet(db, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return SnippetOut.model_validate(snippet)


@router.put("/{snippet_id}", response_model=SnippetOut)
async def update_snippet(
    snippet_id: str,
    update: SnippetUpdate,
    db: Session = Depends(get_db),
):
    """Update a snippet."""
    try:
        snippet = SnippetService.update_snippet(db, snippet_id, update)
        if not snippet:
            raise HTTPException(status_code=404, detail="Snippet not found")
        return SnippetOut.model_validate(snippet)
    except Exception as e:
        logger.error(f"Error updating snippet: {e}")
        raise HTTPException(status_code=500, detail="Failed to update snippet")


@router.delete("/{snippet_id}", status_code=204)
async def delete_snippet(snippet_id: str, db: Session = Depends(get_db)):
    """Delete a snippet."""
    success = SnippetService.delete_snippet(db, snippet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return None


@router.get("/export/{format}", response_model=dict)
async def export_snippets(
    format: str,
    db: Session = Depends(get_db),
):
    """Export all snippets in specified format."""
    if format not in ["json", "markdown"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'markdown'")
    
    try:
        content = SnippetService.export_snippets(db, format=format)
        return {
            "format": format,
            "size": len(content),
            "content": content,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting snippets: {e}")
        raise HTTPException(status_code=500, detail="Failed to export snippets")
