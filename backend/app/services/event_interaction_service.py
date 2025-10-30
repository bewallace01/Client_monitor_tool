"""Event user interaction service layer for managing per-user event interactions."""

from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import EventUserInteraction, Event


class EventInteractionService:
    """Service for managing per-user event interactions (read/starred status, notes)."""

    @staticmethod
    def get_interaction(
        db: Session,
        event_id: UUID,
        user_id: int
    ) -> Optional[EventUserInteraction]:
        """Get user interaction for a specific event."""
        return db.query(EventUserInteraction).filter(
            EventUserInteraction.event_id == event_id,
            EventUserInteraction.user_id == user_id
        ).first()

    @staticmethod
    def get_or_create_interaction(
        db: Session,
        event_id: UUID,
        user_id: int
    ) -> EventUserInteraction:
        """Get existing interaction or create new one."""
        interaction = EventInteractionService.get_interaction(db, event_id, user_id)

        if not interaction:
            interaction = EventUserInteraction(
                id=uuid4(),
                event_id=event_id,
                user_id=user_id,
                is_read=False,
                is_starred=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)

        return interaction

    @staticmethod
    def mark_as_read(
        db: Session,
        event_id: UUID,
        user_id: int,
        is_read: bool = True
    ) -> EventUserInteraction:
        """Mark an event as read/unread for a specific user."""
        interaction = EventInteractionService.get_or_create_interaction(db, event_id, user_id)

        interaction.is_read = is_read
        interaction.read_at = datetime.utcnow() if is_read else None
        interaction.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def mark_as_starred(
        db: Session,
        event_id: UUID,
        user_id: int,
        is_starred: bool = True
    ) -> EventUserInteraction:
        """Mark an event as starred/unstarred for a specific user."""
        interaction = EventInteractionService.get_or_create_interaction(db, event_id, user_id)

        interaction.is_starred = is_starred
        interaction.starred_at = datetime.utcnow() if is_starred else None
        interaction.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def update_notes(
        db: Session,
        event_id: UUID,
        user_id: int,
        notes: Optional[str]
    ) -> EventUserInteraction:
        """Update user notes for an event."""
        interaction = EventInteractionService.get_or_create_interaction(db, event_id, user_id)

        interaction.user_notes = notes
        interaction.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def bulk_mark_as_read(
        db: Session,
        event_ids: List[UUID],
        user_id: int,
        is_read: bool = True
    ) -> int:
        """
        Bulk mark events as read/unread for a user.

        Returns number of interactions updated/created.
        """
        count = 0
        for event_id in event_ids:
            EventInteractionService.mark_as_read(db, event_id, user_id, is_read)
            count += 1

        return count

    @staticmethod
    def bulk_mark_as_starred(
        db: Session,
        event_ids: List[UUID],
        user_id: int,
        is_starred: bool = True
    ) -> int:
        """
        Bulk mark events as starred/unstarred for a user.

        Returns number of interactions updated/created.
        """
        count = 0
        for event_id in event_ids:
            EventInteractionService.mark_as_starred(db, event_id, user_id, is_starred)
            count += 1

        return count

    @staticmethod
    def get_user_read_events(
        db: Session,
        user_id: int,
        business_id: UUID,
        limit: int = 50
    ) -> List[EventUserInteraction]:
        """Get all events marked as read by a user."""
        return (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.is_read == True,
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .order_by(EventUserInteraction.read_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_starred_events(
        db: Session,
        user_id: int,
        business_id: UUID,
        limit: int = 50
    ) -> List[EventUserInteraction]:
        """Get all events starred by a user."""
        return (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.is_starred == True,
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .order_by(EventUserInteraction.starred_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_events_with_notes(
        db: Session,
        user_id: int,
        business_id: UUID,
        limit: int = 50
    ) -> List[EventUserInteraction]:
        """Get all events with user notes."""
        return (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.user_notes.isnot(None),
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .order_by(EventUserInteraction.updated_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_interaction_stats(db: Session, user_id: int, business_id: UUID) -> dict:
        """Get statistics about user interactions."""
        # Count events the user has interacted with
        total_read = (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.is_read == True,
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .count()
        )

        total_starred = (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.is_starred == True,
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .count()
        )

        total_with_notes = (
            db.query(EventUserInteraction)
            .join(Event)
            .filter(
                EventUserInteraction.user_id == user_id,
                EventUserInteraction.user_notes.isnot(None),
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .count()
        )

        # Total events available for this business
        total_events = db.query(Event).filter(
            Event.business_id == business_id,
            Event.is_deleted == False
        ).count()

        unread_count = total_events - total_read

        return {
            "total_read": total_read,
            "total_starred": total_starred,
            "total_with_notes": total_with_notes,
            "total_events": total_events,
            "unread_count": unread_count
        }
