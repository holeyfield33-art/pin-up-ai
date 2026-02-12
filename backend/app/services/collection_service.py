"""Business logic for collection operations."""

import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Collection, Snippet

logger = logging.getLogger(__name__)


class CollectionService:
    """Service for collection CRUD operations."""

    @staticmethod
    def create_collection(
        db: Session,
        name: str,
        description: str = None,
        icon: str = None,
        color: str = "#3B82F6",
    ) -> Collection:
        """Create a new collection."""
        collection_id = str(uuid.uuid4())

        try:
            collection = Collection(
                id=collection_id,
                name=name,
                description=description,
                icon=icon,
                color=color,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)
            logger.info(f"Created collection: {collection_id}")
            return collection
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating collection: {e}")
            raise ValueError("Failed to create collection")

    @staticmethod
    def get_collection(db: Session, collection_id: str) -> Collection | None:
        """Get collection by ID."""
        return db.query(Collection).filter(Collection.id == collection_id).first()

    @staticmethod
    def list_collections(db: Session, limit: int = 100, offset: int = 0) -> tuple[list[dict], int]:
        """List all collections with snippet count."""
        # Get total count
        total = db.query(Collection).count()

        # Get collections
        collections = (
            db.query(Collection)
            .order_by(Collection.name.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Build response with snippet counts
        result = []
        for collection in collections:
            snippet_count = len(collection.snippets)
            result.append({
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "icon": collection.icon,
                "color": collection.color,
                "created_at": collection.created_at,
                "updated_at": collection.updated_at,
                "snippet_count": snippet_count,
            })

        return result, total

    @staticmethod
    def update_collection(
        db: Session,
        collection_id: str,
        name: str = None,
        description: str = None,
        icon: str = None,
        color: str = None,
    ) -> Collection | None:
        """Update collection."""
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return None

        try:
            if name:
                collection.name = name
            if description is not None:
                collection.description = description
            if icon:
                collection.icon = icon
            if color:
                collection.color = color
            
            collection.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(collection)
            logger.info(f"Updated collection: {collection_id}")
            return collection
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating collection: {e}")
            raise

    @staticmethod
    def delete_collection(db: Session, collection_id: str) -> bool:
        """Delete collection."""
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return False

        try:
            # Remove collection from all snippets
            for snippet in collection.snippets:
                snippet.collections.remove(collection)
            
            db.delete(collection)
            db.commit()
            logger.info(f"Deleted collection: {collection_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting collection: {e}")
            raise
