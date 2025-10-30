"""API Request Log schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class APIRequestLogResponse(BaseModel):
    """API request log response."""

    id: UUID
    provider: str
    endpoint: Optional[str] = None
    method: str
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    job_run_id: Optional[UUID] = None
    status_code: Optional[int] = None
    success: bool
    response_time_ms: Optional[float] = None
    results_count: int
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIRequestLogList(BaseModel):
    """List of API request logs."""

    items: list[APIRequestLogResponse]
    total: int
    skip: int
    limit: int


class APIUsageStats(BaseModel):
    """API usage statistics."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    total_results: int
    errors_by_type: dict[str, int]
    requests_per_hour: float


class APIUsageByProvider(BaseModel):
    """API usage statistics grouped by provider."""

    provider_stats: dict[str, APIUsageStats]


class APIFailureSummary(BaseModel):
    """Summary of recent API failures."""

    provider: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    client_name: Optional[str] = None
    status_code: Optional[int] = None
    created_at: datetime
