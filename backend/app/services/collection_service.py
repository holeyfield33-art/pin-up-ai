"""Collection service — CRUD with snippet counts."""

import logging
import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Collection, snippet_collections, _now_ms

logger = logging.getLogger(__name__)


def create_collection(
    db: Session,
    name: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> Collection:
    norm = name.strip()
    existing = db.query(Collection).filter(func.lower(Collection.name) == func.lower(norm)).first()
    if existing:
        changed = False
        if description is not None:
            existing.description = description
            changed = True
        if icon is not None:
            existing.icon = icon
            changed = True
        if color is not None:
            existing.color = color
            changed = True
        if changed:
            existing.updated_at = _now_ms()
            db.commit()
            db.refresh(existing)
        return existing
    now = _now_ms()
    col = Collection(
        id=str(uuid.uuid4()),
        name=norm,
        description=description,
        icon=icon or "📁",
        color=color or "#7C5CFC",
        created_at=now,
        updated_at=now,
    )
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


def get_collection(db: Session, collection_id: str) -> Optional[Collection]:
    return db.query(Collection).filter(Collection.id == collection_id).first()


def list_collections(db: Session) -> list[dict]:
    rows = (
        db.query(
            Collection.id, Collection.name, Collection.description,
            Collection.icon, Collection.color,
            Collection.created_at, Collection.updated_at,
            func.count(snippet_collections.c.snippet_id).label("count"),
        )
        .outerjoin(snippet_collections, snippet_collections.c.collection_id == Collection.id)
        .group_by(Collection.id)
        .order_by(Collection.name)
        .all()
    )
    return [
        {
            "id": r[0], "name": r[1], "description": r[2],
            "icon": r[3], "color": r[4],
            "created_at": r[5], "updated_at": r[6], "count": r[7],
        }
        for r in rows
    ]


def update_collection(
    db: Session, collection_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> Optional[Collection]:
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        return None
    if name is not None:
        col.name = name.strip()
    if description is not None:
        col.description = description
    if icon is not None:
        col.icon = icon
    if color is not None:
        col.color = color
    col.updated_at = _now_ms()
    db.commit()
    db.refresh(col)
    return col


def delete_collection(db: Session, collection_id: str) -> bool:
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        return False
    db.delete(col)
    db.commit()
    return True
