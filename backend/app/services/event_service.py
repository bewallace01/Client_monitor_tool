"""Event service layer for business logic."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session, joinedload

from app.models import Event, Client, AuditLog, EventUserInteraction
from app.schemas import EventCreate, EventUpdate


class EventService:
    """Service for managing events."""

    @staticmethod
    def _create_audit_log(
        db: Session,
        business_id: UUID,
        user_id: int,
        action: str,
        table_name: str,
        record_id: UUID,
        changes: Optional[dict] = None
    ):
        """Helper method to create audit log entries."""
        from uuid import uuid4
        import json

        # Extract old/new values from changes dict
        old_values = {}
        new_values = {}
        changed_fields = []

        if changes:
            for field, value in changes.items():
                if isinstance(value, dict) and 'old' in value and 'new' in value:
                    old_values[field] = value['old']
                    new_values[field] = value['new']
                    changed_fields.append(field)
                else:
                    # Simple value (for CREATE/DELETE)
                    new_values[field] = value
                    changed_fields.append(field)

        audit_log = AuditLog(
            id=uuid4(),
            business_id=business_id,
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=str(record_id),
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            changed_fields=json.dumps(changed_fields) if changed_fields else None,
            created_at=datetime.utcnow()
        )
        db.add(audit_log)

    @staticmethod
    def get_events(
        db: Session,
        business_id: Optional[UUID] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
        client_id: Optional[UUID] = None,
        category: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_starred: Optional[bool] = None,
        min_relevance: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        sort_by: str = "event_date",
        sort_desc: bool = True,
        include_deleted: bool = False,
    ) -> Tuple[List[Event], int]:
        """
        Get list of events with filtering, sorting, and pagination.

        If business_id is None, returns all events (for system admins).
        Note: is_read and is_starred are now per-user via EventUserInteraction.
        These filters will only work if user_id is provided.

        Returns tuple of (events, total_count).
        """
        query = db.query(Event).options(joinedload(Event.client))

        # Filter by business_id if provided (None means all events for system admin)
        if business_id is not None:
            query = query.filter(Event.business_id == business_id)

        # Soft delete filter
        if not include_deleted:
            query = query.filter(Event.is_deleted == False)

        # Apply filters
        if client_id:
            query = query.filter(Event.client_id == client_id)

        if category:
            query = query.filter(Event.category == category)

        # For per-user filters, join with EventUserInteraction
        if user_id and (is_read is not None or is_starred is not None):
            query = query.outerjoin(
                EventUserInteraction,
                and_(
                    EventUserInteraction.event_id == Event.id,
                    EventUserInteraction.user_id == user_id
                )
            )

            if is_read is not None:
                if is_read:
                    query = query.filter(EventUserInteraction.is_read == True)
                else:
                    query = query.filter(
                        or_(
                            EventUserInteraction.is_read == False,
                            EventUserInteraction.id.is_(None)
                        )
                    )

            if is_starred is not None:
                if is_starred:
                    query = query.filter(EventUserInteraction.is_starred == True)
                else:
                    query = query.filter(
                        or_(
                            EventUserInteraction.is_starred == False,
                            EventUserInteraction.id.is_(None)
                        )
                    )

        if min_relevance is not None:
            query = query.filter(Event.relevance_score >= min_relevance)

        if start_date:
            query = query.filter(Event.event_date >= start_date)

        if end_date:
            query = query.filter(Event.event_date <= end_date)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.source.ilike(search_term),
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(Event, sort_by, Event.event_date)
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        events = query.offset(skip).limit(limit).all()

        return events, total

    @staticmethod
    def get_event(
        db: Session,
        event_id: UUID,
        business_id: Optional[UUID] = None,
        include_deleted: bool = False
    ) -> Optional[Event]:
        """
        Get a single event by ID.

        If business_id is None, searches all events (for system admins).
        """
        query = db.query(Event).filter(Event.id == event_id)

        if business_id is not None:
            query = query.filter(Event.business_id == business_id)

        if not include_deleted:
            query = query.filter(Event.is_deleted == False)

        return query.first()

    @staticmethod
    def create_event(
        db: Session,
        event: EventCreate,
        business_id: UUID,
        user_id: int
    ) -> Event:
        """Create a new event."""
        from uuid import uuid4

        event_id = uuid4()
        db_event = Event(
            id=event_id,
            business_id=business_id,
            client_id=event.client_id,
            title=event.title,
            description=event.description,
            url=event.url,
            source=event.source,
            category=event.category,
            relevance_score=event.relevance_score,
            sentiment_score=event.sentiment_score,
            event_date=event.event_date,
            discovered_at=datetime.utcnow(),
            content_hash=event.content_hash,
            created_by_user_id=user_id,
            is_deleted=False,
        )
        db.add(db_event)

        # Create audit log
        EventService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="CREATE",
            table_name="events",
            record_id=event_id,
            changes={"title": event.title, "client_id": str(event.client_id)}
        )

        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def update_event(
        db: Session,
        event_id: UUID,
        business_id: UUID,
        event_update: EventUpdate,
        user_id: int
    ) -> Optional[Event]:
        """Update an existing event."""
        db_event = db.query(Event).filter(
            Event.id == event_id,
            Event.business_id == business_id,
            Event.is_deleted == False
        ).first()

        if not db_event:
            return None

        # Track changes for audit log
        update_data = event_update.model_dump(exclude_unset=True)
        changes = {}
        for field, value in update_data.items():
            old_value = getattr(db_event, field)
            if old_value != value:
                changes[field] = {"old": str(old_value), "new": str(value)}
                setattr(db_event, field, value)

        # Create audit log if there were changes
        if changes:
            EventService._create_audit_log(
                db=db,
                business_id=business_id,
                user_id=user_id,
                action="UPDATE",
                table_name="events",
                record_id=event_id,
                changes=changes
            )

        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def delete_event(
        db: Session,
        event_id: UUID,
        business_id: UUID,
        user_id: int,
        hard_delete: bool = False,
        is_system_admin: bool = False
    ) -> bool:
        """
        Delete an event (soft delete by default).

        Args:
            db: Database session
            event_id: UUID of event to delete
            business_id: UUID of business for authorization (can be None for system admin)
            user_id: User performing the deletion
            hard_delete: If True, permanently delete; if False, soft delete (default)
            is_system_admin: If True, bypass business_id check

        Returns True if deleted, False if not found.
        """
        # System admins can delete any event
        if is_system_admin:
            db_event = db.query(Event).filter(Event.id == event_id).first()
        else:
            db_event = db.query(Event).filter(
                Event.id == event_id,
                Event.business_id == business_id
            ).first()

        if not db_event:
            return False

        # Use event's business_id for audit log if business_id is None (system admin)
        audit_business_id = business_id or db_event.business_id

        if hard_delete:
            # Permanent deletion
            db.delete(db_event)
            EventService._create_audit_log(
                db=db,
                business_id=audit_business_id,
                user_id=user_id,
                action="HARD_DELETE",
                table_name="events",
                record_id=event_id,
                changes={"title": db_event.title}
            )
        else:
            # Soft delete
            if db_event.is_deleted:
                return False  # Already deleted

            db_event.is_deleted = True
            db_event.deleted_at = datetime.utcnow()
            db_event.deleted_by_user_id = user_id

            EventService._create_audit_log(
                db=db,
                business_id=audit_business_id,
                user_id=user_id,
                action="DELETE",
                table_name="events",
                record_id=event_id,
                changes={"title": db_event.title}
            )

        db.commit()
        return True

    @staticmethod
    def restore_event(
        db: Session,
        event_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[Event]:
        """
        Restore a soft-deleted event.

        Returns the restored event or None if not found.
        """
        db_event = db.query(Event).filter(
            Event.id == event_id,
            Event.business_id == business_id,
            Event.is_deleted == True
        ).first()

        if not db_event:
            return None

        db_event.is_deleted = False
        db_event.deleted_at = None
        db_event.deleted_by_user_id = None

        EventService._create_audit_log(
            db=db,
            business_id=business_id,
            user_id=user_id,
            action="RESTORE",
            table_name="events",
            record_id=event_id,
            changes={"title": db_event.title}
        )

        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def bulk_delete_events(
        db: Session,
        event_ids: List[UUID],
        business_id: UUID,
        user_id: int,
        hard_delete: bool = False
    ) -> int:
        """
        Bulk delete events (soft delete by default).

        Returns number of events deleted.
        """
        query = db.query(Event).filter(
            Event.id.in_(event_ids),
            Event.business_id == business_id
        )

        if hard_delete:
            # Permanent deletion
            events = query.all()
            for event in events:
                EventService._create_audit_log(
                    db=db,
                    business_id=business_id,
                    user_id=user_id,
                    action="HARD_DELETE",
                    table_name="events",
                    record_id=event.id,
                    changes={"title": event.title}
                )
            count = query.delete(synchronize_session=False)
        else:
            # Soft delete
            query = query.filter(Event.is_deleted == False)
            events = query.all()
            for event in events:
                event.is_deleted = True
                event.deleted_at = datetime.utcnow()
                event.deleted_by_user_id = user_id

                EventService._create_audit_log(
                    db=db,
                    business_id=business_id,
                    user_id=user_id,
                    action="DELETE",
                    table_name="events",
                    record_id=event.id,
                    changes={"title": event.title}
                )
            count = len(events)

        db.commit()
        return count

    @staticmethod
    def get_event_stats(db: Session, business_id: Optional[UUID] = None, user_id: Optional[int] = None) -> dict:
        """
        Get statistics about events for a specific business.

        If business_id is None, returns stats for all events (system admins).
        If user_id is provided, includes per-user unread/starred counts.
        """
        base_query = db.query(Event).filter(Event.is_deleted == False)

        if business_id is not None:
            base_query = base_query.filter(Event.business_id == business_id)

        total_events = base_query.count()

        # Per-user stats via EventUserInteraction
        if user_id:
            interaction_filter = [
                Event.is_deleted == False,
                EventUserInteraction.user_id == user_id
            ]
            if business_id is not None:
                interaction_filter.append(Event.business_id == business_id)

            interaction_query = db.query(EventUserInteraction).join(Event).filter(*interaction_filter)

            unread_events = base_query.outerjoin(
                EventUserInteraction,
                and_(
                    EventUserInteraction.event_id == Event.id,
                    EventUserInteraction.user_id == user_id
                )
            ).filter(
                or_(
                    EventUserInteraction.is_read == False,
                    EventUserInteraction.id.is_(None)
                )
            ).count()

            starred_events = interaction_query.filter(EventUserInteraction.is_starred == True).count()
        else:
            # Without user_id, count all unread/unstarred
            unread_events = total_events
            starred_events = 0

        # Events by category
        category_stats = (
            base_query
            .with_entities(Event.category, func.count(Event.id))
            .group_by(Event.category)
            .all()
        )
        events_by_category = {category: count for category, count in category_stats}

        # Events by sentiment (positive, neutral, negative)
        sentiment_distribution = {
            "positive": base_query.filter(Event.sentiment_score > 0.3).count(),
            "neutral": base_query.filter(
                and_(Event.sentiment_score >= -0.3, Event.sentiment_score <= 0.3)
            ).count(),
            "negative": base_query.filter(Event.sentiment_score < -0.3).count(),
        }

        # Recent events (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events_count = base_query.filter(Event.event_date >= seven_days_ago).count()

        return {
            "total_events": total_events,
            "unread_events": unread_events,
            "starred_events": starred_events,
            "events_by_category": events_by_category,
            "events_by_sentiment": sentiment_distribution,
            "recent_events_count": recent_events_count,
        }

    @staticmethod
    def get_all_categories(db: Session, business_id: Optional[UUID] = None) -> List[str]:
        """
        Get list of all unique categories for a specific business.

        If business_id is None, returns all categories (for system admins).
        """
        query = db.query(Event.category).filter(Event.is_deleted == False)

        if business_id is not None:
            query = query.filter(Event.business_id == business_id)

        categories = query.distinct().all()
        return [category[0] for category in categories]

    @staticmethod
    def get_events_for_client(
        db: Session,
        client_id: UUID,
        business_id: UUID,
        limit: int = 10
    ) -> List[Event]:
        """Get recent events for a specific client."""
        return (
            db.query(Event)
            .filter(
                Event.client_id == client_id,
                Event.business_id == business_id,
                Event.is_deleted == False
            )
            .order_by(Event.event_date.desc())
            .limit(limit)
            .all()
        )
