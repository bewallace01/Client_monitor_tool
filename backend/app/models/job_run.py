"""Job run model for tracking scheduled job executions."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class JobRun(Base):
    """Tracks execution of scheduled jobs."""

    __tablename__ = "job_runs"

    # Primary Key (UUID instead of int)
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)  # Unique job execution ID
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Multi-tenancy
    business_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=True,  # Nullable for backwards compatibility and system-wide jobs
        index=True
    )

    # Execution timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, running, completed, failed

    # Metrics
    events_found: Mapped[int] = mapped_column(default=0)
    events_new: Mapped[int] = mapped_column(default=0)
    clients_processed: Mapped[int] = mapped_column(default=0)

    # Results and errors
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object

    # Relationships
    business = relationship("Business", back_populates="job_runs")
    api_request_logs = relationship("APIRequestLog", back_populates="job_run", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        Index("ix_job_runs_business_status", "business_id", "status"),
        Index("ix_job_runs_business_type", "business_id", "job_type"),
    )

    def __repr__(self) -> str:
        return f"<JobRun(id={self.id}, job_type='{self.job_type}', status='{self.status}', business_id={self.business_id})>"

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def mark_completed(self, events_found: int = 0, events_new: int = 0, clients_processed: int = 0):
        """Mark job as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.events_found = events_found
        self.events_new = events_new
        self.clients_processed = clients_processed

    def mark_failed(self, error_message: str):
        """Mark job as failed."""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
