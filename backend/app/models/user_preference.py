"""User preference model for notification and automation settings."""

import uuid
from datetime import datetime, time
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Float, Text, Integer, ForeignKey, Index, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class UserPreference(Base):
    """User preferences for notifications and automation settings."""

    __tablename__ = "user_preferences"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One preference record per user
        index=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Notification Settings
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Threshold Settings
    relevance_threshold: Mapped[float] = mapped_column(
        Float,
        default=0.7,
        nullable=False
    )  # 0.0 to 1.0 - only notify for events above this score

    # Category Filters
    notification_categories: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )  # JSON array of categories to monitor (null = all categories)

    # Frequency Settings
    notification_frequency: Mapped[str] = mapped_column(
        String(20),
        default="instant",
        nullable=False
    )  # "instant", "daily", "weekly"

    # Client Filtering
    assigned_clients_only: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )  # Only notify for clients assigned to this user

    # Digest Settings
    digest_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )  # Time of day for daily/weekly digests (e.g., 09:00:00)

    digest_day_of_week: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # For weekly digests: 0=Monday, 6=Sunday

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", backref="preference")
    business = relationship("Business")

    # Composite indexes
    __table_args__ = (
        Index("ix_user_preferences_user_business", "user_id", "business_id"),
    )

    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, relevance_threshold={self.relevance_threshold}, frequency='{self.notification_frequency}')>"

    @property
    def should_send_instant_notifications(self) -> bool:
        """Check if instant notifications are enabled."""
        return self.notification_enabled and self.notification_frequency == "instant"

    @property
    def should_send_digest(self) -> bool:
        """Check if digest notifications are enabled."""
        return self.notification_enabled and self.notification_frequency in ["daily", "weekly"]
