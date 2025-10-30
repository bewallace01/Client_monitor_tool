"""Client API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.client_service import ClientService
from app.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    ClientStats,
    MessageResponse,
)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=ClientListResponse)
def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, domain, description"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    sort_by: str = Query("updated_at", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of clients with filtering, sorting, and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 50, max: 100)
    - **search**: Search term for name, domain, description, keywords
    - **industry**: Filter by industry
    - **is_active**: Filter by active status
    - **tier**: Filter by tier (Enterprise, Mid-Market, etc.)
    - **sort_by**: Field to sort by (default: updated_at)
    - **sort_desc**: Sort descending if true (default: true)
    """
    # Get user's business_id (system admins can see all clients)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all clients (business_id=None), others get their business clients
    business_id = None if current_user.is_system_admin else current_user.business_id

    clients, total = ClientService.get_clients(
        db=db,
        business_id=business_id,
        skip=skip,
        limit=limit,
        search=search,
        industry=industry,
        is_active=is_active,
        tier=tier,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return ClientListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[ClientResponse.model_validate(client) for client in clients],
    )


@router.get("/stats", response_model=ClientStats)
def get_client_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get client statistics.

    Returns counts and distributions of clients.
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    stats = ClientService.get_client_stats(db, business_id)
    return ClientStats(**stats)


@router.get("/industries", response_model=list[str])
def get_industries(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all unique industries."""
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    return ClientService.get_all_industries(db, business_id)


@router.get("/tiers", response_model=list[str])
def get_tiers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all unique tiers."""
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    return ClientService.get_all_tiers(db, business_id)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single client by ID.

    - **client_id**: The UUID of the client to retrieve
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    client = ClientService.get_client(db, client_id, business_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found",
        )
    return ClientResponse.model_validate(client)


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new client.

    - **name**: Client name (required)
    - **domain**: Client domain/website
    - **industry**: Industry sector
    - **description**: Client description
    - **search_keywords**: Comma-separated search keywords
    - **monitoring_frequency**: How often to monitor (daily, weekly, etc.)
    - **is_active**: Whether monitoring is active (default: true)
    - **tier**: Client tier (Enterprise, SMB, etc.)
    - **notes**: Internal notes
    """
    # Non-system admins must have a business_id
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # Use user's business_id (required for creating a client)
    business_id = current_user.business_id

    # System admins must have a business_id to create a client
    if not business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="business_id is required to create a client"
        )

    # Check if client with same name already exists
    existing = ClientService.get_client_by_name(db, client.name, business_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with name '{client.name}' already exists",
        )

    db_client = ClientService.create_client(
        db=db,
        client=client,
        business_id=business_id,
        user_id=current_user.id
    )
    return ClientResponse.model_validate(db_client)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID,
    client_update: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing client.

    - **client_id**: The UUID of the client to update

    All fields are optional. Only provided fields will be updated.
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    db_client = ClientService.update_client(
        db=db,
        client_id=client_id,
        business_id=business_id,
        client_update=client_update,
        user_id=current_user.id
    )
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found",
        )
    return ClientResponse.model_validate(db_client)


@router.delete("/{client_id}", response_model=MessageResponse)
def delete_client(
    client_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a client (soft delete by default).

    - **client_id**: The UUID of the client to delete
    - **hard_delete**: If true, permanently delete; if false, soft delete (default)

    Soft delete preserves data and allows restoration. Hard delete is permanent.
    """
    # System admins can delete any client, others need business_id
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    deleted = ClientService.delete_client(
        db=db,
        client_id=client_id,
        business_id=business_id,
        user_id=current_user.id,
        hard_delete=hard_delete,
        is_system_admin=current_user.is_system_admin
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found",
        )

    delete_type = "permanently deleted" if hard_delete else "deleted"
    return MessageResponse(message=f"Client {client_id} {delete_type} successfully")


@router.post("/{client_id}/restore", response_model=ClientResponse)
def restore_client(
    client_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Restore a soft-deleted client.

    - **client_id**: The UUID of the client to restore
    """
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id

    db_client = ClientService.restore_client(
        db=db,
        client_id=client_id,
        business_id=business_id,
        user_id=current_user.id
    )
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deleted client with id {client_id} not found",
        )
    return ClientResponse.model_validate(db_client)
