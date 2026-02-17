"""Tag service — CRUD with snippet counts."""

import logging
import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Tag, snippet_tags, _now_ms

logger = logging.getLogger(__name__)


def create_tag(db: Session, name: str, color: Optional[str] = None) -> Tag:
    """Upsert by normalized name."""
    norm = name.strip().lower()
    existing = db.query(Tag).filter(func.lower(Tag.name) == norm).first()
    if existing:
        if color:
            existing.color = color
            db.commit()
            db.refresh(existing)
        return existing
    tag = Tag(id=str(uuid.uuid4()), name=norm, color=color, created_at=_now_ms())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def get_tag(db: Session, tag_id: str) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def list_tags(db: Session) -> list[dict]:
    """Return tags with snippet counts."""
    rows = (
        db.query(
            Tag.id, Tag.name, Tag.color, Tag.created_at,
            func.count(snippet_tags.c.snippet_id).label("count"),
        )
        .outerjoin(snippet_tags, snippet_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(Tag.name)
        .all()
    )
    return [
        {"id": r[0], "name": r[1], "color": r[2], "created_at": r[3], "count": r[4]}
        for r in rows
    ]


def update_tag(db: Session, tag_id: str, name: Optional[str] = None, color: Optional[str] = None) -> Optional[Tag]:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None
    if name is not None:
        tag.name = name.strip().lower()
    if color is not None:
        tag.color = color
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: str) -> bool:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False
    db.delete(tag)
    db.commit()
    return True
