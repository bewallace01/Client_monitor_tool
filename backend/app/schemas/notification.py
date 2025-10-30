"""Notification Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    """Schema for creating a new notification."""
    business_id: UUID = Field(..., description="Business/Organization ID")
    user_id: int = Field(..., description="Target user ID")
    type: str = Field(..., max_length=50, description="Notification type")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    link_url: Optional[str] = Field(None, max_length=500, description="Optional URL to related resource")
    related_event_id: Optional[UUID] = Field(None, description="Optional related event ID")
    related_client_id: Optional[UUID] = Field(None, description="Optional related client ID")
    priority: str = Field(default="normal", max_length=20, description="Priority level (low, normal, high, urgent)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": 1,
                "type": "high_relevance_event",
                "title": "High Relevance Event Detected",
                "message": "A highly relevant funding event was detected for Acme Corporation",
                "link_url": "/events/770e8400-e29b-41d4-a716-446655440002",
                "related_event_id": "770e8400-e29b-41d4-a716-446655440002",
                "related_client_id": "550e8400-e29b-41d4-a716-446655440000",
                "priority": "high"
            }
        }
    )


class NotificationUpdate(BaseModel):
    """Schema for updating a notification (all fields optional)."""
    is_read: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_read": True
            }
        }
    )


class NotificationResponse(BaseModel):
    """Schema for notification response with all fields."""
    id: UUID
    business_id: UUID
    user_id: int
    type: str
    title: str
    message: str
    link_url: Optional[str] = None
    related_event_id: Optional[UUID] = None
    related_client_id: Optional[UUID] = None
    is_read: bool
    read_at: Optional[datetime] = None
    priority: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "bb0e8400-e29b-41d4-a716-446655440008",
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": 1,
                "type": "high_relevance_event",
                "title": "High Relevance Event Detected",
                "message": "A highly relevant funding event was detected for Acme Corporation",
                "link_url": "/events/770e8400-e29b-41d4-a716-446655440002",
                "related_event_id": "770e8400-e29b-41d4-a716-446655440002",
                "related_client_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_read": False,
                "read_at": None,
                "priority": "high",
                "created_at": "2025-10-16T10:30:00Z"
            }
        }
    )


class NotificationListResponse(BaseModel):
    """Schema for paginated list of notifications."""
    total: int
    unread_count: int
    page: int
    page_size: int
    total_pages: int
    items: list[NotificationResponse]

    model_config = ConfigDict(from_attributes=True)


class NotificationFilters(BaseModel):
    """Query parameters for filtering notifications."""
    is_read: Optional[bool] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BulkNotificationUpdate(BaseModel):
    """Schema for bulk updating multiple notifications."""
    notification_ids: list[UUID] = Field(..., min_length=1, description="List of notification IDs to update")
    is_read: bool = Field(..., description="Mark as read or unread")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_ids": [
                    "bb0e8400-e29b-41d4-a716-446655440008",
                    "bb0e8400-e29b-41d4-a716-446655440009",
                    "bb0e8400-e29b-41d4-a716-446655440010"
                ],
                "is_read": True
            }
        }
    )
