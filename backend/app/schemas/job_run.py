"""JobRun Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class JobStatus(str, Enum):
    """Job execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRunBase(BaseModel):
    """Base JobRun schema with common fields."""
    job_type: str = Field(..., min_length=1, max_length=100, description="Job type")


class JobRunCreate(JobRunBase):
    """Schema for creating a new job run."""
    job_id: str = Field(..., min_length=1, max_length=100, description="Unique job execution ID")
    business_id: Optional[UUID] = Field(default=None, description="Business ID for multi-tenancy")
    status: Optional[JobStatus] = Field(default=JobStatus.PENDING, description="Job status")
    started_at: Optional[datetime] = Field(default=None, description="Job start time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")
    events_found: Optional[int] = Field(default=0, description="Number of events found")
    events_new: Optional[int] = Field(default=0, description="Number of new events created")
    clients_processed: Optional[int] = Field(default=0, description="Number of clients processed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    job_metadata: Optional[str] = Field(None, description="JSON metadata about the job")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "daily-scan-2025-10-16-10-30",
                "job_type": "daily_client_scan",
                "started_at": "2025-10-16T10:30:00Z",
                "status": "pending",
                "job_metadata": "{\"clients_scanned\": 50, \"api_used\": \"news_api\"}"
            }
        }
    )


class JobRunUpdate(BaseModel):
    """Schema for updating a job run (typically to mark completion)."""
    completed_at: Optional[datetime] = None
    status: Optional[JobStatus] = None
    events_found: Optional[int] = None
    events_new: Optional[int] = None
    clients_processed: Optional[int] = None
    error_message: Optional[str] = None
    job_metadata: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "end_time": "2025-10-16T10:45:00Z",
                "status": "completed",
                "results_summary": "Scanned 50 clients, found 23 new events"
            }
        }
    )


class JobRunResponse(JobRunBase):
    """Schema for job run response with all fields."""
    id: UUID
    job_id: str
    business_id: Optional[UUID] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    events_found: int
    events_new: int
    clients_processed: int
    error_message: Optional[str] = None
    job_metadata: Optional[str] = None
    duration_seconds: Optional[float] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "74a6f895-2fcb-448f-870c-416ad3d0aac2",
                "job_id": "daily-scan-2025-10-16-10-30",
                "job_type": "daily_client_scan",
                "started_at": "2025-10-16T10:30:00Z",
                "completed_at": "2025-10-16T10:45:00Z",
                "status": "completed",
                "events_found": 23,
                "events_new": 10,
                "clients_processed": 50,
                "error_message": None,
                "job_metadata": "{\"clients_scanned\": 50, \"api_used\": \"news_api\"}",
                "duration_seconds": 900.0
            }
        }
    )


class JobRunListResponse(BaseModel):
    """Schema for paginated list of job runs."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[JobRunResponse]

    model_config = ConfigDict(from_attributes=True)


class JobRunFilters(BaseModel):
    """Query parameters for filtering job runs."""
    job_type: Optional[str] = Field(None, max_length=100)
    status: Optional[JobStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobRunStats(BaseModel):
    """Job run statistics and metrics."""
    total_runs: int
    completed_runs: int
    failed_runs: int
    running_runs: int
    pending_runs: int
    average_duration_seconds: Optional[float] = None
    runs_by_job_type: dict[str, int]
    recent_runs: list[JobRunResponse]  # Last 10 runs

    model_config = ConfigDict(from_attributes=True)


class JobScheduleInfo(BaseModel):
    """Information about a scheduled job."""
    job_type: str
    schedule: str  # e.g., "0 */6 * * *" (cron format)
    enabled: bool
    next_run: Optional[datetime] = None
    last_run: Optional[JobRunResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "job_type": "daily_client_scan",
                "schedule": "0 0 * * *",
                "enabled": True,
                "next_run": "2025-10-17T00:00:00Z",
                "last_run": {
                    "id": "74a6f895-2fcb-448f-870c-416ad3d0aac2",
                    "job_id": "daily-scan-2025-10-16-00-00",
                    "job_type": "daily_client_scan",
                    "started_at": "2025-10-16T00:00:00Z",
                    "completed_at": "2025-10-16T00:15:00Z",
                    "status": "completed",
                    "events_found": 23,
                    "events_new": 10,
                    "clients_processed": 50,
                    "error_message": None,
                    "job_metadata": None,
                    "duration_seconds": 900.0
                }
            }
        }
    )


class TriggerJobRequest(BaseModel):
    """Request to manually trigger a job."""
    job_type: str = Field(..., min_length=1, max_length=100, description="Type of job to trigger")
    override_params: Optional[dict] = Field(None, description="Parameters to override for this run")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_type": "daily_client_scan",
                "override_params": {
                    "client_ids": [1, 2, 3],
                    "force_refresh": True
                }
            }
        }
    )
