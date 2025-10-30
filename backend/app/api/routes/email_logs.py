"""Email log API endpoints."""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user as get_current_user
from app.models.user import User
from app.models.email_log import EmailLog
from app.schemas.email_log import EmailLogResponse, EmailLogList

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-logs", tags=["Email Logs"])


@router.get("/", response_model=EmailLogList)
def list_email_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    email_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    recipient_email: Optional[str] = Query(None),
    event_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List email logs for current business.

    Supports filtering by email type, status, recipient, event, and date range.
    """
    try:
        query = db.query(EmailLog).filter(
            EmailLog.business_id == current_user.business_id
        )

        # Apply filters
        if email_type:
            query = query.filter(EmailLog.email_type == email_type)

        if status_filter:
            query = query.filter(EmailLog.status == status_filter)

        if recipient_email:
            query = query.filter(EmailLog.recipient_email == recipient_email)

        if event_id:
            query = query.filter(EmailLog.event_id == event_id)

        if start_date:
            query = query.filter(EmailLog.created_at >= start_date)

        if end_date:
            query = query.filter(EmailLog.created_at <= end_date)

        # Get total count
        total = query.count()

        # Get paginated results
        logs = query.order_by(
            EmailLog.created_at.desc()
        ).offset(skip).limit(limit).all()

        return {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listing email logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list email logs"
        )


@router.get("/{log_id}", response_model=EmailLogResponse)
def get_email_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific email log by ID."""
    try:
        log = db.query(EmailLog).filter(
            EmailLog.id == log_id,
            EmailLog.business_id == current_user.business_id
        ).first()

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email log not found"
            )

        return log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching email log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch email log"
        )


@router.get("/user/{user_id}", response_model=EmailLogList)
def get_user_email_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get email logs for a specific user.

    Users can only access their own logs unless they are admins.
    """
    # Check authorization
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access other users' email logs"
        )

    try:
        query = db.query(EmailLog).filter(
            EmailLog.business_id == current_user.business_id,
            EmailLog.user_id == user_id
        )

        total = query.count()

        logs = query.order_by(
            EmailLog.created_at.desc()
        ).offset(skip).limit(limit).all()

        return {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error fetching user email logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user email logs"
        )


@router.get("/event/{event_id}", response_model=EmailLogList)
def get_event_email_logs(
    event_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all email logs related to a specific event."""
    try:
        query = db.query(EmailLog).filter(
            EmailLog.business_id == current_user.business_id,
            EmailLog.event_id == event_id
        )

        total = query.count()

        logs = query.order_by(
            EmailLog.created_at.desc()
        ).offset(skip).limit(limit).all()

        return {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error fetching event email logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch event email logs"
        )


@router.get("/stats/summary")
def get_email_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get email statistics for current business.

    Returns counts by status, type, and delivery metrics.
    """
    try:
        query = db.query(EmailLog).filter(
            EmailLog.business_id == current_user.business_id
        )

        if start_date:
            query = query.filter(EmailLog.created_at >= start_date)

        if end_date:
            query = query.filter(EmailLog.created_at <= end_date)

        logs = query.all()

        # Calculate statistics
        total_emails = len(logs)
        sent = sum(1 for log in logs if log.status == "sent")
        failed = sum(1 for log in logs if log.status == "failed")
        pending = sum(1 for log in logs if log.status == "pending")
        bounced = sum(1 for log in logs if log.status == "bounced")

        opened = sum(1 for log in logs if log.opened_at is not None)
        clicked = sum(1 for log in logs if log.clicked_at is not None)

        # Calculate rates
        open_rate = (opened / sent * 100) if sent > 0 else 0
        click_rate = (clicked / sent * 100) if sent > 0 else 0
        delivery_rate = (sent / total_emails * 100) if total_emails > 0 else 0

        # Count by type
        by_type = {}
        for log in logs:
            by_type[log.email_type] = by_type.get(log.email_type, 0) + 1

        return {
            "total_emails": total_emails,
            "sent": sent,
            "failed": failed,
            "pending": pending,
            "bounced": bounced,
            "opened": opened,
            "clicked": clicked,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "delivery_rate": round(delivery_rate, 2),
            "by_type": by_type
        }

    except Exception as e:
        logger.error(f"Error calculating email stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate email statistics"
        )
