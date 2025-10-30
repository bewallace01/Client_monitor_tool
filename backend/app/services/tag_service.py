"""Tag service layer for managing tags and tag assignments."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Tag, ClientTag, EventTag, Client, Event
from app.schemas import TagCreate, TagUpdate


class TagService:
    """Service for managing tags and their assignments to clients/events."""

    @staticmethod
    def get_tags(
        db: Session,
        business_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        color: Optional[str] = None,
        sort_by: str = "name",
        sort_desc: bool = False
    ) -> Tuple[List[Tag], int]:
        """
        Get tags with filtering, sorting, and pagination.

        Returns tuple of (tags, total_count).
        """
        query = db.query(Tag).filter(Tag.business_id == business_id)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Tag.name.ilike(search_term),
                    Tag.description.ilike(search_term)
                )
            )

        if color:
            query = query.filter(Tag.color == color)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(Tag, sort_by, Tag.name)
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        tags = query.offset(skip).limit(limit).all()

        return tags, total

    @staticmethod
    def get_tag(
        db: Session,
        tag_id: UUID,
        business_id: UUID
    ) -> Optional[Tag]:
        """Get a tag by ID."""
        return db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.business_id == business_id
        ).first()

    @staticmethod
    def get_tag_by_name(
        db: Session,
        name: str,
        business_id: UUID
    ) -> Optional[Tag]:
        """Get a tag by name."""
        return db.query(Tag).filter(
            Tag.name == name,
            Tag.business_id == business_id
        ).first()

    @staticmethod
    def create_tag(
        db: Session,
        tag: TagCreate,
        business_id: UUID,
        user_id: int
    ) -> Tag:
        """Create a new tag."""
        # Check if tag with same name exists
        existing = TagService.get_tag_by_name(db, tag.name, business_id)
        if existing:
            return existing  # Return existing tag instead of creating duplicate

        db_tag = Tag(
            id=uuid4(),
            business_id=business_id,
            name=tag.name,
            description=tag.description,
            color=tag.color or "#3B82F6",  # Default blue
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    @staticmethod
    def update_tag(
        db: Session,
        tag_id: UUID,
        business_id: UUID,
        tag_update: TagUpdate
    ) -> Optional[Tag]:
        """Update a tag."""
        db_tag = TagService.get_tag(db, tag_id, business_id)
        if not db_tag:
            return None

        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)

        db_tag.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_tag)
        return db_tag

    @staticmethod
    def delete_tag(
        db: Session,
        tag_id: UUID,
        business_id: UUID
    ) -> bool:
        """
        Delete a tag and all its assignments.

        Returns True if deleted, False if not found.
        """
        db_tag = TagService.get_tag(db, tag_id, business_id)
        if not db_tag:
            return False

        # Delete all assignments
        db.query(ClientTag).filter(ClientTag.tag_id == tag_id).delete()
        db.query(EventTag).filter(EventTag.tag_id == tag_id).delete()

        # Delete the tag
        db.delete(db_tag)
        db.commit()
        return True

    # Client Tag Operations

    @staticmethod
    def add_tag_to_client(
        db: Session,
        client_id: UUID,
        tag_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[ClientTag]:
        """Add a tag to a client."""
        # Verify tag belongs to business
        tag = TagService.get_tag(db, tag_id, business_id)
        if not tag:
            return None

        # Check if already tagged
        existing = db.query(ClientTag).filter(
            ClientTag.client_id == client_id,
            ClientTag.tag_id == tag_id
        ).first()

        if existing:
            return existing

        client_tag = ClientTag(
            id=uuid4(),
            client_id=client_id,
            tag_id=tag_id,
            created_by_user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(client_tag)
        db.commit()
        db.refresh(client_tag)
        return client_tag

    @staticmethod
    def remove_tag_from_client(
        db: Session,
        client_id: UUID,
        tag_id: UUID
    ) -> bool:
        """Remove a tag from a client."""
        result = db.query(ClientTag).filter(
            ClientTag.client_id == client_id,
            ClientTag.tag_id == tag_id
        ).delete()
        db.commit()
        return result > 0

    @staticmethod
    def get_client_tags(db: Session, client_id: UUID) -> List[Tag]:
        """Get all tags for a client."""
        return (
            db.query(Tag)
            .join(ClientTag)
            .filter(ClientTag.client_id == client_id)
            .all()
        )

    # Event Tag Operations

    @staticmethod
    def add_tag_to_event(
        db: Session,
        event_id: UUID,
        tag_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[EventTag]:
        """Add a tag to an event."""
        # Verify tag belongs to business
        tag = TagService.get_tag(db, tag_id, business_id)
        if not tag:
            return None

        # Check if already tagged
        existing = db.query(EventTag).filter(
            EventTag.event_id == event_id,
            EventTag.tag_id == tag_id
        ).first()

        if existing:
            return existing

        event_tag = EventTag(
            id=uuid4(),
            event_id=event_id,
            tag_id=tag_id,
            created_by_user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(event_tag)
        db.commit()
        db.refresh(event_tag)
        return event_tag

    @staticmethod
    def remove_tag_from_event(
        db: Session,
        event_id: UUID,
        tag_id: UUID
    ) -> bool:
        """Remove a tag from an event."""
        result = db.query(EventTag).filter(
            EventTag.event_id == event_id,
            EventTag.tag_id == tag_id
        ).delete()
        db.commit()
        return result > 0

    @staticmethod
    def get_event_tags(db: Session, event_id: UUID) -> List[Tag]:
        """Get all tags for an event."""
        return (
            db.query(Tag)
            .join(EventTag)
            .filter(EventTag.event_id == event_id)
            .all()
        )

    # Statistics

    @staticmethod
    def get_tag_stats(db: Session, business_id: UUID) -> dict:
        """Get statistics about tags."""
        total_tags = db.query(Tag).filter(Tag.business_id == business_id).count()

        # Tag usage counts
        client_tag_counts = (
            db.query(Tag.id, Tag.name, func.count(ClientTag.id))
            .outerjoin(ClientTag)
            .filter(Tag.business_id == business_id)
            .group_by(Tag.id, Tag.name)
            .all()
        )

        event_tag_counts = (
            db.query(Tag.id, Tag.name, func.count(EventTag.id))
            .outerjoin(EventTag)
            .filter(Tag.business_id == business_id)
            .group_by(Tag.id, Tag.name)
            .all()
        )

        most_used_tags = []
        for tag_id, tag_name, client_count in client_tag_counts:
            event_count = next((count for tid, _, count in event_tag_counts if tid == tag_id), 0)
            total_usage = client_count + event_count
            if total_usage > 0:
                most_used_tags.append({
                    "tag_id": str(tag_id),
                    "tag_name": tag_name,
                    "client_count": client_count,
                    "event_count": event_count,
                    "total_usage": total_usage
                })

        most_used_tags = sorted(most_used_tags, key=lambda x: x["total_usage"], reverse=True)[:10]

        return {
            "total_tags": total_tags,
            "most_used_tags": most_used_tags
        }
