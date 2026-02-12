"""Business logic for tag operations."""

import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.models import Tag, Snippet

logger = logging.getLogger(__name__)


class TagService:
    """Service for tag CRUD operations."""

    @staticmethod
    def create_tag(db: Session, name: str, color: str = "#6366F1") -> Tag:
        """Create a new tag."""
        tag_id = str(uuid.uuid4())

        try:
            tag = Tag(
                id=tag_id,
                name=name,
                color=color,
                created_at=datetime.utcnow(),
            )
            db.add(tag)
            db.commit()
            db.refresh(tag)
            logger.info(f"Created tag: {tag_id}")
            return tag
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Tag already exists: {name}")
            raise ValueError(f"Tag '{name}' already exists")

    @staticmethod
    def get_tag(db: Session, tag_id: str) -> Tag | None:
        """Get tag by ID."""
        return db.query(Tag).filter(Tag.id == tag_id).first()

    @staticmethod
    def list_tags(db: Session, limit: int = 100, offset: int = 0) -> tuple[list[dict], int]:
        """List all tags with usage count."""
        # Get total count
        total = db.query(func.count(Tag.id)).scalar()

        # Get tags with join to count snippets
        tags = (
            db.query(Tag)
            .order_by(Tag.name.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Build response with snippet counts
        result = []
        for tag in tags:
            snippet_count = len(tag.snippets)
            result.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at,
                "snippet_count": snippet_count,
            })

        return result, total

    @staticmethod
    def delete_tag(db: Session, tag_id: str) -> bool:
        """Delete tag and remove from snippets."""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return False

        try:
            db.delete(tag)
            db.commit()
            logger.info(f"Deleted tag: {tag_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting tag: {e}")
            raise

    @staticmethod
    def update_tag(db: Session, tag_id: str, name: str = None, color: str = None) -> Tag | None:
        """Update tag."""
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None

        try:
            if name:
                tag.name = name
            if color:
                tag.color = color
            db.commit()
            db.refresh(tag)
            logger.info(f"Updated tag: {tag_id}")
            return tag
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Tag name '{name}' already exists")
