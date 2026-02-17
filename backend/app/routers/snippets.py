"""Snippets router — full CRUD + pin/unpin/archive/unarchive per api-contract.md."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import SnippetCreate, SnippetPatch, SnippetOut, SnippetListResponse
from app.services import snippet_service as svc
from app.services.snippet_service import SnippetLimitReached, DuplicateContent

router = APIRouter(prefix="/snippets", tags=["snippets"], dependencies=[Depends(verify_token)])


@router.get("", response_model=SnippetListResponse)
def list_snippets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tag_id: str | None = None,
    collection_id: str | None = None,
    pinned: bool | None = None,
    archived: bool | None = None,
    sort: str = Query("newest", pattern="^(newest|pinned)$"),
    db: Session = Depends(get_db),
):
    items, total = svc.list_snippets(
        db, limit=limit, offset=offset, tag_id=tag_id,
        collection_id=collection_id, pinned=pinned, archived=archived, sort=sort,
    )
    return {"items": [svc.snippet_to_dict(s) for s in items], "total": total}


@router.post("", response_model=SnippetOut, status_code=201)
def create_snippet(body: SnippetCreate, db: Session = Depends(get_db)):
    try:
        s = svc.create_snippet(db, body.model_dump())
    except SnippetLimitReached as e:
        raise HTTPException(status_code=403, detail={"code": "SNIPPET_LIMIT_REACHED", "message": str(e)})
    except DuplicateContent as e:
        raise HTTPException(status_code=409, detail={"code": "DUPLICATE_CONTENT", "message": str(e)})
    return svc.snippet_to_dict(s)


@router.get("/{snippet_id}", response_model=SnippetOut)
def get_snippet(snippet_id: str, db: Session = Depends(get_db)):
    s = svc.get_snippet(db, snippet_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)


@router.patch("/{snippet_id}", response_model=SnippetOut)
def update_snippet(snippet_id: str, body: SnippetPatch, db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    s = svc.update_snippet(db, snippet_id, data)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)


@router.delete("/{snippet_id}")
def delete_snippet(snippet_id: str, db: Session = Depends(get_db)):
    ok = svc.delete_snippet(db, snippet_id)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return {"ok": True}


@router.post("/{snippet_id}/pin", response_model=SnippetOut)
def pin_snippet(snippet_id: str, db: Session = Depends(get_db)):
    s = svc.pin_snippet(db, snippet_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)


@router.post("/{snippet_id}/unpin", response_model=SnippetOut)
def unpin_snippet(snippet_id: str, db: Session = Depends(get_db)):
    s = svc.unpin_snippet(db, snippet_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)


@router.post("/{snippet_id}/archive", response_model=SnippetOut)
def archive_snippet(snippet_id: str, db: Session = Depends(get_db)):
    s = svc.archive_snippet(db, snippet_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)


@router.post("/{snippet_id}/unarchive", response_model=SnippetOut)
def unarchive_snippet(snippet_id: str, db: Session = Depends(get_db)):
    s = svc.unarchive_snippet(db, snippet_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Snippet {snippet_id} not found"})
    return svc.snippet_to_dict(s)
