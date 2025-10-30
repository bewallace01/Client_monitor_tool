"""Event Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum


class EventCategory(str, Enum):
    """Event category enumeration."""
    FUNDING = "funding"
    ACQUISITION = "acquisition"
    LEADERSHIP = "leadership"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT = "product"
    PRODUCT_LAUNCH = "product_launch"
    PARTNERSHIP = "partnership"
    FINANCIAL = "financial"
    FINANCIAL_RESULTS = "financial_results"
    REGULATORY = "regulatory"
    AWARD = "award"
    NEWS = "news"
    OTHER = "other"


class EventBase(BaseModel):
    """Base Event schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    url: Optional[str] = Field(None, max_length=1000, description="Source URL")
    source: Optional[str] = Field(None, max_length=200, description="Source name (e.g., TechCrunch)")
    source_type: Optional[str] = Field(None, max_length=50, description="Source type (news, social, press_release)")
    category: EventCategory = Field(default=EventCategory.OTHER, description="Event category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Subcategory for more granular classification")
    event_date: datetime = Field(..., description="When the event occurred")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            # Add https:// if no protocol specified
            v = f'https://{v}'
        return v


class EventCreate(EventBase):
    """Schema for creating a new event."""
    business_id: UUID = Field(..., description="Business/Organization ID")
    client_id: UUID = Field(..., description="ID of the client this event belongs to")
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance score (0-1)")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI classification confidence (0-1)")
    content_hash: Optional[str] = Field(None, max_length=64, description="Hash for deduplication")
    duplicate_of_event_id: Optional[UUID] = Field(None, description="If this is a duplicate, ID of original event")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Acme Corp Raises $50M Series B Funding",
                "description": "Acme Corporation announced today that it has raised $50 million in Series B funding...",
                "url": "https://techcrunch.com/2025/10/16/acme-funding",
                "source": "TechCrunch",
                "source_type": "news",
                "category": "funding",
                "subcategory": "series_b",
                "relevance_score": 0.95,
                "sentiment_score": 0.8,
                "confidence_score": 0.92,
                "event_date": "2025-10-16T09:00:00Z"
            }
        }
    )


class EventUpdate(BaseModel):
    """Schema for updating an existing event (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=1000)
    source: Optional[str] = Field(None, max_length=200)
    source_type: Optional[str] = Field(None, max_length=50)
    category: Optional[EventCategory] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    event_date: Optional[datetime] = None
    # Legacy fields (deprecated, use EventUserInteraction instead)
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    user_notes: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_read": True,
                "is_starred": True,
                "user_notes": "Follow up with account owner about partnership opportunity"
            }
        }
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            v = f'https://{v}'
        return v


class EventResponse(EventBase):
    """Schema for event response with all fields including metadata."""
    id: UUID
    business_id: UUID
    client_id: UUID
    relevance_score: float
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
    discovered_at: datetime
    content_hash: Optional[str] = None
    duplicate_of_event_id: Optional[UUID] = None

    # Ownership
    created_by_user_id: Optional[int] = None

    # Soft delete
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    # Legacy fields (deprecated, use EventUserInteraction instead)
    is_read: bool
    is_starred: bool
    user_notes: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Acme Corp Raises $50M Series B Funding",
                "description": "Acme Corporation announced today that it has raised $50 million...",
                "url": "https://techcrunch.com/2025/10/16/acme-funding",
                "source": "TechCrunch",
                "source_type": "news",
                "category": "funding",
                "subcategory": "series_b",
                "relevance_score": 0.95,
                "sentiment_score": 0.8,
                "confidence_score": 0.92,
                "event_date": "2025-10-16T09:00:00Z",
                "discovered_at": "2025-10-16T10:30:00Z",
                "content_hash": "abc123...",
                "duplicate_of_event_id": None,
                "created_by_user_id": 1,
                "is_deleted": False,
                "deleted_at": None,
                "is_read": False,
                "is_starred": False,
                "user_notes": None
            }
        }
    )


class EventWithClient(EventResponse):
    """Event response including client information."""
    client_name: str
    client_domain: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """Schema for paginated list of events."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[EventResponse]

    model_config = ConfigDict(from_attributes=True)


class EventFilters(BaseModel):
    """Query parameters for filtering events."""
    client_id: Optional[UUID] = None
    category: Optional[EventCategory] = None
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    min_relevance: Optional[float] = Field(None, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = Field(None, max_length=200, description="Search in title/description")

    model_config = ConfigDict(from_attributes=True)


class EventStats(BaseModel):
    """Event statistics and metrics."""
    total_events: int
    unread_events: int
    starred_events: int
    events_by_category: dict[str, int]
    events_by_sentiment: dict[str, int]  # positive, neutral, negative
    recent_events_count: int  # Last 7 days

    model_config = ConfigDict(from_attributes=True)


class BulkEventUpdate(BaseModel):
    """Schema for bulk updating multiple events."""
    event_ids: list[UUID] = Field(..., min_length=1, description="List of event IDs to update")
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_ids": [
                    "770e8400-e29b-41d4-a716-446655440002",
                    "770e8400-e29b-41d4-a716-446655440003",
                    "770e8400-e29b-41d4-a716-446655440004"
                ],
                "is_read": True
            }
        }
    )
