"""Tags router per api-contract.md — upsert by normalized name."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import TagCreate, TagPatch, TagListResponse
from app.services import tag_service as svc

router = APIRouter(prefix="/tags", tags=["tags"], dependencies=[Depends(verify_token)])


@router.get("", response_model=TagListResponse)
def list_tags(db: Session = Depends(get_db)):
    items = svc.list_tags(db)
    return {"items": items, "total": len(items)}


@router.post("", status_code=201)
def create_tag(body: TagCreate, db: Session = Depends(get_db)):
    tag = svc.create_tag(db, body.name, body.color)
    return {"id": tag.id, "name": tag.name, "color": tag.color, "created_at": tag.created_at}


@router.patch("/{tag_id}")
def update_tag(tag_id: str, body: TagPatch, db: Session = Depends(get_db)):
    tag = svc.update_tag(db, tag_id, name=body.name, color=body.color)
    if not tag:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Tag {tag_id} not found"})
    return {"id": tag.id, "name": tag.name, "color": tag.color, "created_at": tag.created_at}


@router.delete("/{tag_id}")
def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    ok = svc.delete_tag(db, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Tag {tag_id} not found"})
    return {"ok": True}
