"""Notification API endpoints for user notifications."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationFilters,
    BulkNotificationUpdate,
    MessageResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    start_date: Optional[datetime] = Query(None, description="Filter notifications after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter notifications before this date"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get notifications for the current user.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 50, max: 100)
    - **is_read**: Filter by read status
    - **notification_type**: Filter by type
    - **priority**: Filter by priority (low, normal, high, urgent)
    - **start_date**: Notifications after this date
    - **end_date**: Notifications before this date
    - **sort_desc**: Sort descending if true (default: true)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    notifications, total = NotificationService.get_notifications(
        db=db,
        business_id=current_user.business_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_read=is_read,
        notification_type=notification_type,
        priority=priority,
        start_date=start_date,
        end_date=end_date,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    # Get unread count
    unread_count = NotificationService.get_unread_count(
        db, current_user.business_id, current_user.id
    )

    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[NotificationResponse.model_validate(notif) for notif in notifications],
    )


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications for the current user.

    Returns: {"unread_count": int}
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    count = NotificationService.get_unread_count(
        db, current_user.business_id, current_user.id
    )

    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single notification by UUID.

    - **notification_id**: The UUID of the notification to retrieve
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    notification = NotificationService.get_notification(
        db, notification_id, current_user.business_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    return NotificationResponse.model_validate(notification)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read.

    - **notification_id**: The UUID of the notification to mark as read
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    notification = NotificationService.mark_as_read(
        db, notification_id, current_user.business_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    return NotificationResponse.model_validate(notification)


@router.post("/{notification_id}/unread", response_model=NotificationResponse)
def mark_notification_as_unread(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as unread.

    - **notification_id**: The UUID of the notification to mark as unread
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    notification = NotificationService.mark_as_unread(
        db, notification_id, current_user.business_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    return NotificationResponse.model_validate(notification)


@router.post("/bulk-read", response_model=MessageResponse)
def bulk_mark_as_read(
    bulk_update: BulkNotificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk mark multiple notifications as read or unread.

    - **notification_ids**: List of notification UUIDs
    - **is_read**: True to mark as read, False to mark as unread
    """
    if not bulk_update.notification_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="notification_ids list cannot be empty"
        )

    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    count = NotificationService.bulk_mark_as_read(
        db=db,
        notification_ids=bulk_update.notification_ids,
        business_id=current_user.business_id,
        user_id=current_user.id
    )

    action = "read" if bulk_update.is_read else "unread"
    return MessageResponse(message=f"Marked {count} notification(s) as {action}")


@router.post("/mark-all-read", response_model=MessageResponse)
def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for the current user.
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    count = NotificationService.mark_all_as_read(
        db, current_user.business_id, current_user.id
    )

    return MessageResponse(message=f"Marked {count} notification(s) as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification.

    - **notification_id**: The UUID of the notification to delete
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    deleted = NotificationService.delete_notification(
        db, notification_id, current_user.business_id, current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    return MessageResponse(message=f"Notification {notification_id} deleted successfully")


@router.delete("/read/all", response_model=MessageResponse)
def delete_all_read_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete all read notifications for the current user.
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    count = NotificationService.delete_all_read(
        db, current_user.business_id, current_user.id
    )

    return MessageResponse(message=f"Deleted {count} read notification(s)")
