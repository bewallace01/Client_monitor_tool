"""Event user interaction model for tracking user-specific event interactions."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class EventUserInteraction(Base):
    """Track user-specific interactions with events.

    This separates user-specific data (is_read, is_starred) from the event itself,
    allowing multiple users within the same business to have independent interactions
    with the same event.
    """

    __tablename__ = "event_user_interactions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    event_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Interaction flags
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    starred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # User notes (separate from event description)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    event = relationship("Event", back_populates="user_interactions")
    user = relationship("User", back_populates="event_interactions")

    # Unique constraint: one interaction record per user per event
    __table_args__ = (
        Index("ix_event_user_unique", "event_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<EventUserInteraction(event_id={self.event_id}, user_id={self.user_id}, read={self.is_read}, starred={self.is_starred})>"

    def mark_as_read(self):
        """Mark event as read by this user."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()

    def mark_as_unread(self):
        """Mark event as unread by this user."""
        if self.is_read:
            self.is_read = False
            self.read_at = None

    def toggle_starred(self):
        """Toggle starred status for this user."""
        self.is_starred = not self.is_starred
        if self.is_starred:
            self.starred_at = datetime.utcnow()
        else:
            self.starred_at = None
