"""
API Configuration Routes
CRUD operations and testing for API configurations
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.api_config import (
    APIConfigCreate,
    APIConfigUpdate,
    APIConfigResponse,
    APIConfigTestResponse,
    APIUsageStats,
    APIProviderInfo,
    AVAILABLE_PROVIDERS,
)
from app.services.api_config_service import APIConfigService
from app.services.api_tester import APITester


router = APIRouter()


def check_business_access(current_user: User, business_id: UUID) -> None:
    """Check if user has access to the business"""
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return  # System admin can access any business

    if current_user.business_id != business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this business"
        )


@router.get("/providers", response_model=List[APIProviderInfo])
async def list_available_providers():
    """
    Get list of available API providers (public endpoint - no auth required)
    """
    return AVAILABLE_PROVIDERS


@router.get("", response_model=List[APIConfigResponse])
async def list_api_configs(
    business_id: UUID = Query(..., description="Business ID"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of API configurations for a business

    - **business_id**: Business UUID
    - **provider**: Optional provider filter
    - **is_active**: Optional active status filter
    """
    check_business_access(current_user, business_id)

    configs, total = APIConfigService.get_api_configs(
        db=db,
        business_id=business_id,
        skip=skip,
        limit=limit,
        provider=provider,
        is_active=is_active
    )

    # Convert to response schema (masks sensitive data)
    return [config.to_dict(include_sensitive=False) for config in configs]


@router.get("/{config_id}", response_model=APIConfigResponse)
async def get_api_config(
    config_id: UUID,
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific API configuration

    - **config_id**: API Configuration UUID
    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API configuration not found"
        )

    return config.to_dict(include_sensitive=False)


@router.post("", response_model=APIConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_api_config(
    config_create: APIConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new API configuration

    - **business_id**: Business UUID
    - **provider**: API provider (newsapi, openai, google_search, etc.)
    - **api_key**: API key (will be encrypted)
    - **api_secret**: Optional API secret (will be encrypted)
    """
    check_business_access(current_user, config_create.business_id)

    try:
        config = APIConfigService.create_api_config(
            db=db,
            config_create=config_create,
            user_id=current_user.id
        )
        return config.to_dict(include_sensitive=False)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API configuration: {str(e)}"
        )


@router.put("/{config_id}", response_model=APIConfigResponse)
async def update_api_config(
    config_id: UUID,
    config_update: APIConfigUpdate,
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing API configuration

    - **config_id**: API Configuration UUID
    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    config = APIConfigService.update_api_config(
        db=db,
        config_id=config_id,
        business_id=business_id,
        config_update=config_update,
        user_id=current_user.id
    )

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API configuration not found"
        )

    return config.to_dict(include_sensitive=False)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_config(
    config_id: UUID,
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an API configuration

    - **config_id**: API Configuration UUID
    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    # Only business admin or system admin can delete
    if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.BUSINESS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete API configurations"
        )

    success = APIConfigService.delete_api_config(db, config_id, business_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API configuration not found"
        )


@router.post("/{config_id}/test", response_model=APIConfigTestResponse)
async def test_api_connection(
    config_id: UUID,
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test API connection for a configuration

    - **config_id**: API Configuration UUID
    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    config = APIConfigService.get_api_config_by_id(db, config_id, business_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API configuration not found"
        )

    result = await APITester.test_connection(db, config)
    return result


@router.get("/usage/stats", response_model=List[APIUsageStats])
async def get_usage_stats(
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage statistics for all API configurations

    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    stats = APIConfigService.get_usage_stats(db, business_id)
    return stats


@router.post("/{config_id}/usage", status_code=status.HTTP_204_NO_CONTENT)
async def record_api_usage(
    config_id: UUID,
    business_id: UUID = Query(..., description="Business ID"),
    tokens_used: int = Query(1, ge=1, description="Number of tokens used"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record API usage (internal endpoint)

    - **config_id**: API Configuration UUID
    - **business_id**: Business UUID
    - **tokens_used**: Number of tokens/requests used
    """
    check_business_access(current_user, business_id)

    config = APIConfigService.record_api_usage(
        db=db,
        config_id=config_id,
        business_id=business_id,
        tokens_used=tokens_used
    )

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API configuration not found"
        )


@router.post("/usage/reset/monthly", status_code=status.HTTP_200_OK)
async def reset_monthly_usage(
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset monthly usage counters (admin only)

    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    # Only admins can reset usage
    if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.BUSINESS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset usage counters"
        )

    count = APIConfigService.reset_monthly_usage(db, business_id)
    return {"message": f"Reset usage for {count} configurations"}


@router.post("/usage/reset/hourly", status_code=status.HTTP_200_OK)
async def reset_hourly_usage(
    business_id: UUID = Query(..., description="Business ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset hourly usage counters (admin only)

    - **business_id**: Business UUID
    """
    check_business_access(current_user, business_id)

    # Only admins can reset usage
    if current_user.role not in [UserRole.SYSTEM_ADMIN, UserRole.BUSINESS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset usage counters"
        )

    count = APIConfigService.reset_hourly_usage(db, business_id)
    return {"message": f"Reset hourly usage for {count} configurations"}
