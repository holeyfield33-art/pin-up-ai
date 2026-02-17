"""Collections router per api-contract.md."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import CollectionCreate, CollectionPatch, CollectionListResponse
from app.services import collection_service as svc

router = APIRouter(prefix="/collections", tags=["collections"], dependencies=[Depends(verify_token)])


@router.get("", response_model=CollectionListResponse)
def list_collections(db: Session = Depends(get_db)):
    items = svc.list_collections(db)
    return {"items": items, "total": len(items)}


@router.post("", status_code=201)
def create_collection(body: CollectionCreate, db: Session = Depends(get_db)):
    col = svc.create_collection(db, body.name, body.description, body.icon, body.color)
    return {
        "id": col.id, "name": col.name, "description": col.description,
        "icon": col.icon, "color": col.color,
        "created_at": col.created_at, "updated_at": col.updated_at,
    }


@router.patch("/{collection_id}")
def update_collection(collection_id: str, body: CollectionPatch, db: Session = Depends(get_db)):
    col = svc.update_collection(
        db, collection_id,
        name=body.name, description=body.description,
        icon=body.icon, color=body.color,
    )
    if not col:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Collection {collection_id} not found"})
    return {
        "id": col.id, "name": col.name, "description": col.description,
        "icon": col.icon, "color": col.color,
        "created_at": col.created_at, "updated_at": col.updated_at,
    }


@router.delete("/{collection_id}")
def delete_collection(collection_id: str, db: Session = Depends(get_db)):
    ok = svc.delete_collection(db, collection_id)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Collection {collection_id} not found"})
    return {"ok": True}
