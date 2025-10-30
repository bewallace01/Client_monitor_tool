"""Tag Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagBase(BaseModel):
    """Base Tag schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Tag name")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code (e.g., #FF5733)")
    description: Optional[str] = Field(None, max_length=500, description="Tag description")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format."""
        if v:
            if not v.startswith('#'):
                v = f'#{v}'
            if len(v) != 7:
                raise ValueError('Color must be in hex format (#RRGGBB)')
        return v


class TagCreate(TagBase):
    """Schema for creating a new tag."""
    business_id: UUID = Field(..., description="Business/Organization ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "High Priority",
                "color": "#FF5733",
                "description": "High priority clients requiring immediate attention"
            }
        }
    )


class TagUpdate(BaseModel):
    """Schema for updating a tag (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format."""
        if v:
            if not v.startswith('#'):
                v = f'#{v}'
            if len(v) != 7:
                raise ValueError('Color must be in hex format (#RRGGBB)')
        return v


class TagResponse(TagBase):
    """Schema for tag response with all fields."""
    id: UUID
    business_id: UUID
    created_at: datetime
    created_by_user_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "aa0e8400-e29b-41d4-a716-446655440007",
                "business_id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "High Priority",
                "color": "#FF5733",
                "description": "High priority clients requiring immediate attention",
                "created_at": "2025-10-16T10:00:00Z",
                "created_by_user_id": 1
            }
        }
    )


class TagListResponse(BaseModel):
    """Schema for list of tags."""
    total: int
    items: list[TagResponse]

    model_config = ConfigDict(from_attributes=True)


# Client Tag Associations

class ClientTagCreate(BaseModel):
    """Schema for adding a tag to a client."""
    tag_id: UUID = Field(..., description="Tag ID to apply")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag_id": "aa0e8400-e29b-41d4-a716-446655440007"
            }
        }
    )


class ClientTagResponse(BaseModel):
    """Schema for client-tag association response."""
    id: UUID
    client_id: UUID
    tag_id: UUID
    created_at: datetime
    created_by_user_id: Optional[int] = None

    # Include tag details for convenience
    tag: TagResponse

    model_config = ConfigDict(from_attributes=True)


# Event Tag Associations

class EventTagCreate(BaseModel):
    """Schema for adding a tag to an event."""
    tag_id: UUID = Field(..., description="Tag ID to apply")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag_id": "aa0e8400-e29b-41d4-a716-446655440007"
            }
        }
    )


class EventTagResponse(BaseModel):
    """Schema for event-tag association response."""
    id: UUID
    event_id: UUID
    tag_id: UUID
    created_at: datetime
    created_by_user_id: Optional[int] = None

    # Include tag details for convenience
    tag: TagResponse

    model_config = ConfigDict(from_attributes=True)
