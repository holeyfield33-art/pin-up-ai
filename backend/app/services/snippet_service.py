"""Business logic for snippet operations."""

import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models import Snippet, Tag, Collection
from app.schemas import SnippetCreate, SnippetUpdate

logger = logging.getLogger(__name__)


class SnippetService:
    """Service for snippet CRUD operations."""

    @staticmethod
    def create_snippet(db: Session, snippet_create: SnippetCreate) -> Snippet:
        """Create a new snippet."""
        snippet_id = str(uuid.uuid4())
        
        try:
            snippet = Snippet(
                id=snippet_id,
                title=snippet_create.title,
                body=snippet_create.body,
                language=snippet_create.language,
                source=snippet_create.source,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Add tags
            if snippet_create.tag_ids:
                tags = db.query(Tag).filter(Tag.id.in_(snippet_create.tag_ids)).all()
                snippet.tags.extend(tags)

            # Add collections
            if snippet_create.collection_ids:
                collections = db.query(Collection).filter(
                    Collection.id.in_(snippet_create.collection_ids)
                ).all()
                snippet.collections.extend(collections)

            db.add(snippet)
            db.commit()
            db.refresh(snippet)
            logger.info(f"Created snippet: {snippet_id}")
            return snippet
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating snippet: {e}")
            raise ValueError("Failed to create snippet")

    @staticmethod
    def get_snippet(db: Session, snippet_id: str) -> Snippet | None:
        """Get snippet by ID."""
        return db.query(Snippet).filter(Snippet.id == snippet_id).first()

    @staticmethod
    def list_snippets(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        collection_id: str = None,
        tag_id: str = None,
    ) -> tuple[list[Snippet], int]:
        """List snippets with optional filtering."""
        query = db.query(Snippet).filter(Snippet.is_archived == False)

        if collection_id:
            query = query.filter(Snippet.collections.any(Collection.id == collection_id))

        if tag_id:
            query = query.filter(Snippet.tags.any(Tag.id == tag_id))

        total = query.count()
        snippets = query.order_by(Snippet.created_at.desc()).offset(offset).limit(limit).all()
        return snippets, total

    @staticmethod
    def update_snippet(db: Session, snippet_id: str, update: SnippetUpdate) -> Snippet | None:
        """Update snippet."""
        snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
        if not snippet:
            return None

        try:
            # Update fields
            if update.title is not None:
                snippet.title = update.title
            if update.body is not None:
                snippet.body = update.body
            if update.language is not None:
                snippet.language = update.language
            if update.source is not None:
                snippet.source = update.source

            snippet.updated_at = datetime.utcnow()

            # Update tags
            if update.tag_ids is not None:
                tags = db.query(Tag).filter(Tag.id.in_(update.tag_ids)).all()
                snippet.tags = tags

            # Update collections
            if update.collection_ids is not None:
                collections = db.query(Collection).filter(
                    Collection.id.in_(update.collection_ids)
                ).all()
                snippet.collections = collections

            db.commit()
            db.refresh(snippet)
            logger.info(f"Updated snippet: {snippet_id}")
            return snippet
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating snippet: {e}")
            raise

    @staticmethod
    def delete_snippet(db: Session, snippet_id: str) -> bool:
        """Delete snippet (soft delete)."""
        snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
        if not snippet:
            return False

        try:
            snippet.is_archived = True
            db.commit()
            logger.info(f"Archived snippet: {snippet_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting snippet: {e}")
            raise

    @staticmethod
    def search_snippets(db: Session, query: str, limit: int = 50, offset: int = 0) -> tuple[list[Snippet], int]:
        """Search snippets by title and body."""
        search_query = db.query(Snippet).filter(
            Snippet.is_archived == False,
            or_(
                Snippet.title.ilike(f"%{query}%"),
                Snippet.body.ilike(f"%{query}%"),
            ),
        )

        total = search_query.count()
        snippets = (
            search_query
            .order_by(Snippet.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return snippets, total

    @staticmethod
    def export_snippets(db: Session, format: str = "json") -> str:
        """Export all snippets in specified format."""
        snippets = db.query(Snippet).filter(Snippet.is_archived == False).all()

        if format == "json":
            import json
            data = [
                {
                    "id": s.id,
                    "title": s.title,
                    "body": s.body,
                    "language": s.language,
                    "source": s.source,
                    "tags": [t.name for t in s.tags],
                    "collections": [c.name for c in s.collections],
                    "created_at": s.created_at.isoformat(),
                }
                for s in snippets
            ]
            return json.dumps(data, indent=2)
        
        elif format == "markdown":
            lines = ["# Pin-Up AI Snippets Export\n"]
            for s in snippets:
                lines.append(f"## {s.title}\n")
                if s.source:
                    lines.append(f"**Source:** {s.source}\n")
                if s.tags:
                    lines.append(f"**Tags:** {', '.join(t.name for t in s.tags)}\n")
                lines.append(f"```{s.language}\n{s.body}\n```\n\n")
            return "".join(lines)

        raise ValueError(f"Unsupported format: {format}")
