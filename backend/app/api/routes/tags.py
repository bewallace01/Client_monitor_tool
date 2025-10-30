"""Tag management API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.tag_service import TagService
from app.schemas import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
    ClientTagCreate,
    ClientTagResponse,
    EventTagCreate,
    EventTagResponse,
    MessageResponse,
)

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def get_tags(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in tag name and description"),
    color: Optional[str] = Query(None, description="Filter by color"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of tags for the current user's business.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 200)
    - **search**: Search term for name and description
    - **color**: Filter by tag color
    - **sort_by**: Field to sort by (default: name)
    - **sort_desc**: Sort descending if true (default: false)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    tags, total = TagService.get_tags(
        db=db,
        business_id=current_user.business_id,
        skip=skip,
        limit=limit,
        search=search,
        color=color,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return TagListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[TagResponse.model_validate(tag) for tag in tags],
    )


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single tag by UUID.

    - **tag_id**: The UUID of the tag to retrieve
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    tag = TagService.get_tag(db, tag_id, current_user.business_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    return TagResponse.model_validate(tag)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag.

    - **name**: Tag name (required, unique per business)
    - **description**: Tag description
    - **color**: Tag color (hex code, default: #3B82F6)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    db_tag = TagService.create_tag(
        db=db,
        tag=tag,
        business_id=current_user.business_id,
        user_id=current_user.id
    )
    return TagResponse.model_validate(db_tag)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing tag.

    - **tag_id**: The UUID of the tag to update

    All fields are optional. Only provided fields will be updated.
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    db_tag = TagService.update_tag(
        db=db,
        tag_id=tag_id,
        business_id=current_user.business_id,
        tag_update=tag_update
    )
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    return TagResponse.model_validate(db_tag)


@router.delete("/{tag_id}", response_model=MessageResponse)
def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag.

    - **tag_id**: The UUID of the tag to delete

    This will also remove all tag assignments from clients and events.
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    deleted = TagService.delete_tag(
        db=db,
        tag_id=tag_id,
        business_id=current_user.business_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    return MessageResponse(message=f"Tag {tag_id} deleted successfully")


# Client Tag Endpoints

@router.post("/clients/{client_id}/tags", response_model=ClientTagResponse, status_code=status.HTTP_201_CREATED)
def add_tag_to_client(
    client_id: UUID,
    tag_data: ClientTagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a tag to a client.

    - **client_id**: UUID of the client
    - **tag_id**: UUID of the tag to add
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    client_tag = TagService.add_tag_to_client(
        db=db,
        client_id=client_id,
        tag_id=tag_data.tag_id,
        business_id=current_user.business_id,
        user_id=current_user.id
    )

    if not client_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or does not belong to your business"
        )

    return ClientTagResponse.model_validate(client_tag)


@router.delete("/clients/{client_id}/tags/{tag_id}", response_model=MessageResponse)
def remove_tag_from_client(
    client_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a client.

    - **client_id**: UUID of the client
    - **tag_id**: UUID of the tag to remove
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    removed = TagService.remove_tag_from_client(db, client_id, tag_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag assignment not found"
        )

    return MessageResponse(message="Tag removed from client successfully")


@router.get("/clients/{client_id}/tags", response_model=list[TagResponse])
def get_client_tags(
    client_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags assigned to a client.

    - **client_id**: UUID of the client
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    tags = TagService.get_client_tags(db, client_id)
    return [TagResponse.model_validate(tag) for tag in tags]


# Event Tag Endpoints

@router.post("/events/{event_id}/tags", response_model=EventTagResponse, status_code=status.HTTP_201_CREATED)
def add_tag_to_event(
    event_id: UUID,
    tag_data: EventTagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a tag to an event.

    - **event_id**: UUID of the event
    - **tag_id**: UUID of the tag to add
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    event_tag = TagService.add_tag_to_event(
        db=db,
        event_id=event_id,
        tag_id=tag_data.tag_id,
        business_id=current_user.business_id,
        user_id=current_user.id
    )

    if not event_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found or does not belong to your business"
        )

    return EventTagResponse.model_validate(event_tag)


@router.delete("/events/{event_id}/tags/{tag_id}", response_model=MessageResponse)
def remove_tag_from_event(
    event_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from an event.

    - **event_id**: UUID of the event
    - **tag_id**: UUID of the tag to remove
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    removed = TagService.remove_tag_from_event(db, event_id, tag_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag assignment not found"
        )

    return MessageResponse(message="Tag removed from event successfully")


@router.get("/events/{event_id}/tags", response_model=list[TagResponse])
def get_event_tags(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags assigned to an event.

    - **event_id**: UUID of the event
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    tags = TagService.get_event_tags(db, event_id)
    return [TagResponse.model_validate(tag) for tag in tags]
