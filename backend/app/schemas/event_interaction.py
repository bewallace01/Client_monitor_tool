"""EventUserInteraction Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class EventInteractionBase(BaseModel):
    """Base EventUserInteraction schema with common fields."""
    is_read: bool = Field(default=False, description="Whether the user has read this event")
    is_starred: bool = Field(default=False, description="Whether the user has starred this event")
    user_notes: Optional[str] = Field(None, description="User's private notes about this event")


class EventInteractionCreate(EventInteractionBase):
    """Schema for creating a new event user interaction."""
    event_id: UUID = Field(..., description="Event ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "770e8400-e29b-41d4-a716-446655440002",
                "is_read": False,
                "is_starred": False,
                "user_notes": None
            }
        }
    )


class EventInteractionUpdate(BaseModel):
    """Schema for updating an event user interaction (all fields optional)."""
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


class EventInteractionResponse(EventInteractionBase):
    """Schema for event user interaction response with all fields including metadata."""
    id: UUID
    event_id: UUID
    user_id: int
    read_at: Optional[datetime] = None
    starred_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440005",
                "event_id": "770e8400-e29b-41d4-a716-446655440002",
                "user_id": 1,
                "is_read": True,
                "read_at": "2025-10-16T11:00:00Z",
                "is_starred": True,
                "starred_at": "2025-10-16T11:05:00Z",
                "user_notes": "Follow up with account owner",
                "created_at": "2025-10-16T10:30:00Z",
                "updated_at": "2025-10-16T11:05:00Z"
            }
        }
    )


class BulkInteractionUpdate(BaseModel):
    """Schema for bulk updating multiple event interactions."""
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
