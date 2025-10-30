"""API Health and Circuit Breaker endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.circuit_breaker_service import CircuitBreakerService
from app.services.api_request_logger import APIRequestLogger
from app.schemas.circuit_breaker import (
    CircuitBreakerStatus,
    CircuitBreakerList,
    CircuitBreakerManualControl
)
from app.schemas.api_request_log import (
    APIRequestLogResponse,
    APIRequestLogList,
    APIUsageStats,
    APIUsageByProvider,
    APIFailureSummary
)

router = APIRouter(prefix="/api-health", tags=["api-health"])


@router.get("/circuit-breakers", response_model=CircuitBreakerList)
def get_circuit_breakers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all circuit breaker statuses for the business."""
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    statuses = CircuitBreakerService.get_all_breaker_statuses(
        db=db,
        business_id=current_user.business_id
    )

    return {
        "items": statuses,
        "total": len(statuses)
    }


@router.get("/circuit-breakers/{api_config_id}", response_model=CircuitBreakerStatus)
def get_circuit_breaker(
    api_config_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get circuit breaker status for a specific API config."""
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    status_dict = CircuitBreakerService.get_breaker_status(
        db=db,
        api_config_id=api_config_id
    )

    if not status_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Circuit breaker not found"
        )

    return status_dict


@router.post("/circuit-breakers/{api_config_id}/control", response_model=CircuitBreakerStatus)
def control_circuit_breaker(
    api_config_id: UUID,
    control: CircuitBreakerManualControl,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually control a circuit breaker (enable, disable, or reset)."""
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    if control.action == "disable":
        if not control.reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reason required when disabling API"
            )
        breaker = CircuitBreakerService.manually_disable(
            db=db,
            api_config_id=api_config_id,
            reason=control.reason,
            user_id=current_user.id
        )
    elif control.action == "enable":
        breaker = CircuitBreakerService.manually_enable(
            db=db,
            api_config_id=api_config_id
        )
    elif control.action == "reset":
        breaker = CircuitBreakerService.reset_breaker(
            db=db,
            api_config_id=api_config_id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'enable', 'disable', or 'reset'"
        )

    if not breaker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Circuit breaker not found"
        )

    status_dict = CircuitBreakerService.get_breaker_status(db=db, api_config_id=api_config_id)
    return status_dict


@router.get("/request-logs", response_model=APIRequestLogList)
def get_request_logs(
    api_config_id: Optional[UUID] = Query(None),
    provider: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    hours_back: int = Query(24, ge=1, le=168),  # Max 1 week
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get API request logs with filtering.

    - **api_config_id**: Filter by API configuration
    - **provider**: Filter by provider (google_search, newsapi, etc.)
    - **success**: Filter by success status
    - **hours_back**: How many hours back to query (default: 24, max: 168)
    - **skip**: Pagination offset
    - **limit**: Max results (default: 100, max: 500)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    logs = APIRequestLogger.get_recent_logs(
        db=db,
        business_id=current_user.business_id,
        api_config_id=api_config_id,
        provider=provider,
        success=success,
        hours_back=hours_back,
        limit=limit
    )

    return {
        "items": logs,
        "total": len(logs),
        "skip": skip,
        "limit": limit
    }


@router.get("/usage-stats", response_model=APIUsageStats)
def get_usage_stats(
    api_config_id: Optional[UUID] = Query(None),
    hours_back: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get API usage statistics.

    - **api_config_id**: Filter by specific API config (optional)
    - **hours_back**: How many hours back to calculate stats (default: 24, max: 168)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    stats = APIRequestLogger.get_usage_stats(
        db=db,
        business_id=current_user.business_id,
        api_config_id=api_config_id,
        hours_back=hours_back
    )

    return stats


@router.get("/usage-by-provider", response_model=APIUsageByProvider)
def get_usage_by_provider(
    hours_back: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get API usage statistics grouped by provider.

    - **hours_back**: How many hours back to calculate stats (default: 24, max: 168)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    provider_stats = APIRequestLogger.get_usage_by_provider(
        db=db,
        business_id=current_user.business_id,
        hours_back=hours_back
    )

    return {"provider_stats": provider_stats}


@router.get("/failures", response_model=list[APIFailureSummary])
def get_failures(
    hours_back: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of recent API failures.

    - **hours_back**: How many hours back to query (default: 24, max: 168)
    """
    if not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    failures = APIRequestLogger.get_failure_summary(
        db=db,
        business_id=current_user.business_id,
        hours_back=hours_back
    )

    return failures
