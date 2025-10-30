"""Email log model for tracking email delivery."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class EmailLog(Base):
    """Tracks email delivery history for notifications and digests."""

    __tablename__ = "email_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Related entities
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    job_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("job_runs.id", ondelete="SET NULL"),
        nullable=True
    )

    # Email details
    email_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # "event_notification", "digest", "alert", "system"

    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # First 500 chars

    # Delivery tracking
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # "sent", "failed", "pending", "bounced"

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Provider information
    provider: Mapped[str] = mapped_column(
        String(50),
        default="smtp",
        nullable=False
    )  # "smtp", "sendgrid", "ses", "mock"

    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # User interaction tracking
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    business = relationship("Business")
    user = relationship("User")
    event = relationship("Event")
    job_run = relationship("JobRun")

    # Composite indexes
    __table_args__ = (
        Index("ix_email_logs_business_user", "business_id", "user_id"),
        Index("ix_email_logs_business_type", "business_id", "email_type"),
        Index("ix_email_logs_status_sent", "status", "sent_at"),
        Index("ix_email_logs_user_sent", "user_id", "sent_at"),
    )

    def __repr__(self) -> str:
        return f"<EmailLog(id={self.id}, type='{self.email_type}', recipient='{self.recipient_email}', status='{self.status}')>"

    def mark_sent(self, provider_message_id: str = None):
        """Mark email as sent."""
        self.status = "sent"
        self.sent_at = datetime.utcnow()
        self.provider_message_id = provider_message_id

    def mark_failed(self, error_message: str):
        """Mark email as failed."""
        self.status = "failed"
        self.error_message = error_message
        self.retry_count += 1

    def mark_bounced(self, error_message: str):
        """Mark email as bounced."""
        self.status = "bounced"
        self.error_message = error_message

    def mark_opened(self):
        """Mark email as opened by recipient."""
        if not self.opened_at:
            self.opened_at = datetime.utcnow()

    def mark_clicked(self):
        """Mark email link as clicked by recipient."""
        if not self.clicked_at:
            self.clicked_at = datetime.utcnow()

    @property
    def should_retry(self) -> bool:
        """Check if email should be retried."""
        return self.status == "failed" and self.retry_count < 3

    @property
    def was_delivered(self) -> bool:
        """Check if email was successfully delivered."""
        return self.status == "sent"
