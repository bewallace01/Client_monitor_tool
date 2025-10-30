"""Notification model for user notifications."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class Notification(Base):
    """User notifications for important events and updates.

    Notifications alert users to high-relevance events, client assignments,
    system updates, and other important information within their business context.
    """

    __tablename__ = "notifications"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Multi-tenancy and targeting
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

    # Notification content
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "high_relevance_event", "client_assigned", "system_update", etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Optional URL to related resource

    # Related entities (optional)
    related_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=True
    )
    related_client_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=True
    )

    # Status tracking
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Priority level
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)  # "low", "normal", "high", "urgent"

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    business = relationship("Business")
    user = relationship("User", back_populates="notifications")
    related_event = relationship("Event")
    related_client = relationship("Client")

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_business_created", "business_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type='{self.type}', user_id={self.user_id}, read={self.is_read})>"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()

    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.is_read:
            self.is_read = False
            self.read_at = None
