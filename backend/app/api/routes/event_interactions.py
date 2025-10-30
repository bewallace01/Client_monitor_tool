"""Event User Interaction API endpoints for per-user event tracking."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.event_interaction_service import EventInteractionService
from app.schemas import (
    EventInteractionResponse,
    EventInteractionUpdate,
    MessageResponse,
    BulkInteractionUpdate,
)

router = APIRouter(prefix="/events", tags=["event-interactions"])


@router.get("/{event_id}/interaction", response_model=EventInteractionResponse)
def get_event_interaction(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's interaction with an event.

    Returns the user's read status, starred status, and notes for the event.
    If no interaction exists, returns default values (unread, not starred, no notes).
    """
    interaction = EventInteractionService.get_interaction(db, event_id, current_user.id)

    if not interaction:
        # Return default interaction if none exists
        return EventInteractionResponse(
            id=None,
            event_id=event_id,
            user_id=current_user.id,
            is_read=False,
            read_at=None,
            is_starred=False,
            starred_at=None,
            user_notes=None,
            created_at=None,
            updated_at=None
        )

    return EventInteractionResponse.model_validate(interaction)


@router.post("/{event_id}/read", response_model=EventInteractionResponse)
def mark_event_as_read(
    event_id: UUID,
    is_read: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark an event as read or unread for the current user.

    - **event_id**: UUID of the event
    - **is_read**: True to mark as read, False to mark as unread (default: True)
    """
    interaction = EventInteractionService.mark_as_read(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        is_read=is_read
    )
    return EventInteractionResponse.model_validate(interaction)


@router.post("/{event_id}/star", response_model=EventInteractionResponse)
def toggle_event_star(
    event_id: UUID,
    is_starred: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Star or unstar an event for the current user.

    - **event_id**: UUID of the event
    - **is_starred**: True to star, False to unstar (default: True)
    """
    interaction = EventInteractionService.mark_as_starred(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        is_starred=is_starred
    )
    return EventInteractionResponse.model_validate(interaction)


@router.put("/{event_id}/notes", response_model=EventInteractionResponse)
def update_event_notes(
    event_id: UUID,
    update: EventInteractionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user notes for an event.

    - **event_id**: UUID of the event
    - **user_notes**: Notes text (or null to remove notes)
    """
    interaction = EventInteractionService.update_notes(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        notes=update.user_notes
    )
    return EventInteractionResponse.model_validate(interaction)


@router.post("/bulk-read", response_model=MessageResponse)
def bulk_mark_as_read(
    bulk_update: BulkInteractionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk mark multiple events as read or unread.

    - **event_ids**: List of event UUIDs
    - **is_read**: True to mark as read, False to mark as unread
    """
    if not bulk_update.event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_ids list cannot be empty"
        )

    count = EventInteractionService.bulk_mark_as_read(
        db=db,
        event_ids=bulk_update.event_ids,
        user_id=current_user.id,
        is_read=bulk_update.is_read if bulk_update.is_read is not None else True
    )

    action = "read" if bulk_update.is_read else "unread"
    return MessageResponse(message=f"Marked {count} event(s) as {action}")


@router.post("/bulk-star", response_model=MessageResponse)
def bulk_star_events(
    bulk_update: BulkInteractionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk star or unstar multiple events.

    - **event_ids**: List of event UUIDs
    - **is_starred**: True to star, False to unstar
    """
    if not bulk_update.event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_ids list cannot be empty"
        )

    if bulk_update.is_starred is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_starred field is required"
        )

    count = EventInteractionService.bulk_mark_as_starred(
        db=db,
        event_ids=bulk_update.event_ids,
        user_id=current_user.id,
        is_starred=bulk_update.is_starred
    )

    action = "starred" if bulk_update.is_starred else "unstarred"
    return MessageResponse(message=f"{action.capitalize()} {count} event(s)")
