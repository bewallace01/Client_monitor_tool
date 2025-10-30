"""Scheduler runner for automated job execution."""

import schedule
import time
import logging
import signal
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.storage import SQLiteStorage
from src.scheduler.jobs import run_job

logger = logging.getLogger(__name__)


class SchedulerRunner:
    """Manages scheduled job execution."""

    def __init__(self, status_file: str = "data/scheduler_status.json"):
        """
        Initialize scheduler runner.

        Args:
            status_file: Path to status file for tracking scheduler state
        """
        self.storage = SQLiteStorage()
        self.storage.connect()
        self.running = False
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        # Default schedules
        self.schedules = {
            "daily_scan": "08:00",
            "weekly_report": {"day": "monday", "time": "09:00"},
            "cache_cleanup": "02:00",
        }

        # Track last run times
        self.last_runs = {}

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def _update_status(self, status: str, next_run: str = None):
        """Update status file for UI monitoring."""
        status_data = {
            "status": status,
            "last_updated": datetime.utcnow().isoformat(),
            "next_run": next_run,
            "schedules": self.schedules,
            "last_runs": self.last_runs,
        }

        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

    def _run_job_wrapper(self, job_name: str):
        """Wrapper to run job and update status."""
        try:
            logger.info(f"Running scheduled job: {job_name}")
            self._update_status("running", None)

            job_run = run_job(job_name, self.storage)

            self.last_runs[job_name] = {
                "time": datetime.utcnow().isoformat(),
                "status": job_run.status,
                "summary": job_run.results_summary,
            }

            logger.info(f"Job {job_name} completed with status: {job_run.status}")
            self._update_status("idle", self._get_next_run())

        except Exception as e:
            logger.error(f"Error running job {job_name}: {e}")
            self.last_runs[job_name] = {
                "time": datetime.utcnow().isoformat(),
                "status": "failed",
                "summary": str(e),
            }
            self._update_status("idle", self._get_next_run())

    def _get_next_run(self) -> str:
        """Get the next scheduled job run time."""
        next_run = schedule.next_run()
        if next_run:
            return next_run.isoformat()
        return None

    def configure_schedule(self, schedules: Dict[str, Any] = None):
        """
        Configure job schedules.

        Args:
            schedules: Dictionary of job schedules
        """
        if schedules:
            self.schedules.update(schedules)

        # Clear existing schedule
        schedule.clear()

        # Schedule daily scan
        if "daily_scan" in self.schedules:
            daily_time = self.schedules["daily_scan"]
            schedule.every().day.at(daily_time).do(
                self._run_job_wrapper, "daily_scan"
            )
            logger.info(f"Scheduled daily_scan for {daily_time} daily")

        # Schedule weekly report
        if "weekly_report" in self.schedules:
            weekly_config = self.schedules["weekly_report"]
            day = weekly_config.get("day", "monday")
            time_str = weekly_config.get("time", "09:00")

            getattr(schedule.every(), day).at(time_str).do(
                self._run_job_wrapper, "weekly_report"
            )
            logger.info(f"Scheduled weekly_report for {day} at {time_str}")

        # Schedule cache cleanup
        if "cache_cleanup" in self.schedules:
            cleanup_time = self.schedules["cache_cleanup"]
            schedule.every().day.at(cleanup_time).do(
                self._run_job_wrapper, "cache_cleanup"
            )
            logger.info(f"Scheduled cache_cleanup for {cleanup_time} daily")

        self._update_status("idle", self._get_next_run())

    def start(self):
        """Start the scheduler loop."""
        logger.info("Starting scheduler...")
        self.running = True
        self.configure_schedule()
        self._update_status("idle", self._get_next_run())

        while self.running:
            schedule.run_pending()
            time.sleep(1)

        logger.info("Scheduler stopped")
        self._update_status("stopped", None)

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.running = False
        self._update_status("stopped", None)

    def run_job_now(self, job_name: str):
        """Run a job immediately (outside of schedule)."""
        logger.info(f"Running job {job_name} manually...")
        self._run_job_wrapper(job_name)


def get_scheduler_status(status_file: str = "data/scheduler_status.json") -> Dict[str, Any]:
    """
    Read scheduler status from file.

    Args:
        status_file: Path to status file

    Returns:
        Dictionary with scheduler status or None if not found
    """
    status_path = Path(status_file)

    if not status_path.exists():
        return {
            "status": "stopped",
            "last_updated": None,
            "next_run": None,
            "schedules": {},
            "last_runs": {},
        }

    try:
        with open(status_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading scheduler status: {e}")
        return {
            "status": "unknown",
            "last_updated": None,
            "next_run": None,
            "schedules": {},
            "last_runs": {},
        }
