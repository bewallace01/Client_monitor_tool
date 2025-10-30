"""Analytics Pydantic schemas for dashboard and reporting."""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value: int = Field(..., description="Value for this date")

    model_config = ConfigDict(from_attributes=True)


class CategoryDistribution(BaseModel):
    """Distribution data for a category."""
    category: str
    count: int
    percentage: float = Field(..., ge=0.0, le=100.0)

    model_config = ConfigDict(from_attributes=True)


class SentimentDistribution(BaseModel):
    """Sentiment distribution metrics."""
    positive: int = Field(..., ge=0)
    neutral: int = Field(..., ge=0)
    negative: int = Field(..., ge=0)
    positive_percentage: float = Field(..., ge=0.0, le=100.0)
    neutral_percentage: float = Field(..., ge=0.0, le=100.0)
    negative_percentage: float = Field(..., ge=0.0, le=100.0)

    model_config = ConfigDict(from_attributes=True)


class ClientActivityMetrics(BaseModel):
    """Client activity metrics."""
    client_id: int
    client_name: str
    total_events: int
    unread_events: int
    recent_events: int  # Last 7 days
    last_event_date: Optional[datetime] = None
    avg_relevance_score: float = Field(..., ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class TopClientsResponse(BaseModel):
    """Response for top clients by activity."""
    clients: List[ClientActivityMetrics]
    period_days: int

    model_config = ConfigDict(from_attributes=True)


class EventTimelineResponse(BaseModel):
    """Event timeline data."""
    timeline: List[TimeSeriesDataPoint]
    total_events: int
    period_start: str
    period_end: str

    model_config = ConfigDict(from_attributes=True)


class CategoryAnalytics(BaseModel):
    """Category distribution analytics."""
    distribution: List[CategoryDistribution]
    total_events: int
    unique_categories: int

    model_config = ConfigDict(from_attributes=True)


class SentimentAnalytics(BaseModel):
    """Sentiment analysis metrics."""
    distribution: SentimentDistribution
    total_events: int
    avg_sentiment_score: float = Field(..., ge=-1.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class RelevanceMetrics(BaseModel):
    """Relevance score metrics."""
    avg_score: float = Field(..., ge=0.0, le=1.0)
    high_relevance_count: int = Field(..., description="Events with score >= 0.7")
    medium_relevance_count: int = Field(..., description="Events with score 0.4-0.7")
    low_relevance_count: int = Field(..., description="Events with score < 0.4")
    high_relevance_percentage: float = Field(..., ge=0.0, le=100.0)

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    """Complete dashboard summary with all key metrics."""
    # Client metrics
    total_clients: int
    active_clients: int
    clients_by_tier: Dict[str, int]
    clients_by_industry: Dict[str, int]

    # Event metrics
    total_events: int
    unread_events: int
    starred_events: int
    recent_events: int  # Last 7 days

    # Activity metrics
    events_by_category: Dict[str, int]
    sentiment_distribution: SentimentDistribution

    # Time-based metrics
    events_this_week: int
    events_this_month: int
    events_today: int

    # Quality metrics
    avg_relevance_score: float = Field(..., ge=0.0, le=1.0)
    high_relevance_events: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "total_clients": 43,
                "active_clients": 40,
                "clients_by_tier": {"Enterprise": 15, "Mid-Market": 20},
                "clients_by_industry": {"Technology": 13, "Finance": 8},
                "total_events": 1557,
                "unread_events": 1539,
                "starred_events": 1,
                "recent_events": 1540,
                "events_by_category": {"funding": 175, "acquisition": 120},
                "sentiment_distribution": {
                    "positive": 914,
                    "neutral": 579,
                    "negative": 0,
                    "positive_percentage": 58.7,
                    "neutral_percentage": 37.2,
                    "negative_percentage": 0.0
                },
                "events_this_week": 250,
                "events_this_month": 1200,
                "events_today": 45,
                "avg_relevance_score": 0.85,
                "high_relevance_events": 1400
            }
        }
    )


class TrendData(BaseModel):
    """Trend data with growth metrics."""
    current_value: int
    previous_value: int
    change: int
    change_percentage: float
    trend: str = Field(..., description="up, down, or stable")

    model_config = ConfigDict(from_attributes=True)


class GrowthMetrics(BaseModel):
    """Growth metrics over time periods."""
    events_trend: TrendData
    clients_trend: TrendData
    period: str = Field(..., description="Comparison period (e.g., 'last_7_days')")

    model_config = ConfigDict(from_attributes=True)
