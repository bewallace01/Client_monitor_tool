"""Notification service layer for managing user notifications."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.models import Notification
from app.schemas import NotificationCreate, NotificationUpdate


class NotificationService:
    """Service for managing user notifications."""

    @staticmethod
    def get_notifications(
        db: Session,
        business_id: UUID,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        is_read: Optional[bool] = None,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_desc: bool = True
    ) -> Tuple[List[Notification], int]:
        """
        Get notifications for a user with filtering, sorting, and pagination.

        Returns tuple of (notifications, total_count).
        """
        query = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id
        )

        # Apply filters
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        if notification_type:
            query = query.filter(Notification.type == notification_type)

        if priority:
            query = query.filter(Notification.priority == priority)

        if start_date:
            query = query.filter(Notification.created_at >= start_date)

        if end_date:
            query = query.filter(Notification.created_at <= end_date)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_desc:
            query = query.order_by(Notification.created_at.desc())
        else:
            query = query.order_by(Notification.created_at.asc())

        # Apply pagination
        notifications = query.offset(skip).limit(limit).all()

        return notifications, total

    @staticmethod
    def get_notification(
        db: Session,
        notification_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[Notification]:
        """Get a specific notification by ID."""
        return db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.business_id == business_id,
            Notification.user_id == user_id
        ).first()

    @staticmethod
    def create_notification(
        db: Session,
        notification: NotificationCreate
    ) -> Notification:
        """Create a new notification."""
        db_notification = Notification(
            id=uuid4(),
            business_id=notification.business_id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            link_url=notification.link_url,
            related_event_id=notification.related_event_id,
            related_client_id=notification.related_client_id,
            priority=notification.priority,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = NotificationService.get_notification(
            db, notification_id, business_id, user_id
        )

        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_as_unread(
        db: Session,
        notification_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> Optional[Notification]:
        """Mark a notification as unread."""
        notification = NotificationService.get_notification(
            db, notification_id, business_id, user_id
        )

        if not notification:
            return None

        notification.is_read = False
        notification.read_at = None

        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def bulk_mark_as_read(
        db: Session,
        notification_ids: List[UUID],
        business_id: UUID,
        user_id: int
    ) -> int:
        """
        Bulk mark notifications as read.

        Returns number of notifications updated.
        """
        count = db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update(
            {
                "is_read": True,
                "read_at": datetime.utcnow()
            },
            synchronize_session=False
        )

        db.commit()
        return count

    @staticmethod
    def mark_all_as_read(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> int:
        """
        Mark all notifications as read for a user.

        Returns number of notifications updated.
        """
        count = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update(
            {
                "is_read": True,
                "read_at": datetime.utcnow()
            },
            synchronize_session=False
        )

        db.commit()
        return count

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: UUID,
        business_id: UUID,
        user_id: int
    ) -> bool:
        """
        Delete a notification.

        Returns True if deleted, False if not found.
        """
        result = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.business_id == business_id,
            Notification.user_id == user_id
        ).delete()

        db.commit()
        return result > 0

    @staticmethod
    def delete_all_read(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> int:
        """
        Delete all read notifications for a user.

        Returns number of notifications deleted.
        """
        count = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.is_read == True
        ).delete()

        db.commit()
        return count

    @staticmethod
    def get_unread_count(
        db: Session,
        business_id: UUID,
        user_id: int
    ) -> int:
        """Get count of unread notifications for a user."""
        return db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    @staticmethod
    def get_priority_notifications(
        db: Session,
        business_id: UUID,
        user_id: int,
        priority: str = "high",
        limit: int = 10
    ) -> List[Notification]:
        """Get high-priority unread notifications."""
        return (
            db.query(Notification)
            .filter(
                Notification.business_id == business_id,
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.priority == priority
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_notification_stats(db: Session, business_id: UUID, user_id: int) -> dict:
        """Get statistics about notifications for a user."""
        from sqlalchemy import func

        total_notifications = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id
        ).count()

        unread_count = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

        # Count by priority
        priority_counts = (
            db.query(Notification.priority, func.count(Notification.id))
            .filter(
                Notification.business_id == business_id,
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .group_by(Notification.priority)
            .all()
        )
        unread_by_priority = {priority: count for priority, count in priority_counts}

        # Count by type
        type_counts = (
            db.query(Notification.type, func.count(Notification.id))
            .filter(
                Notification.business_id == business_id,
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .group_by(Notification.type)
            .all()
        )
        unread_by_type = {notification_type: count for notification_type, count in type_counts}

        # Recent notifications (last 24 hours)
        from datetime import timedelta
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_count = db.query(Notification).filter(
            Notification.business_id == business_id,
            Notification.user_id == user_id,
            Notification.created_at >= twenty_four_hours_ago
        ).count()

        return {
            "total_notifications": total_notifications,
            "unread_count": unread_count,
            "unread_by_priority": unread_by_priority,
            "unread_by_type": unread_by_type,
            "recent_count": recent_count
        }

    @staticmethod
    def create_high_relevance_notification(
        db: Session,
        business_id: UUID,
        user_id: int,
        event_id: UUID,
        client_id: UUID,
        event_title: str,
        client_name: str
    ) -> Notification:
        """Helper to create a high-relevance event notification."""
        notification = NotificationCreate(
            business_id=business_id,
            user_id=user_id,
            type="high_relevance_event",
            title=f"High Relevance Event: {client_name}",
            message=f"A highly relevant event was detected: {event_title}",
            link_url=f"/events/{event_id}",
            related_event_id=event_id,
            related_client_id=client_id,
            priority="high"
        )
        return NotificationService.create_notification(db, notification)
