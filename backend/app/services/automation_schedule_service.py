"""Automation schedule service for managing job schedules."""

import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.automation_schedule import AutomationSchedule
from app.schemas.automation_schedule import (
    AutomationScheduleCreate,
    AutomationScheduleUpdate
)

logger = logging.getLogger(__name__)


class AutomationScheduleService:
    """Service for managing automation schedules."""

    @staticmethod
    def create_schedule(
        db: Session,
        schedule_data: AutomationScheduleCreate
    ) -> AutomationSchedule:
        """
        Create new automation schedule.

        Args:
            db: Database session
            schedule_data: AutomationScheduleCreate schema

        Returns:
            Created AutomationSchedule instance
        """
        # Serialize client_ids to JSON
        client_ids_json = None
        if schedule_data.client_ids:
            client_ids_json = json.dumps([str(cid) for cid in schedule_data.client_ids])

        # Calculate next run time
        next_run_at = AutomationScheduleService._calculate_next_run(
            schedule_type=schedule_data.schedule_type,
            hour_of_day=schedule_data.hour_of_day,
            day_of_week=schedule_data.day_of_week,
            day_of_month=schedule_data.day_of_month,
            cron_expression=schedule_data.cron_expression
        )

        schedule = AutomationSchedule(
            business_id=schedule_data.business_id,
            created_by_user_id=schedule_data.created_by_user_id,
            name=schedule_data.name,
            description=schedule_data.description,
            job_type=schedule_data.job_type,
            client_ids=client_ids_json,
            schedule_type=schedule_data.schedule_type,
            cron_expression=schedule_data.cron_expression,
            hour_of_day=schedule_data.hour_of_day,
            day_of_week=schedule_data.day_of_week,
            day_of_month=schedule_data.day_of_month,
            is_active=schedule_data.is_active,
            next_run_at=next_run_at,
            consecutive_failures=0
        )

        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        logger.info(f"Created automation schedule: {schedule.name} (ID: {schedule.id})")
        return schedule

    @staticmethod
    def get_schedule(
        db: Session,
        schedule_id: UUID,
        business_id: Optional[UUID] = None
    ) -> Optional[AutomationSchedule]:
        """Get schedule by ID."""
        query = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        )

        if business_id:
            query = query.filter(AutomationSchedule.business_id == business_id)

        return query.first()

    @staticmethod
    def get_schedules(
        db: Session,
        business_id: UUID,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
        job_type: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_desc: Optional[bool] = False
    ) -> Tuple[List[AutomationSchedule], int]:
        """
        Get schedules for a business with pagination.

        Args:
            db: Database session
            business_id: Business UUID
            skip: Number of records to skip
            limit: Maximum number of records
            is_active: Filter by active status
            job_type: Filter by job type
            sort_by: Field to sort by
            sort_desc: Sort in descending order

        Returns:
            Tuple of (schedules, total_count)
        """
        query = db.query(AutomationSchedule).filter(
            AutomationSchedule.business_id == business_id
        )

        if is_active is not None:
            query = query.filter(AutomationSchedule.is_active == is_active)

        if job_type:
            query = query.filter(AutomationSchedule.job_type == job_type)

        total = query.count()

        # Apply sorting
        sort_column = AutomationSchedule.created_at  # default
        if sort_by and hasattr(AutomationSchedule, sort_by):
            sort_column = getattr(AutomationSchedule, sort_by)

        if sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        schedules = query.offset(skip).limit(limit).all()

        return schedules, total

    @staticmethod
    def update_schedule(
        db: Session,
        schedule_id: UUID,
        updates: AutomationScheduleUpdate,
        business_id: Optional[UUID] = None
    ) -> Optional[AutomationSchedule]:
        """
        Update automation schedule.

        Args:
            db: Database session
            schedule_id: Schedule UUID
            updates: AutomationScheduleUpdate schema
            business_id: Optional business ID for validation

        Returns:
            Updated AutomationSchedule or None
        """
        query = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        )

        if business_id:
            query = query.filter(AutomationSchedule.business_id == business_id)

        schedule = query.first()
        if not schedule:
            return None

        # Update fields
        update_data = updates.model_dump(exclude_unset=True)

        # Handle client_ids serialization
        if "client_ids" in update_data:
            client_ids = update_data["client_ids"]
            if client_ids is not None:
                update_data["client_ids"] = json.dumps([str(cid) for cid in client_ids])

        for field, value in update_data.items():
            setattr(schedule, field, value)

        # Recalculate next run if schedule changed
        if any(k in update_data for k in ["schedule_type", "hour_of_day", "day_of_week", "day_of_month", "cron_expression"]):
            schedule.next_run_at = AutomationScheduleService._calculate_next_run(
                schedule_type=schedule.schedule_type,
                hour_of_day=schedule.hour_of_day,
                day_of_week=schedule.day_of_week,
                day_of_month=schedule.day_of_month,
                cron_expression=schedule.cron_expression
            )

        db.commit()
        db.refresh(schedule)

        logger.info(f"Updated automation schedule: {schedule.name}")
        return schedule

    @staticmethod
    def delete_schedule(
        db: Session,
        schedule_id: UUID,
        business_id: Optional[UUID] = None
    ) -> bool:
        """
        Delete automation schedule.

        Returns:
            True if deleted, False if not found
        """
        query = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        )

        if business_id:
            query = query.filter(AutomationSchedule.business_id == business_id)

        schedule = query.first()
        if not schedule:
            return False

        db.delete(schedule)
        db.commit()

        logger.info(f"Deleted automation schedule: {schedule.name}")
        return True

    @staticmethod
    def activate_schedule(
        db: Session,
        schedule_id: UUID,
        business_id: Optional[UUID] = None
    ) -> Optional[AutomationSchedule]:
        """Activate a schedule."""
        schedule = AutomationScheduleService.get_schedule(db, schedule_id, business_id)
        if not schedule:
            return None

        schedule.activate()

        # Recalculate next run
        schedule.next_run_at = AutomationScheduleService._calculate_next_run(
            schedule_type=schedule.schedule_type,
            hour_of_day=schedule.hour_of_day,
            day_of_week=schedule.day_of_week,
            day_of_month=schedule.day_of_month,
            cron_expression=schedule.cron_expression
        )

        db.commit()
        db.refresh(schedule)

        logger.info(f"Activated schedule: {schedule.name}")
        return schedule

    @staticmethod
    def deactivate_schedule(
        db: Session,
        schedule_id: UUID,
        business_id: Optional[UUID] = None
    ) -> Optional[AutomationSchedule]:
        """Deactivate a schedule."""
        schedule = AutomationScheduleService.get_schedule(db, schedule_id, business_id)
        if not schedule:
            return None

        schedule.deactivate()
        db.commit()
        db.refresh(schedule)

        logger.info(f"Deactivated schedule: {schedule.name}")
        return schedule

    @staticmethod
    def get_due_schedules(db: Session) -> List[AutomationSchedule]:
        """Get all active schedules that are due to run."""
        now = datetime.utcnow()

        schedules = db.query(AutomationSchedule).filter(
            AutomationSchedule.is_active == True,
            AutomationSchedule.next_run_at <= now
        ).all()

        logger.info(f"Found {len(schedules)} due schedules")
        return schedules

    @staticmethod
    def mark_schedule_executed(
        db: Session,
        schedule_id: UUID,
        job_run_id: UUID,
        success: bool,
        error_message: Optional[str] = None
    ):
        """
        Mark schedule as executed and calculate next run time.

        Args:
            db: Database session
            schedule_id: Schedule UUID
            job_run_id: JobRun UUID
            success: Whether execution was successful
            error_message: Error message if failed
        """
        schedule = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        ).first()

        if not schedule:
            return

        if success:
            schedule.mark_run_success(job_run_id)
        else:
            schedule.mark_run_failed(error_message or "Unknown error")

        # Calculate next run time
        schedule.next_run_at = AutomationScheduleService._calculate_next_run(
            schedule_type=schedule.schedule_type,
            hour_of_day=schedule.hour_of_day,
            day_of_week=schedule.day_of_week,
            day_of_month=schedule.day_of_month,
            cron_expression=schedule.cron_expression,
            from_time=datetime.utcnow()
        )

        # Auto-disable if too many failures
        if schedule.should_auto_disable:
            logger.warning(
                f"Auto-disabling schedule {schedule.name} after {schedule.consecutive_failures} failures"
            )
            schedule.deactivate()

        db.commit()

    @staticmethod
    def _calculate_next_run(
        schedule_type: str,
        hour_of_day: Optional[int] = None,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
        cron_expression: Optional[str] = None,
        from_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next run time based on schedule type.

        Args:
            schedule_type: Type of schedule
            hour_of_day: Hour of day (0-23)
            day_of_week: Day of week (0-6, Monday-Sunday)
            day_of_month: Day of month (1-31)
            cron_expression: Cron expression for custom schedules
            from_time: Calculate from this time (default: now)

        Returns:
            Next run datetime
        """
        if from_time is None:
            from_time = datetime.utcnow()

        if schedule_type == "manual":
            # Manual schedules don't have automatic next run
            return from_time + timedelta(days=365)  # Far future

        elif schedule_type == "hourly":
            # Next hour
            next_run = from_time.replace(minute=0, second=0, microsecond=0)
            next_run += timedelta(hours=1)
            return next_run

        elif schedule_type == "daily":
            # Next occurrence of hour_of_day
            next_run = from_time.replace(
                hour=hour_of_day or 9,
                minute=0,
                second=0,
                microsecond=0
            )
            if next_run <= from_time:
                next_run += timedelta(days=1)
            return next_run

        elif schedule_type == "weekly":
            # Next occurrence of day_of_week at hour_of_day
            target_weekday = day_of_week or 0  # Monday
            target_hour = hour_of_day or 9

            next_run = from_time.replace(
                hour=target_hour,
                minute=0,
                second=0,
                microsecond=0
            )

            # Calculate days until target weekday
            current_weekday = from_time.weekday()
            days_ahead = target_weekday - current_weekday

            if days_ahead <= 0 or (days_ahead == 0 and next_run <= from_time):
                days_ahead += 7

            next_run += timedelta(days=days_ahead)
            return next_run

        elif schedule_type == "monthly":
            # Next occurrence of day_of_month at hour_of_day
            target_day = day_of_month or 1
            target_hour = hour_of_day or 9

            next_run = from_time.replace(
                day=target_day,
                hour=target_hour,
                minute=0,
                second=0,
                microsecond=0
            )

            if next_run <= from_time:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)

            return next_run

        elif schedule_type == "custom" and cron_expression:
            # Use APScheduler's cron parser
            try:
                from apscheduler.triggers.cron import CronTrigger
                trigger = CronTrigger.from_crontab(cron_expression)
                next_run = trigger.get_next_fire_time(None, from_time)
                return next_run
            except Exception as e:
                logger.error(f"Failed to parse cron expression: {cron_expression}, {str(e)}")
                return from_time + timedelta(days=1)

        else:
            # Default: run in 1 hour
            return from_time + timedelta(hours=1)

    @staticmethod
    def get_all_active_schedules(db: Session) -> List[AutomationSchedule]:
        """Get all active schedules across all businesses."""
        schedules = db.query(AutomationSchedule).filter(
            AutomationSchedule.is_active == True,
            AutomationSchedule.schedule_type != "manual"
        ).all()

        logger.info(f"Found {len(schedules)} active schedules")
        return schedules

    @staticmethod
    def update_last_run(db: Session, schedule_id: UUID):
        """Update last run timestamp for a schedule."""
        schedule = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        ).first()

        if schedule:
            schedule.last_run_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def record_job_success(db: Session, schedule_id: UUID):
        """Record successful job execution."""
        schedule = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        ).first()

        if schedule:
            schedule.consecutive_failures = 0
            db.commit()
            logger.info(f"Recorded success for schedule {schedule_id}")

    @staticmethod
    def record_job_failure(db: Session, schedule_id: UUID, error_message: str):
        """Record failed job execution."""
        schedule = db.query(AutomationSchedule).filter(
            AutomationSchedule.id == schedule_id
        ).first()

        if schedule:
            schedule.consecutive_failures += 1
            schedule.last_error_message = error_message
            schedule.last_error_at = datetime.utcnow()

            # Auto-disable if too many consecutive failures
            if schedule.consecutive_failures >= 5:
                logger.warning(
                    f"Auto-disabling schedule {schedule_id} after {schedule.consecutive_failures} consecutive failures"
                )
                schedule.deactivate()

            db.commit()
            logger.error(f"Recorded failure for schedule {schedule_id}: {error_message}")

    @staticmethod
    def parse_client_ids(schedule: AutomationSchedule) -> Optional[List[UUID]]:
        """Parse client IDs from JSON string."""
        if not schedule.client_ids:
            return None

        try:
            client_id_strings = json.loads(schedule.client_ids)
            return [UUID(cid) for cid in client_id_strings]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse client_ids for schedule {schedule.id}: {str(e)}")
            return None
