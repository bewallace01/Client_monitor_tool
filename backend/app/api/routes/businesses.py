"""Business API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.business_service import BusinessService
from app.schemas import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessListResponse,
    MessageResponse,
)

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("", response_model=BusinessListResponse)
def get_businesses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, domain"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    subscription_tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    sort_by: str = Query("updated_at", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of businesses with filtering, sorting, and pagination.

    System admins only.
    """
    # Only system admins can access business management
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can access business management"
        )

    businesses, total = BusinessService.get_businesses(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        industry=industry,
        is_active=is_active,
        subscription_tier=subscription_tier,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return BusinessListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[BusinessResponse.model_validate(business) for business in businesses],
    )


@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a single business by UUID."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can access business management"
        )

    business = BusinessService.get_business(db, business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )
    return BusinessResponse.model_validate(business)


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_business(
    business: BusinessCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new business. System admins only."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can create businesses"
        )

    # Check if business with same name already exists
    existing = BusinessService.get_business_by_name(db, business.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Business with name '{business.name}' already exists",
        )

    db_business = BusinessService.create_business(
        db=db,
        business=business,
        user_id=current_user.id
    )
    return BusinessResponse.model_validate(db_business)


@router.put("/{business_id}", response_model=BusinessResponse)
def update_business(
    business_id: UUID,
    business_update: BusinessUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing business. System admins only."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can update businesses"
        )

    db_business = BusinessService.update_business(
        db=db,
        business_id=business_id,
        business_update=business_update,
        user_id=current_user.id
    )
    if not db_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )
    return BusinessResponse.model_validate(db_business)


@router.delete("/{business_id}", response_model=MessageResponse)
def delete_business(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a business (permanent). System admins only."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can delete businesses"
        )

    deleted = BusinessService.delete_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )

    return MessageResponse(message=f"Business {business_id} permanently deleted successfully")


@router.post("/{business_id}/activate", response_model=BusinessResponse)
def activate_business(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate a business. System admins only."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can activate businesses"
        )

    db_business = BusinessService.activate_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id
    )
    if not db_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )
    return BusinessResponse.model_validate(db_business)


@router.post("/{business_id}/deactivate", response_model=BusinessResponse)
def deactivate_business(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate a business. System admins only."""
    if current_user.role != 'system_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can deactivate businesses"
        )

    db_business = BusinessService.deactivate_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id
    )
    if not db_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id {business_id} not found",
        )
    return BusinessResponse.model_validate(db_business)
