"""Event data model."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Float, Text, Integer, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class EventCategory(str, Enum):
    """Event category enumeration."""
    FUNDING = "funding"
    ACQUISITION = "acquisition"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT_LAUNCH = "product_launch"
    PARTNERSHIP = "partnership"
    FINANCIAL_RESULTS = "financial_results"
    REGULATORY = "regulatory"
    AWARD = "award"
    OTHER = "other"


class Event(Base):
    """Represents a business event for a client."""

    __tablename__ = "events"

    # Primary Key (UUID instead of int)
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Event details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # e.g., "TechCrunch", "Reuters"
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "news", "social", "press_release"

    # Classification
    category: Mapped[str] = mapped_column(String(50), nullable=False, default=EventCategory.OTHER.value, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # More granular
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array for flexible tagging

    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, index=True)  # 0.0 to 1.0
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1.0 to 1.0
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # How confident is the AI classification?

    # Dates
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Deduplication
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    duplicate_of_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("events.id"),
        nullable=True
    )

    # User interaction (DEPRECATED - moved to EventUserInteraction, kept for backwards compatibility during migration)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Data ownership
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    business = relationship("Business", back_populates="events")
    client = relationship("Client", back_populates="events")
    user_interactions = relationship("EventUserInteraction", back_populates="event", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    deleted_by_user = relationship("User", foreign_keys=[deleted_by_user_id])
    duplicate_of = relationship("Event", remote_side=[id], foreign_keys=[duplicate_of_event_id])
    event_tags = relationship("EventTag", back_populates="event", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        Index("ix_events_business_client", "business_id", "client_id"),
        Index("ix_events_business_date", "business_id", "event_date"),
        Index("ix_events_business_category", "business_id", "category"),
        Index("ix_events_business_deleted", "business_id", "is_deleted"),
        Index("ix_events_content_hash", "content_hash"),
    )

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, client_id={self.client_id}, category='{self.category}', title='{self.title[:50]}...')>"

    @property
    def sentiment_label(self) -> str:
        """Human-readable sentiment label."""
        if self.sentiment_score is None:
            return "neutral"
        if self.sentiment_score > 0.3:
            return "positive"
        elif self.sentiment_score < -0.3:
            return "negative"
        else:
            return "neutral"

    @property
    def relevance_label(self) -> str:
        """Human-readable relevance label."""
        if self.relevance_score >= 0.7:
            return "high"
        elif self.relevance_score >= 0.4:
            return "medium"
        else:
            return "low"
