"""Pydantic schemas for Event Raw Data."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EventRawDataBase(BaseModel):
    """Base schema for event raw data."""
    source_api: str = Field(..., description="API source: google_search, serper, newsapi, mock")
    search_query: str = Field(..., description="Search query used")
    raw_content: str = Field(..., description="Raw JSON response from API")
    content_hash: Optional[str] = Field(None, description="Hash for deduplication")


class EventRawDataCreate(EventRawDataBase):
    """Schema for creating event raw data."""
    business_id: UUID
    client_id: UUID
    job_run_id: Optional[UUID] = None


class EventRawDataUpdate(BaseModel):
    """Schema for updating event raw data."""
    is_processed: Optional[bool] = None
    processed_at: Optional[datetime] = None
    processed_into_event_id: Optional[UUID] = None
    processing_error: Optional[str] = None


class EventRawDataResponse(EventRawDataBase):
    """Schema for event raw data response."""
    id: UUID
    business_id: UUID
    client_id: UUID
    job_run_id: Optional[UUID]
    is_processed: bool
    processed_at: Optional[datetime]
    processed_into_event_id: Optional[UUID]
    processing_error: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EventRawDataListResponse(BaseModel):
    """Schema for paginated list of event raw data."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[EventRawDataResponse]


class EventRawDataStats(BaseModel):
    """Statistics for event raw data."""
    total_raw_data: int
    unprocessed_count: int
    processed_count: int
    failed_count: int
    by_source_api: dict[str, int]
