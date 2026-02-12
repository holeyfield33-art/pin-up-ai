"""Full-text search endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchQuery, SnippetOut
from app.services import SnippetService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/query", response_model=dict)
async def search_snippets(
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search snippets by query using full-text search."""
    try:
        snippets, total = SnippetService.search_snippets(
            db, query=q, limit=limit, offset=offset
        )
        return {
            "query": q,
            "data": [SnippetOut.model_validate(s) for s in snippets],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error searching snippets: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/", response_model=dict)
async def search_snippets_post(
    search_query: SearchQuery,
    db: Session = Depends(get_db),
):
    """Search snippets via POST with SearchQuery model."""
    try:
        snippets, total = SnippetService.search_snippets(
            db,
            query=search_query.query,
            limit=search_query.limit,
            offset=search_query.offset,
        )
        return {
            "query": search_query.query,
            "data": [SnippetOut.model_validate(s) for s in snippets],
            "total": total,
            "limit": search_query.limit,
            "offset": search_query.offset,
        }
    except Exception as e:
        logger.error(f"Error searching snippets: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
