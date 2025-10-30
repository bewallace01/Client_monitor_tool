"""Analytics API endpoints for dashboard and reporting."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.schemas import (
    DashboardSummary,
    TopClientsResponse,
    EventTimelineResponse,
    CategoryAnalytics,
    SentimentAnalytics,
    RelevanceMetrics,
    GrowthMetrics,
    ClientActivityMetrics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard summary with all key metrics for the current user's business.

    Returns comprehensive dashboard metrics including:
    - Client statistics (total, active, by tier, by industry)
    - Event statistics (total, unread, starred, recent) - per-user read/starred counts
    - Category distribution
    - Sentiment analysis
    - Time-based metrics (today, this week, this month)
    - Relevance metrics
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    summary = AnalyticsService.get_dashboard_summary(
        db=db,
        business_id=business_id,
        user_id=current_user.id
    )
    return DashboardSummary(**summary)


@router.get("/clients/top-activity", response_model=TopClientsResponse)
def get_top_clients_by_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of clients to return"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get top clients ranked by event activity for the current user's business.

    Returns clients with the most events in the specified period,
    including activity metrics and last event date. Unread counts are per-user.

    - **limit**: Maximum number of clients to return (1-50, default: 10)
    - **days**: Time period to analyze (1-365 days, default: 30)
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    clients, period = AnalyticsService.get_top_clients_by_activity(
        db=db,
        business_id=business_id,
        user_id=current_user.id,
        limit=limit,
        days=days
    )

    return TopClientsResponse(
        clients=[ClientActivityMetrics(**client) for client in clients],
        period_days=period,
    )


@router.get("/events/timeline", response_model=EventTimelineResponse)
def get_event_timeline(
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    group_by: str = Query("day", description="Grouping: day or week"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get event timeline data for visualization for the current user's business.

    Returns time series data showing event counts over time.

    - **days**: Time period to analyze (1-365 days, default: 30)
    - **group_by**: How to group data - 'day' or 'week' (default: day)
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    timeline, total, start, end = AnalyticsService.get_event_timeline(
        db=db,
        business_id=business_id,
        days=days,
        group_by=group_by
    )

    return EventTimelineResponse(
        timeline=timeline,
        total_events=total,
        period_start=start,
        period_end=end,
    )


@router.get("/events/categories", response_model=CategoryAnalytics)
def get_category_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get event category distribution analytics for the current user's business.

    Returns breakdown of events by category with counts and percentages.
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    distribution, total, unique = AnalyticsService.get_category_analytics(
        db=db,
        business_id=business_id
    )

    return CategoryAnalytics(
        distribution=distribution,
        total_events=total,
        unique_categories=unique,
    )


@router.get("/events/sentiment", response_model=SentimentAnalytics)
def get_sentiment_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sentiment analysis metrics for the current user's business.

    Returns sentiment distribution (positive, neutral, negative) and
    average sentiment score across all events.
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    distribution, total, avg_score = AnalyticsService.get_sentiment_analytics(
        db=db,
        business_id=business_id
    )

    return SentimentAnalytics(
        distribution=distribution,
        total_events=total,
        avg_sentiment_score=avg_score,
    )


@router.get("/events/relevance", response_model=RelevanceMetrics)
def get_relevance_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get relevance score metrics for the current user's business.

    Returns relevance distribution (high/medium/low) and statistics.
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    metrics = AnalyticsService.get_relevance_metrics(
        db=db,
        business_id=business_id
    )
    return RelevanceMetrics(**metrics)


@router.get("/growth", response_model=GrowthMetrics)
def get_growth_metrics(
    period_days: int = Query(7, ge=1, le=90, description="Comparison period in days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get growth metrics and trends for the current user's business.

    Compares current period to previous period for:
    - Event volume (new events)
    - Client growth (new clients)

    Returns trend direction (up/down/stable) and percentage change.

    - **period_days**: Comparison period (1-90 days, default: 7)
    """
    # Get user's business_id (system admins can see all data)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all data (business_id=None), others get their business data
    business_id = None if current_user.is_system_admin else current_user.business_id

    metrics = AnalyticsService.get_growth_metrics(
        db=db,
        business_id=business_id,
        period_days=period_days
    )
    return GrowthMetrics(**metrics)
