"""Job run model for tracking scheduled job executions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Literal
import json


@dataclass
class JobRun:
    """
    Tracks execution of scheduled jobs.
    """

    id: str
    job_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: Literal["running", "completed", "failed", "cancelled"] = "running"
    results_summary: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "job_name": self.job_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "results_summary": self.results_summary,
            "error_message": self.error_message,
            "metadata": json.dumps(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobRun":
        """Create JobRun from dictionary."""
        if isinstance(data.get("start_time"), str):
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if isinstance(data.get("end_time"), str) and data["end_time"]:
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        if isinstance(data.get("metadata"), str):
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}

        return cls(**data)

    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def mark_completed(self, results_summary: str = ""):
        """Mark job as completed."""
        self.status = "completed"
        self.end_time = datetime.utcnow()
        self.results_summary = results_summary

    def mark_failed(self, error_message: str):
        """Mark job as failed."""
        self.status = "failed"
        self.end_time = datetime.utcnow()
        self.error_message = error_message

    def mark_cancelled(self):
        """Mark job as cancelled."""
        self.status = "cancelled"
        self.end_time = datetime.utcnow()
