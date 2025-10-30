"""Scheduler process control utilities."""

import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_pid_file() -> Path:
    """Get the PID file path."""
    return get_project_root() / "data" / "scheduler.pid"


def is_scheduler_running() -> bool:
    """Check if scheduler is currently running."""
    pid_file = get_pid_file()

    if not pid_file.exists():
        return False

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        # Check if process exists
        if sys.platform == "win32":
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Unix: send signal 0 to check if process exists
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    except Exception:
        return False


def start_scheduler() -> bool:
    """
    Start the scheduler in background.

    Returns:
        bool: True if started successfully, False otherwise
    """
    if is_scheduler_running():
        return False  # Already running

    project_root = get_project_root()
    script_path = project_root / "scripts" / "start_scheduler.py"

    try:
        if sys.platform == "win32":
            # Windows: use pythonw to run in background without console
            subprocess.Popen(
                [sys.executable, str(script_path)],
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=str(project_root)
            )
        else:
            # Unix: use nohup to run in background
            subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                cwd=str(project_root)
            )

        return True

    except Exception as e:
        print(f"Error starting scheduler: {e}")
        return False


def stop_scheduler() -> bool:
    """
    Stop the running scheduler.

    Returns:
        bool: True if stopped successfully, False otherwise
    """
    pid_file = get_pid_file()

    if not pid_file.exists():
        return False  # Not running

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        # Send termination signal
        if sys.platform == "win32":
            # Windows: use taskkill
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True
            )
        else:
            # Unix: send SIGTERM
            os.kill(pid, signal.SIGTERM)

        # Remove PID file
        pid_file.unlink()

        return True

    except Exception as e:
        print(f"Error stopping scheduler: {e}")
        return False


def get_scheduler_pid() -> Optional[int]:
    """
    Get the PID of the running scheduler.

    Returns:
        int or None: PID if running, None otherwise
    """
    pid_file = get_pid_file()

    if not pid_file.exists():
        return None

    try:
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return None
