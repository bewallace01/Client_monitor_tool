"""Start the scheduler in background mode."""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scheduler.runner import SchedulerRunner


def setup_logging():
    """Setup logging to file and console."""
    # Create logs directory
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / "scheduler.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def write_pid_file():
    """Write process ID to file for monitoring."""
    pid_file = project_root / "data" / "scheduler.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)

    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    return pid_file


def remove_pid_file():
    """Remove PID file on shutdown."""
    pid_file = project_root / "data" / "scheduler.pid"
    if pid_file.exists():
        pid_file.unlink()


def main():
    """Main entry point for scheduler."""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("SCHEDULER STARTING")
    logger.info("=" * 60)
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"PID: {os.getpid()}")

    # Write PID file
    pid_file = write_pid_file()
    logger.info(f"PID file: {pid_file}")

    try:
        # Create and start scheduler
        scheduler = SchedulerRunner()

        logger.info("Scheduler initialized with default schedules:")
        for job_name, schedule_config in scheduler.schedules.items():
            logger.info(f"  - {job_name}: {schedule_config}")

        logger.info("Starting scheduler loop...")
        logger.info("Press Ctrl+C to stop")

        # Start scheduler (blocking call)
        scheduler.start()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")

    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)

    finally:
        remove_pid_file()
        logger.info("Scheduler stopped")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
