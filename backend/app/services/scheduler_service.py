"""Scheduler service layer for job run management."""

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.models import JobRun
from app.schemas import JobRunCreate, JobRunUpdate, JobStatus


class SchedulerService:
    """Service for managing scheduled jobs and job runs."""

    @staticmethod
    def get_job_runs(
        db: Session,
        business_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
        job_type: Optional[str] = None,
        status: Optional[JobStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "started_at",
        sort_desc: bool = True,
    ) -> Tuple[List[JobRun], int]:
        """
        Get list of job runs with filtering, sorting, and pagination.

        Args:
            business_id: Filter by business (None for system admins to see all)
            Other parameters for filtering and pagination

        Returns tuple of (job_runs, total_count).
        """
        query = db.query(JobRun)

        # Apply business filter (None means show all for system admins)
        if business_id is not None:
            query = query.filter(JobRun.business_id == business_id)

        # Apply filters
        if job_type:
            query = query.filter(JobRun.job_type == job_type)

        if status:
            query = query.filter(JobRun.status == status.value)

        if start_date:
            query = query.filter(JobRun.started_at >= start_date)

        if end_date:
            query = query.filter(JobRun.started_at <= end_date)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(JobRun, sort_by, JobRun.started_at)
        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        job_runs = query.offset(skip).limit(limit).all()

        return job_runs, total

    @staticmethod
    def get_job_run(db: Session, job_run_id: int) -> Optional[JobRun]:
        """Get a single job run by ID."""
        return db.query(JobRun).filter(JobRun.id == job_run_id).first()

    @staticmethod
    def get_job_run_by_job_id(db: Session, job_id: str) -> Optional[JobRun]:
        """Get a single job run by job_id (UUID)."""
        return db.query(JobRun).filter(JobRun.job_id == job_id).first()

    @staticmethod
    def create_job_run(db: Session, job_run: JobRunCreate) -> JobRun:
        """Create a new job run."""
        db_job_run = JobRun(
            job_id=job_run.job_id,
            job_type=job_run.job_type,
            business_id=job_run.business_id,
            status=job_run.status or JobStatus.PENDING.value,
            started_at=job_run.started_at or datetime.utcnow(),
            completed_at=job_run.completed_at,
            events_found=job_run.events_found or 0,
            events_new=job_run.events_new or 0,
            clients_processed=job_run.clients_processed or 0,
            error_message=job_run.error_message,
            job_metadata=job_run.job_metadata,
        )
        db.add(db_job_run)
        db.commit()
        db.refresh(db_job_run)
        return db_job_run

    @staticmethod
    def update_job_run(
        db: Session, job_run_id: int, job_run_update: JobRunUpdate
    ) -> Optional[JobRun]:
        """Update an existing job run."""
        db_job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not db_job_run:
            return None

        # Update only provided fields
        update_data = job_run_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_job_run, field, value)

        db.commit()
        db.refresh(db_job_run)
        return db_job_run

    @staticmethod
    def delete_job_run(db: Session, job_run_id: int) -> bool:
        """
        Delete a job run.

        Returns True if deleted, False if not found.
        """
        db_job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not db_job_run:
            return False

        db.delete(db_job_run)
        db.commit()
        return True

    @staticmethod
    def get_job_run_stats(db: Session, business_id: Optional[UUID] = None) -> dict:
        """
        Get statistics about job runs.

        Args:
            business_id: Filter by business (None for system admins to see all)
        """
        query = db.query(JobRun)

        # Apply business filter
        if business_id is not None:
            query = query.filter(JobRun.business_id == business_id)

        total_runs = query.count()

        # Count by status
        completed_runs = query.filter(JobRun.status == JobStatus.COMPLETED.value).count()
        failed_runs = query.filter(JobRun.status == JobStatus.FAILED.value).count()
        running_runs = query.filter(JobRun.status == JobStatus.RUNNING.value).count()
        pending_runs = query.filter(JobRun.status == JobStatus.PENDING.value).count()

        # Count by job type
        type_query = db.query(JobRun.job_type, func.count(JobRun.id))
        if business_id is not None:
            type_query = type_query.filter(JobRun.business_id == business_id)
        type_stats = type_query.group_by(JobRun.job_type).all()
        runs_by_job_type = {job_type: count for job_type, count in type_stats}

        # Get recent runs
        recent_query = db.query(JobRun)
        if business_id is not None:
            recent_query = recent_query.filter(JobRun.business_id == business_id)
        recent_runs = recent_query.order_by(JobRun.started_at.desc()).limit(10).all()

        # Calculate average duration (only for completed jobs)
        completed_query = db.query(JobRun).filter(JobRun.status == JobStatus.COMPLETED.value).filter(JobRun.completed_at.isnot(None))
        if business_id is not None:
            completed_query = completed_query.filter(JobRun.business_id == business_id)
        completed_jobs = completed_query.all()

        if completed_jobs:
            total_duration = sum((job.completed_at - job.started_at).total_seconds() for job in completed_jobs)
            average_duration_seconds = total_duration / len(completed_jobs)
        else:
            average_duration_seconds = None

        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "failed_runs": failed_runs,
            "running_runs": running_runs,
            "pending_runs": pending_runs,
            "average_duration_seconds": average_duration_seconds,
            "runs_by_job_type": runs_by_job_type,
            "recent_runs": recent_runs,
        }

    @staticmethod
    def get_recent_job_runs(db: Session, business_id: Optional[UUID] = None, limit: int = 10) -> List[JobRun]:
        """
        Get most recent job runs.

        Args:
            business_id: Filter by business (None for system admins to see all)
            limit: Maximum number of runs to return
        """
        query = db.query(JobRun)
        if business_id is not None:
            query = query.filter(JobRun.business_id == business_id)
        return query.order_by(JobRun.started_at.desc()).limit(limit).all()

    @staticmethod
    def get_active_job_runs(db: Session, business_id: Optional[UUID] = None) -> List[JobRun]:
        """
        Get currently running or pending jobs.

        Args:
            business_id: Filter by business (None for system admins to see all)
        """
        query = db.query(JobRun).filter(
            or_(
                JobRun.status == JobStatus.PENDING.value,
                JobRun.status == JobStatus.RUNNING.value,
            )
        )
        if business_id is not None:
            query = query.filter(JobRun.business_id == business_id)
        return query.order_by(JobRun.started_at.desc()).all()

    @staticmethod
    def mark_job_as_running(db: Session, job_run_id: int) -> Optional[JobRun]:
        """Mark a job as running."""
        db_job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not db_job_run:
            return None

        db_job_run.status = JobStatus.RUNNING.value
        db_job_run.started_at = datetime.utcnow()

        db.commit()
        db.refresh(db_job_run)
        return db_job_run

    @staticmethod
    def mark_job_as_completed(
        db: Session,
        job_run_id: int,
        events_found: int = 0,
        events_new: int = 0,
        clients_processed: int = 0,
    ) -> Optional[JobRun]:
        """Mark a job as completed."""
        db_job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not db_job_run:
            return None

        db_job_run.status = JobStatus.COMPLETED.value
        db_job_run.completed_at = datetime.utcnow()
        db_job_run.events_found = events_found
        db_job_run.events_new = events_new
        db_job_run.clients_processed = clients_processed

        db.commit()
        db.refresh(db_job_run)
        return db_job_run

    @staticmethod
    def mark_job_as_failed(
        db: Session, job_run_id: int, error_message: str
    ) -> Optional[JobRun]:
        """Mark a job as failed."""
        db_job_run = db.query(JobRun).filter(JobRun.id == job_run_id).first()
        if not db_job_run:
            return None

        db_job_run.status = JobStatus.FAILED.value
        db_job_run.completed_at = datetime.utcnow()
        db_job_run.error_message = error_message

        db.commit()
        db.refresh(db_job_run)
        return db_job_run

    @staticmethod
    def get_job_types(db: Session, business_id: Optional[UUID] = None) -> List[str]:
        """
        Get list of all available job types.

        NOTE: Manual job triggering has been moved to the dedicated
        monitoring jobs endpoint (/api/v1/monitoring-jobs/execute).
        This endpoint is kept for backward compatibility but returns
        an empty list as all manual jobs should use the new interface.

        Args:
            business_id: Filter by business (None for system admins to see all)
        """
        # Return empty list - manual job execution moved to monitoring-jobs endpoint
        return []
