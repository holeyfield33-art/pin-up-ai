"""Search router — FTS5 + DSL per search-spec.md."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import SearchResponse
from app.services import search_service as svc

router = APIRouter(prefix="/search", tags=["search"], dependencies=[Depends(verify_token)])


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("relevance", pattern="^(relevance|newest|pinned)$"),
    db: Session = Depends(get_db),
):
    results, total = svc.search(db, q=q, limit=limit, offset=offset, sort=sort)
    return {"results": results, "total": total}
