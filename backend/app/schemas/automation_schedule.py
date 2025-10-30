"""Pydantic schemas for Automation Schedules."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AutomationScheduleBase(BaseModel):
    """Base schema for automation schedules."""
    name: str = Field(..., max_length=200, description="User-friendly schedule name")
    description: Optional[str] = Field(None, description="Schedule description")
    job_type: str = Field(..., description="Job type: client_monitoring, search_only, notification_digest")
    client_ids: Optional[List[UUID]] = Field(None, description="Client IDs to monitor (null = all)")
    schedule_type: str = Field(..., description="Schedule type: manual, hourly, daily, weekly, monthly, custom")
    cron_expression: Optional[str] = Field(None, description="Cron expression for custom schedules")
    hour_of_day: Optional[int] = Field(None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month (1-31)")
    is_active: bool = Field(True, description="Whether schedule is active")

    @validator('job_type')
    def validate_job_type(cls, v):
        """Validate job type."""
        allowed = ['client_monitoring', 'search_only', 'notification_digest']
        if v not in allowed:
            raise ValueError(f"Job type must be one of: {', '.join(allowed)}")
        return v

    @validator('schedule_type')
    def validate_schedule_type(cls, v):
        """Validate schedule type."""
        allowed = ['manual', 'hourly', 'daily', 'weekly', 'monthly', 'custom']
        if v not in allowed:
            raise ValueError(f"Schedule type must be one of: {', '.join(allowed)}")
        return v

    @validator('cron_expression')
    def validate_cron(cls, v, values):
        """Validate cron expression for custom schedules."""
        schedule_type = values.get('schedule_type')
        if schedule_type == 'custom' and not v:
            raise ValueError("cron_expression is required when schedule_type is custom")
        return v

    @validator('hour_of_day')
    def validate_hour(cls, v, values):
        """Validate hour is provided for daily/weekly schedules."""
        schedule_type = values.get('schedule_type')
        if schedule_type in ['daily', 'weekly'] and v is None:
            raise ValueError(f"hour_of_day is required when schedule_type is {schedule_type}")
        return v

    @validator('day_of_week')
    def validate_day_of_week(cls, v, values):
        """Validate day of week for weekly schedules."""
        schedule_type = values.get('schedule_type')
        if schedule_type == 'weekly' and v is None:
            raise ValueError("day_of_week is required when schedule_type is weekly")
        return v

    @validator('day_of_month')
    def validate_day_of_month(cls, v, values):
        """Validate day of month for monthly schedules."""
        schedule_type = values.get('schedule_type')
        if schedule_type == 'monthly' and v is None:
            raise ValueError("day_of_month is required when schedule_type is monthly")
        return v


class AutomationScheduleCreate(AutomationScheduleBase):
    """Schema for creating automation schedule."""
    business_id: UUID
    created_by_user_id: int


class AutomationScheduleUpdate(BaseModel):
    """Schema for updating automation schedule."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    job_type: Optional[str] = None
    client_ids: Optional[List[UUID]] = None
    schedule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    hour_of_day: Optional[int] = Field(None, ge=0, le=23)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    is_active: Optional[bool] = None

    @validator('job_type')
    def validate_job_type(cls, v):
        """Validate job type."""
        if v is not None:
            allowed = ['client_monitoring', 'search_only', 'notification_digest']
            if v not in allowed:
                raise ValueError(f"Job type must be one of: {', '.join(allowed)}")
        return v

    @validator('schedule_type')
    def validate_schedule_type(cls, v):
        """Validate schedule type."""
        if v is not None:
            allowed = ['manual', 'hourly', 'daily', 'weekly', 'monthly', 'custom']
            if v not in allowed:
                raise ValueError(f"Schedule type must be one of: {', '.join(allowed)}")
        return v


class AutomationScheduleResponse(AutomationScheduleBase):
    """Schema for automation schedule response."""
    id: UUID
    business_id: UUID
    created_by_user_id: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_run_status: Optional[str]
    last_run_job_id: Optional[UUID]
    consecutive_failures: int
    last_error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Override to convert JSON string to list
    client_ids: Optional[List[UUID]] = None

    class Config:
        from_attributes = True

    @validator('client_ids', pre=True)
    def parse_client_ids(cls, v):
        """Parse JSON string to list if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            import json
            try:
                parsed = json.loads(v)
                # Convert string UUIDs to UUID objects
                return [UUID(cid) if isinstance(cid, str) else cid for cid in parsed]
            except (json.JSONDecodeError, ValueError):
                return None
        return v


class AutomationScheduleList(BaseModel):
    """Schema for paginated list of automation schedules."""
    items: list[AutomationScheduleResponse]
    total: int
    skip: int
    limit: int


class AutomationScheduleListResponse(BaseModel):
    """Schema for paginated list of automation schedules."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[AutomationScheduleResponse]


class AutomationScheduleStats(BaseModel):
    """Statistics for automation schedules."""
    total_schedules: int
    active_schedules: int
    inactive_schedules: int
    schedules_by_type: dict[str, int]
    schedules_with_failures: int


class ScheduleTypeInfo(BaseModel):
    """Information about a schedule type."""
    type: str
    display_name: str
    description: str
    requires_cron: bool
    requires_hour: bool
    requires_day_of_week: bool
    requires_day_of_month: bool


class JobTypeInfo(BaseModel):
    """Information about a job type."""
    type: str
    display_name: str
    description: str
    required_apis: List[str]
    optional_apis: List[str]
