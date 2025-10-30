"""Event raw data model for storing unprocessed API responses."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class EventRawData(Base):
    """Stores raw, unprocessed data from external APIs before AI processing."""

    __tablename__ = "event_raw_data"

    # Primary Key
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

    # Job tracking
    job_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("job_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Source information
    source_api: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # "google_search", "serper", "newsapi", "mock"

    search_query: Mapped[str] = mapped_column(String(500), nullable=False)

    # Raw data from API
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string

    # Content hash for deduplication
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    processed_into_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True
    )

    # Processing error tracking
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    business = relationship("Business")
    client = relationship("Client")
    job_run = relationship("JobRun")
    processed_event = relationship("Event", foreign_keys=[processed_into_event_id])

    # Composite indexes
    __table_args__ = (
        Index("ix_event_raw_data_business_client", "business_id", "client_id"),
        Index("ix_event_raw_data_business_processed", "business_id", "is_processed"),
        Index("ix_event_raw_data_source_api", "source_api", "created_at"),
        Index("ix_event_raw_data_content_hash", "content_hash"),
    )

    def __repr__(self) -> str:
        return f"<EventRawData(id={self.id}, client_id={self.client_id}, source='{self.source_api}', processed={self.is_processed})>"

    def mark_as_processed(self, event_id: uuid.UUID):
        """Mark raw data as processed into an event."""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        self.processed_into_event_id = event_id

    def mark_as_failed(self, error_message: str):
        """Mark raw data processing as failed."""
        self.is_processed = True  # Mark as processed so we don't retry indefinitely
        self.processed_at = datetime.utcnow()
        self.processing_error = error_message
