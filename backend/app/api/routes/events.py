"""Event API endpoints."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.event_service import EventService
from app.services.client_service import ClientService
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
    EventStats,
    MessageResponse,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
def get_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    client_id: Optional[UUID] = Query(None, description="Filter by client UUID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_read: Optional[bool] = Query(None, description="Filter by read status (per-user)"),
    is_starred: Optional[bool] = Query(None, description="Filter by starred status (per-user)"),
    min_relevance: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum relevance score"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    search: Optional[str] = Query(None, description="Search in title, description, source"),
    sort_by: str = Query("event_date", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of events with filtering, sorting, and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 50, max: 100)
    - **client_id**: Filter by client UUID
    - **category**: Filter by category (funding, acquisition, etc.)
    - **is_read**: Filter by read status (per-user)
    - **is_starred**: Filter by starred status (per-user)
    - **min_relevance**: Minimum relevance score (0-1)
    - **start_date**: Events after this date
    - **end_date**: Events before this date
    - **search**: Search term for title, description, source
    - **sort_by**: Field to sort by (default: event_date)
    - **sort_desc**: Sort descending if true (default: true)
    """
    # Get user's business_id (system admins can see all events)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all events (business_id=None), others get their business events
    business_id = None if current_user.is_system_admin else current_user.business_id

    events, total = EventService.get_events(
        db=db,
        business_id=business_id,
        user_id=current_user.id,  # For per-user read/starred filtering
        skip=skip,
        limit=limit,
        client_id=client_id,
        category=category,
        is_read=is_read,
        is_starred=is_starred,
        min_relevance=min_relevance,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return EventListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[EventResponse.model_validate(event) for event in events],
    )


@router.get("/stats", response_model=EventStats)
def get_event_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get event statistics.

    Returns counts and distributions of events (per-user stats for read/starred).
    """
    # Get user's business_id (system admins can see all events)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all events (business_id=None), others get their business events
    business_id = None if current_user.is_system_admin else current_user.business_id

    stats = EventService.get_event_stats(db, business_id, current_user.id)
    return EventStats(**stats)


@router.get("/categories", response_model=list[str])
def get_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all unique categories."""
    # Get user's business_id (system admins can see all categories)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all categories (business_id=None), others get their business categories
    business_id = None if current_user.is_system_admin else current_user.business_id

    return EventService.get_all_categories(db, business_id)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single event by UUID.

    - **event_id**: The UUID of the event to retrieve
    """
    # Get user's business_id (system admins can see all events)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all events (business_id=None), others get their business events
    business_id = None if current_user.is_system_admin else current_user.business_id

    event = EventService.get_event(db, event_id, business_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )
    return EventResponse.model_validate(event)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new event.

    - **client_id**: UUID of the client this event belongs to (required)
    - **title**: Event title (required)
    - **description**: Event description
    - **url**: Source URL
    - **source**: Source name
    - **category**: Event category (default: other)
    - **relevance_score**: Relevance score 0-1 (default: 0.5)
    - **sentiment_score**: Sentiment score -1 to 1
    - **event_date**: When the event occurred (required)
    - **content_hash**: Hash for deduplication
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    # Verify client exists and belongs to user's business
    client = ClientService.get_client(db, event.client_id, business_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {event.client_id} not found",
        )

    db_event = EventService.create_event(
        db=db,
        event=event,
        business_id=business_id,
        user_id=current_user.id
    )
    return EventResponse.model_validate(db_event)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: UUID,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing event.

    - **event_id**: The UUID of the event to update

    All fields are optional. Only provided fields will be updated.
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    db_event = EventService.update_event(
        db=db,
        event_id=event_id,
        business_id=business_id,
        event_update=event_update,
        user_id=current_user.id
    )
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )
    return EventResponse.model_validate(db_event)


@router.delete("/{event_id}", response_model=MessageResponse)
def delete_event(
    event_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an event (soft delete by default).

    - **event_id**: The UUID of the event to delete
    - **hard_delete**: If true, permanently delete; if false, soft delete (default)
    """
    # System admins can delete any event, others need business_id
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    deleted = EventService.delete_event(
        db=db,
        event_id=event_id,
        business_id=business_id,
        user_id=current_user.id,
        hard_delete=hard_delete,
        is_system_admin=current_user.is_system_admin
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )

    delete_type = "permanently deleted" if hard_delete else "deleted"
    return MessageResponse(message=f"Event {event_id} {delete_type} successfully")


@router.post("/{event_id}/restore", response_model=EventResponse)
def restore_event(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Restore a soft-deleted event.

    - **event_id**: The UUID of the event to restore
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    db_event = EventService.restore_event(
        db=db,
        event_id=event_id,
        business_id=business_id,
        user_id=current_user.id
    )
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deleted event with id {event_id} not found",
        )
    return EventResponse.model_validate(db_event)


@router.post("/bulk-delete", response_model=MessageResponse)
def bulk_delete_events(
    event_ids: list[UUID],
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk delete multiple events (soft delete by default).

    - **event_ids**: List of event UUIDs to delete (required)
    - **hard_delete**: If true, permanently delete; if false, soft delete (default)
    """
    if not event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_ids list cannot be empty",
        )

    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    count = EventService.bulk_delete_events(
        db=db,
        event_ids=event_ids,
        business_id=business_id,
        user_id=current_user.id,
        hard_delete=hard_delete
    )

    delete_type = "permanently deleted" if hard_delete else "deleted"
    return MessageResponse(message=f"{delete_type.capitalize()} {count} event(s) successfully")
