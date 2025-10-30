"""Event data model."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, DateTime, Float, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from .client import Base


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
    __table_args__ = (
        Index("ix_events_client_date", "client_id", "event_date"),
        Index("ix_events_category", "category"),
        Index("ix_events_relevance", "relevance_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=False, index=True)

    # Event details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # e.g., "TechCrunch", "Reuters"

    # Classification
    category: Mapped[str] = mapped_column(String(50), nullable=False, default=EventCategory.OTHER.value)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1.0 to 1.0

    # Dates
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Deduplication
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # User interaction
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_starred: Mapped[bool] = mapped_column(default=False, nullable=False)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, client_id={self.client_id}, category='{self.category}', title='{self.title[:50]}...')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API/UI use."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "relevance_score": self.relevance_score,
            "sentiment_score": self.sentiment_score,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "content_hash": self.content_hash,
            "is_read": self.is_read,
            "is_starred": self.is_starred,
            "user_notes": self.user_notes,
        }

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
