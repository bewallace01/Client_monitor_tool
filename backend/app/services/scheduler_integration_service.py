"""Scheduler integration service for managing automated jobs.

Integrates APScheduler with the database-backed automation schedules.
Handles job registration, execution, and lifecycle management.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from app.models.automation_schedule import AutomationSchedule
from app.services.automation_engine_service import AutomationEngineService
from app.services.automation_schedule_service import AutomationScheduleService
from app.database.connection import SessionLocal

logger = logging.getLogger(__name__)


class SchedulerIntegrationService:
    """Manages APScheduler integration with database schedules."""

    _scheduler: Optional[AsyncIOScheduler] = None
    _is_running: bool = False

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        """Get or create the scheduler instance."""
        if cls._scheduler is None:
            cls._scheduler = AsyncIOScheduler(
                timezone="UTC",
                job_defaults={
                    'coalesce': True,  # Combine missed executions
                    'max_instances': 3,  # Allow up to 3 concurrent instances per job
                    'misfire_grace_time': 900  # 15 minutes grace time for missed jobs
                }
            )
        return cls._scheduler

    @classmethod
    async def start_scheduler(cls):
        """Start the scheduler and load all active schedules."""
        if cls._is_running:
            logger.warning("Scheduler is already running")
            return

        scheduler = cls.get_scheduler()

        # Start the scheduler
        scheduler.start()
        cls._is_running = True
        logger.info("APScheduler started successfully")

        # Load and register all active schedules from database
        await cls.load_all_schedules()

    @classmethod
    async def shutdown_scheduler(cls):
        """Shutdown the scheduler gracefully."""
        if not cls._is_running:
            logger.warning("Scheduler is not running")
            return

        scheduler = cls.get_scheduler()
        scheduler.shutdown(wait=True)
        cls._is_running = False
        logger.info("APScheduler shut down successfully")

    @classmethod
    async def load_all_schedules(cls):
        """Load all active schedules from database and register with APScheduler."""
        db = SessionLocal()
        try:
            # Get all active schedules across all businesses
            schedules = AutomationScheduleService.get_all_active_schedules(db)

            logger.info(f"Loading {len(schedules)} active schedules")

            for schedule in schedules:
                try:
                    await cls.register_schedule(schedule)
                except Exception as e:
                    logger.error(f"Failed to register schedule {schedule.id}: {str(e)}")
                    continue

            logger.info(f"Successfully loaded {len(schedules)} schedules")

        except Exception as e:
            logger.error(f"Failed to load schedules: {str(e)}")
        finally:
            db.close()

    @classmethod
    async def register_schedule(cls, schedule: AutomationSchedule):
        """Register a single schedule with APScheduler."""
        if not cls._is_running:
            logger.warning("Cannot register schedule - scheduler not running")
            return

        scheduler = cls.get_scheduler()
        job_id = str(schedule.id)

        # Remove existing job if it exists
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed existing job {job_id}")

        # Create appropriate trigger based on schedule type
        trigger = cls._create_trigger(schedule)

        if trigger is None:
            logger.warning(f"Could not create trigger for schedule {schedule.id} (type: {schedule.schedule_type})")
            return

        # Register the job
        scheduler.add_job(
            func=cls._execute_scheduled_job,
            trigger=trigger,
            id=job_id,
            name=schedule.name or f"{schedule.job_type}_{schedule.id}",
            kwargs={
                'schedule_id': schedule.id,
                'business_id': schedule.business_id,
                'job_type': schedule.job_type
            },
            replace_existing=True
        )

        logger.info(
            f"Registered schedule {schedule.id} ({schedule.schedule_type}) - "
            f"Next run: {schedule.next_run_at}"
        )

    @classmethod
    def _create_trigger(cls, schedule: AutomationSchedule):
        """Create APScheduler trigger from schedule configuration."""

        if schedule.schedule_type == "manual":
            # Manual schedules don't have triggers
            return None

        elif schedule.schedule_type == "hourly":
            # Run every hour at the specified minute
            minute = schedule.minute_of_hour or 0
            return CronTrigger(minute=minute, timezone="UTC")

        elif schedule.schedule_type == "daily":
            # Run daily at the specified time
            hour = schedule.hour_of_day or 9
            minute = schedule.minute_of_hour or 0
            return CronTrigger(hour=hour, minute=minute, timezone="UTC")

        elif schedule.schedule_type == "weekly":
            # Run weekly on specified day and time
            day_of_week = schedule.day_of_week or 0  # 0 = Monday
            hour = schedule.hour_of_day or 9
            minute = schedule.minute_of_hour or 0
            return CronTrigger(
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                timezone="UTC"
            )

        elif schedule.schedule_type == "monthly":
            # Run monthly on specified day and time
            day = schedule.day_of_month or 1
            hour = schedule.hour_of_day or 9
            minute = schedule.minute_of_hour or 0
            return CronTrigger(
                day=day,
                hour=hour,
                minute=minute,
                timezone="UTC"
            )

        elif schedule.schedule_type == "custom" and schedule.cron_expression:
            # Custom cron expression
            try:
                return CronTrigger.from_crontab(schedule.cron_expression, timezone="UTC")
            except Exception as e:
                logger.error(f"Invalid cron expression for schedule {schedule.id}: {str(e)}")
                return None

        else:
            logger.warning(f"Unknown schedule type: {schedule.schedule_type}")
            return None

    @classmethod
    async def _execute_scheduled_job(
        cls,
        schedule_id: uuid.UUID,
        business_id: uuid.UUID,
        job_type: str
    ):
        """Execute a scheduled job."""
        db = SessionLocal()
        try:
            logger.info(f"Executing scheduled job {schedule_id} (type: {job_type})")

            # Get the schedule
            schedule = AutomationScheduleService.get_schedule(db, schedule_id)
            if not schedule:
                logger.error(f"Schedule {schedule_id} not found")
                return

            # Check if schedule is still active
            if not schedule.is_active:
                logger.info(f"Schedule {schedule_id} is inactive, skipping execution")
                cls._remove_job_from_scheduler(schedule_id)
                return

            # Update last run timestamp
            AutomationScheduleService.update_last_run(db, schedule_id)

            # Execute based on job type
            result = None
            if job_type == "client_monitoring":
                result = await cls._execute_client_monitoring(db, schedule)
            else:
                logger.warning(f"Unknown job type: {job_type}")
                return

            # Handle result
            if result and result.get("success"):
                # Reset failure count on success
                AutomationScheduleService.record_job_success(db, schedule_id)
                logger.info(
                    f"Job {schedule_id} completed successfully: "
                    f"{result.get('clients_processed', 0)} clients, "
                    f"{result.get('events_new', 0)} new events"
                )
            else:
                # Increment failure count
                AutomationScheduleService.record_job_failure(
                    db,
                    schedule_id,
                    result.get("error", "Unknown error") if result else "Job returned no result"
                )
                logger.error(f"Job {schedule_id} failed")

        except Exception as e:
            logger.error(f"Error executing scheduled job {schedule_id}: {str(e)}")
            # Record failure in database
            try:
                AutomationScheduleService.record_job_failure(db, schedule_id, str(e))
            except:
                pass

        finally:
            db.close()

    @classmethod
    async def _execute_client_monitoring(
        cls,
        db: Session,
        schedule: AutomationSchedule
    ) -> Dict[str, Any]:
        """Execute client monitoring job."""
        try:
            # Parse client IDs from configuration
            client_ids = None
            if schedule.client_ids:
                try:
                    import json
                    parsed_ids = json.loads(schedule.client_ids)
                    client_ids = [uuid.UUID(cid) for cid in parsed_ids]
                except Exception as e:
                    logger.warning(f"Failed to parse client_ids for schedule {schedule.id}: {str(e)}")

            # Parse configuration for additional options
            config = {}
            if schedule.config:
                try:
                    import json
                    config = json.loads(schedule.config)
                except Exception as e:
                    logger.warning(f"Failed to parse config for schedule {schedule.id}: {str(e)}")

            force_mock = config.get("force_mock", False)

            # Execute the monitoring job
            result = await AutomationEngineService.execute_client_monitoring_job(
                db=db,
                business_id=schedule.business_id,
                client_ids=client_ids,
                job_run_id=None,  # Let the service create a new job run
                user_id=schedule.created_by_user_id,
                force_mock=force_mock
            )

            return result

        except Exception as e:
            logger.error(f"Client monitoring job failed for schedule {schedule.id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def _remove_job_from_scheduler(cls, schedule_id: uuid.UUID):
        """Remove a job from the scheduler."""
        if not cls._is_running:
            return

        scheduler = cls.get_scheduler()
        job_id = str(schedule_id)

        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id} from scheduler")

    @classmethod
    async def add_schedule(cls, schedule: AutomationSchedule):
        """Add a new schedule to the scheduler."""
        if schedule.is_active and schedule.schedule_type != "manual":
            await cls.register_schedule(schedule)

    @classmethod
    async def update_schedule(cls, schedule: AutomationSchedule):
        """Update an existing schedule in the scheduler."""
        # Remove old job
        cls._remove_job_from_scheduler(schedule.id)

        # Re-register if active
        if schedule.is_active and schedule.schedule_type != "manual":
            await cls.register_schedule(schedule)

    @classmethod
    async def remove_schedule(cls, schedule_id: uuid.UUID):
        """Remove a schedule from the scheduler."""
        cls._remove_job_from_scheduler(schedule_id)

    @classmethod
    async def trigger_manual_run(
        cls,
        db: Session,
        schedule_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Manually trigger a schedule to run immediately."""
        try:
            # Get the schedule
            schedule = AutomationScheduleService.get_schedule(db, schedule_id)
            if not schedule:
                return {
                    "success": False,
                    "error": "Schedule not found"
                }

            logger.info(f"Manually triggering schedule {schedule_id}")

            # Execute the job directly
            await cls._execute_scheduled_job(
                schedule_id=schedule.id,
                business_id=schedule.business_id,
                job_type=schedule.job_type
            )

            return {
                "success": True,
                "message": "Job triggered successfully"
            }

        except Exception as e:
            logger.error(f"Failed to trigger manual run for schedule {schedule_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def get_scheduler_status(cls) -> Dict[str, Any]:
        """Get current scheduler status and job information."""
        if not cls._is_running:
            return {
                "running": False,
                "jobs": []
            }

        scheduler = cls.get_scheduler()
        jobs = scheduler.get_jobs()

        return {
            "running": True,
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
