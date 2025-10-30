"""Scheduler API endpoints for job management."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid

from app.database.connection import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.scheduler_service import SchedulerService
from app.services.scheduler_integration_service import SchedulerIntegrationService
from app.schemas import (
    JobRunCreate,
    JobRunUpdate,
    JobRunResponse,
    JobRunListResponse,
    JobRunStats,
    JobStatus,
    TriggerJobRequest,
    MessageResponse,
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/jobs", response_model=JobRunListResponse)
def get_job_runs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter jobs after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter jobs before this date"),
    sort_by: str = Query("started_at", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of job runs with filtering, sorting, and pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 50, max: 100)
    - **job_type**: Filter by job type (e.g., 'news_scraper', 'email_digest')
    - **status**: Filter by status (pending, running, completed, failed)
    - **start_date**: Jobs started after this date
    - **end_date**: Jobs started before this date
    - **sort_by**: Field to sort by (default: started_at)
    - **sort_desc**: Sort descending if true (default: true)
    """
    # Get user's business_id (system admins can see all job runs)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all job runs (business_id=None), others get their business job runs
    business_id = None if current_user.is_system_admin else current_user.business_id

    job_runs, total = SchedulerService.get_job_runs(
        db=db,
        business_id=business_id,
        skip=skip,
        limit=limit,
        job_type=job_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    # Calculate pagination info
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    return JobRunListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        items=[JobRunResponse.model_validate(job_run) for job_run in job_runs],
    )


@router.get("/jobs/stats", response_model=JobRunStats)
def get_job_run_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get job run statistics.

    Returns counts, distributions, and metrics about job runs.
    """
    # Get user's business_id (system admins can see all job run stats)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # System admins get all stats (business_id=None), others get their business stats
    business_id = None if current_user.is_system_admin else current_user.business_id

    stats = SchedulerService.get_job_run_stats(db, business_id)
    return JobRunStats(**stats)


@router.get("/jobs/recent")
def get_recent_job_runs(
    limit: int = Query(10, ge=1, le=50, description="Number of recent jobs to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get most recent job runs.

    - **limit**: Number of jobs to return (1-50, default: 10)
    """
    # Get user's business_id (system admins can see all)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    job_runs = SchedulerService.get_recent_job_runs(db, business_id, limit)
    return [JobRunResponse.model_validate(job_run) for job_run in job_runs]


@router.get("/jobs/active")
def get_active_job_runs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get currently active (pending or running) jobs.

    Returns jobs that are currently pending or in progress.
    """
    # Get user's business_id (system admins can see all)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    job_runs = SchedulerService.get_active_job_runs(db, business_id)
    return [JobRunResponse.model_validate(job_run) for job_run in job_runs]


@router.get("/jobs/types", response_model=list[str])
def get_job_types(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all unique job types."""
    # Get user's business_id (system admins can see all)
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    business_id = None if current_user.is_system_admin else current_user.business_id
    return SchedulerService.get_job_types(db, business_id)


@router.get("/jobs/{job_run_id}", response_model=JobRunResponse)
def get_job_run(
    job_run_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single job run by ID.

    - **job_run_id**: The ID of the job run to retrieve
    """
    job_run = SchedulerService.get_job_run(db, job_run_id)
    if not job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return JobRunResponse.model_validate(job_run)


@router.post("/jobs", response_model=JobRunResponse, status_code=status.HTTP_201_CREATED)
def create_job_run(
    job_run: JobRunCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new job run.

    - **job_id**: Unique job identifier (UUID)
    - **job_type**: Type of job (required)
    - **status**: Job status (default: pending)
    - **started_at**: When job started (default: now)
    - **events_found**: Number of events found
    - **events_new**: Number of new events created
    - **clients_processed**: Number of clients processed
    - **job_metadata**: Additional job metadata (JSON)
    """
    db_job_run = SchedulerService.create_job_run(db, job_run)
    return JobRunResponse.model_validate(db_job_run)


@router.put("/jobs/{job_run_id}", response_model=JobRunResponse)
def update_job_run(
    job_run_id: int,
    job_run_update: JobRunUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing job run.

    - **job_run_id**: The ID of the job run to update

    All fields are optional. Only provided fields will be updated.
    """
    db_job_run = SchedulerService.update_job_run(db, job_run_id, job_run_update)
    if not db_job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return JobRunResponse.model_validate(db_job_run)


@router.delete("/jobs/{job_run_id}", response_model=MessageResponse)
def delete_job_run(
    job_run_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a job run.

    - **job_run_id**: The ID of the job run to delete
    """
    deleted = SchedulerService.delete_job_run(db, job_run_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return MessageResponse(message=f"Job run {job_run_id} deleted successfully")


@router.post("/jobs/trigger", response_model=JobRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_job(
    trigger_request: TriggerJobRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a new job run.

    Creates a new job run with pending status. The actual job execution
    should be handled by a background worker.

    - **job_type**: Type of job to trigger (required)
    - **override_params**: Optional parameters for the job
    """
    import json

    # Get user's business_id
    if not current_user.is_system_admin and not current_user.business_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a business"
        )

    # Use user's business_id (or None for system admins if they want system-wide jobs)
    business_id = current_user.business_id

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Convert override_params dict to JSON string for job_metadata
    job_metadata_str = None
    if trigger_request.override_params:
        job_metadata_str = json.dumps(trigger_request.override_params)

    # Create job run with pending status
    job_run_data = JobRunCreate(
        job_id=job_id,
        job_type=trigger_request.job_type,
        status=JobStatus.PENDING,
        started_at=datetime.utcnow(),
        job_metadata=job_metadata_str,
        business_id=business_id,
    )

    db_job_run = SchedulerService.create_job_run(db, job_run_data)

    return JobRunResponse.model_validate(db_job_run)


@router.post("/jobs/{job_run_id}/start", response_model=JobRunResponse)
def start_job(
    job_run_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a job as running.

    Updates job status to 'running' and sets started_at timestamp.

    - **job_run_id**: The ID of the job run to start
    """
    db_job_run = SchedulerService.mark_job_as_running(db, job_run_id)
    if not db_job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return JobRunResponse.model_validate(db_job_run)


@router.post("/jobs/{job_run_id}/complete", response_model=JobRunResponse)
def complete_job(
    job_run_id: int,
    events_found: int = Query(0, ge=0, description="Number of events found"),
    events_new: int = Query(0, ge=0, description="Number of new events created"),
    clients_processed: int = Query(0, ge=0, description="Number of clients processed"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Mark a job as completed.

    Updates job status to 'completed', sets completion timestamp,
    and records metrics.

    - **job_run_id**: The ID of the job run to complete
    - **events_found**: Number of events found
    - **events_new**: Number of new events created
    - **clients_processed**: Number of clients processed
    """
    db_job_run = SchedulerService.mark_job_as_completed(
        db, job_run_id, events_found, events_new, clients_processed
    )
    if not db_job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return JobRunResponse.model_validate(db_job_run)


@router.post("/jobs/{job_run_id}/fail", response_model=JobRunResponse)
def fail_job(
    job_run_id: int,
    error_message: str = Query(..., description="Error message describing the failure"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Mark a job as failed.

    Updates job status to 'failed', sets completion timestamp,
    and records error message.

    - **job_run_id**: The ID of the job run to mark as failed
    - **error_message**: Error message describing what went wrong
    """
    db_job_run = SchedulerService.mark_job_as_failed(db, job_run_id, error_message)
    if not db_job_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job run with id {job_run_id} not found",
        )
    return JobRunResponse.model_validate(db_job_run)


@router.get("/status")
def get_scheduler_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current scheduler status and information.

    Returns whether the scheduler is running, total number of scheduled jobs,
    and details about each scheduled job including next run times.
    """
    try:
        status_info = SchedulerIntegrationService.get_scheduler_status()
        return status_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )
