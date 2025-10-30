"""Automation schedule model for user-defined job schedules."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class AutomationSchedule(Base):
    """User-defined schedules for automated monitoring jobs."""

    __tablename__ = "automation_schedules"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Schedule Details
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # User-friendly name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Job Configuration
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # "client_monitoring", "search_only", "notification_digest"

    client_ids: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )  # JSON array of client UUIDs to monitor (null = all clients)

    config: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )  # JSON configuration for job (e.g., force_mock, additional_params)

    minute_of_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-59

    # Schedule Configuration
    schedule_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # "manual", "hourly", "daily", "weekly", "monthly", "custom"

    cron_expression: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )  # For custom schedules (e.g., "0 9 * * 1-5" for weekdays at 9am)

    # Schedule metadata
    hour_of_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-23
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-6 (Monday-Sunday)
    day_of_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-31

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Execution tracking
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    last_run_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "success", "failed"
    last_run_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("job_runs.id", ondelete="SET NULL"),
        nullable=True
    )

    # Error tracking
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    business = relationship("Business")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    last_run_job = relationship("JobRun", foreign_keys=[last_run_job_id])

    # Composite indexes
    __table_args__ = (
        Index("ix_automation_schedules_business_active", "business_id", "is_active"),
        Index("ix_automation_schedules_business_type", "business_id", "job_type"),
        Index("ix_automation_schedules_next_run", "is_active", "next_run_at"),
    )

    def __repr__(self) -> str:
        return f"<AutomationSchedule(id={self.id}, name='{self.name}', type='{self.job_type}', active={self.is_active})>"

    def mark_run_success(self, job_run_id: uuid.UUID):
        """Mark a successful job run."""
        self.last_run_at = datetime.utcnow()
        self.last_run_status = "success"
        self.last_run_job_id = job_run_id
        self.consecutive_failures = 0
        self.last_error_message = None

    def mark_run_failed(self, error_message: str):
        """Mark a failed job run."""
        self.last_run_at = datetime.utcnow()
        self.last_run_status = "failed"
        self.consecutive_failures += 1
        self.last_error_message = error_message

    def activate(self):
        """Activate the schedule."""
        self.is_active = True

    def deactivate(self):
        """Deactivate the schedule."""
        self.is_active = False

    @property
    def is_due(self) -> bool:
        """Check if schedule is due to run."""
        if not self.is_active:
            return False
        if self.next_run_at is None:
            return True
        return datetime.utcnow() >= self.next_run_at

    @property
    def should_auto_disable(self) -> bool:
        """Check if schedule should be auto-disabled due to failures."""
        # Auto-disable after 5 consecutive failures
        return self.consecutive_failures >= 5
