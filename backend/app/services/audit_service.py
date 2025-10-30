"""Audit log service layer for tracking system changes."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, User


class AuditLogService:
    """Service for querying and managing audit logs."""

    @staticmethod
    def get_audit_logs(
        db: Session,
        business_id: UUID,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_desc: bool = True
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs with filtering, sorting, and pagination.

        Returns tuple of (audit_logs, total_count).
        """
        query = db.query(AuditLog).options(joinedload(AuditLog.user))

        # Filter by business
        query = query.filter(AuditLog.business_id == business_id)

        # Apply filters
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_desc:
            query = query.order_by(AuditLog.created_at.desc())
        else:
            query = query.order_by(AuditLog.created_at.asc())

        # Apply pagination
        audit_logs = query.offset(skip).limit(limit).all()

        return audit_logs, total

    @staticmethod
    def get_entity_history(
        db: Session,
        business_id: UUID,
        entity_type: str,
        entity_id: UUID,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get complete audit history for a specific entity."""
        return (
            db.query(AuditLog)
            .options(joinedload(AuditLog.user))
            .filter(
                AuditLog.business_id == business_id,
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_activity(
        db: Session,
        business_id: UUID,
        user_id: int,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get recent activity for a specific user."""
        return (
            db.query(AuditLog)
            .filter(
                AuditLog.business_id == business_id,
                AuditLog.user_id == user_id
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_activity(
        db: Session,
        business_id: UUID,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get recent audit activity for the business."""
        return (
            db.query(AuditLog)
            .options(joinedload(AuditLog.user))
            .filter(AuditLog.business_id == business_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_audit_stats(db: Session, business_id: UUID) -> dict:
        """Get statistics about audit logs."""
        from sqlalchemy import func

        total_logs = db.query(AuditLog).filter(
            AuditLog.business_id == business_id
        ).count()

        # Logs by action
        action_stats = (
            db.query(AuditLog.action, func.count(AuditLog.id))
            .filter(AuditLog.business_id == business_id)
            .group_by(AuditLog.action)
            .all()
        )
        logs_by_action = {action: count for action, count in action_stats}

        # Logs by entity type
        entity_stats = (
            db.query(AuditLog.entity_type, func.count(AuditLog.id))
            .filter(AuditLog.business_id == business_id)
            .group_by(AuditLog.entity_type)
            .all()
        )
        logs_by_entity = {entity_type: count for entity_type, count in entity_stats}

        # Recent activity (last 24 hours)
        from datetime import timedelta
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_activity_count = db.query(AuditLog).filter(
            AuditLog.business_id == business_id,
            AuditLog.created_at >= twenty_four_hours_ago
        ).count()

        # Most active users (top 5)
        active_users = (
            db.query(AuditLog.user_id, func.count(AuditLog.id))
            .filter(AuditLog.business_id == business_id)
            .group_by(AuditLog.user_id)
            .order_by(func.count(AuditLog.id).desc())
            .limit(5)
            .all()
        )
        most_active_users = [{"user_id": user_id, "action_count": count} for user_id, count in active_users]

        return {
            "total_logs": total_logs,
            "logs_by_action": logs_by_action,
            "logs_by_entity": logs_by_entity,
            "recent_activity_count": recent_activity_count,
            "most_active_users": most_active_users
        }

    @staticmethod
    def search_audit_logs(
        db: Session,
        business_id: UUID,
        search_term: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Search audit logs by entity type, action, or changes.

        Note: This searches in the changes JSON field for PostgreSQL.
        For SQLite, it searches action and entity_type only.
        """
        search_pattern = f"%{search_term}%"

        # Basic search in action and entity_type
        query = db.query(AuditLog).options(joinedload(AuditLog.user)).filter(
            AuditLog.business_id == business_id,
            or_(
                AuditLog.action.ilike(search_pattern),
                AuditLog.entity_type.ilike(search_pattern)
            )
        )

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
