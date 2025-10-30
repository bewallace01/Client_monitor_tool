"""Pydantic schemas for Email Logs."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class EmailLogBase(BaseModel):
    """Base schema for email logs."""
    email_type: str = Field(..., description="Email type: event_notification, digest, alert, system")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., max_length=500, description="Email subject")
    body_preview: Optional[str] = Field(None, description="Preview of email body")


class EmailLogCreate(EmailLogBase):
    """Schema for creating email log."""
    business_id: UUID
    user_id: int
    event_id: Optional[UUID] = None
    job_run_id: Optional[UUID] = None
    provider: str = Field("smtp", description="Email provider")
    status: str = Field("pending", description="Email status")


class EmailLogUpdate(BaseModel):
    """Schema for updating email log."""
    status: Optional[str] = None
    error_message: Optional[str] = None
    provider_message_id: Optional[str] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None


class EmailLogResponse(EmailLogBase):
    """Schema for email log response."""
    id: UUID
    business_id: UUID
    user_id: int
    event_id: Optional[UUID]
    job_run_id: Optional[UUID]
    sent_at: datetime
    status: str
    error_message: Optional[str]
    retry_count: int
    provider: str
    provider_message_id: Optional[str]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmailLogList(BaseModel):
    """Schema for paginated list of email logs."""
    logs: list[EmailLogResponse]
    total: int
    skip: int
    limit: int


class EmailLogListResponse(BaseModel):
    """Schema for paginated list of email logs."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[EmailLogResponse]


class EmailLogStats(BaseModel):
    """Statistics for email logs."""
    total_emails: int
    sent_count: int
    failed_count: int
    pending_count: int
    bounced_count: int
    open_rate: Optional[float] = Field(None, description="Percentage of emails opened")
    click_rate: Optional[float] = Field(None, description="Percentage of emails clicked")
    emails_by_type: dict[str, int]


class EmailResendRequest(BaseModel):
    """Request to resend a failed email."""
    email_log_id: UUID
    force_resend: bool = Field(False, description="Force resend even if not failed")
