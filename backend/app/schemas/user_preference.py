"""Pydantic schemas for User Preferences."""

from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class UserPreferenceBase(BaseModel):
    """Base schema for user preferences."""
    notification_enabled: bool = Field(True, description="Enable in-app notifications")
    email_notifications_enabled: bool = Field(True, description="Enable email notifications")
    relevance_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum relevance score for notifications")
    notification_categories: Optional[List[str]] = Field(None, description="Categories to monitor (null = all)")
    notification_frequency: str = Field("instant", description="Notification frequency: instant, daily, weekly")
    assigned_clients_only: bool = Field(False, description="Only notify for assigned clients")
    digest_time: Optional[time] = Field(None, description="Time of day for digests (HH:MM:SS)")
    digest_day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week for weekly digests (0=Monday)")

    @validator('notification_frequency')
    def validate_frequency(cls, v):
        """Validate notification frequency."""
        allowed = ['instant', 'daily', 'weekly']
        if v not in allowed:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed)}")
        return v

    @validator('digest_time')
    def validate_digest_time(cls, v, values):
        """Validate digest time is provided when frequency is not instant."""
        frequency = values.get('notification_frequency')
        if frequency in ['daily', 'weekly'] and v is None:
            raise ValueError("digest_time is required when notification_frequency is daily or weekly")
        return v

    @validator('digest_day_of_week')
    def validate_digest_day(cls, v, values):
        """Validate digest day is provided for weekly frequency."""
        frequency = values.get('notification_frequency')
        if frequency == 'weekly' and v is None:
            raise ValueError("digest_day_of_week is required when notification_frequency is weekly")
        return v


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""
    user_id: int
    business_id: UUID


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""
    notification_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    relevance_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    notification_categories: Optional[List[str]] = None
    notification_frequency: Optional[str] = None
    assigned_clients_only: Optional[bool] = None
    digest_time: Optional[time] = None
    digest_day_of_week: Optional[int] = Field(None, ge=0, le=6)

    @validator('notification_frequency')
    def validate_frequency(cls, v):
        """Validate notification frequency."""
        if v is not None:
            allowed = ['instant', 'daily', 'weekly']
            if v not in allowed:
                raise ValueError(f"Frequency must be one of: {', '.join(allowed)}")
        return v


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference response."""
    id: UUID
    user_id: int
    business_id: UUID
    created_at: datetime
    updated_at: datetime

    # Override to convert JSON string to list
    notification_categories: Optional[List[str]] = None

    class Config:
        from_attributes = True

    @validator('notification_categories', pre=True)
    def parse_categories(cls, v):
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class UserPreferenceDefaults(BaseModel):
    """Default preference values."""
    notification_enabled: bool = True
    email_notifications_enabled: bool = True
    relevance_threshold: float = 0.7
    notification_categories: Optional[List[str]] = None
    notification_frequency: str = "instant"
    assigned_clients_only: bool = False
    digest_time: Optional[time] = time(9, 0, 0)  # 9:00 AM default
    digest_day_of_week: Optional[int] = 0  # Monday default
