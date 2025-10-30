"""Tag models for flexible categorization of clients and events."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class Tag(Base):
    """Flexible tagging system for clients and events.

    Tags allow users to categorize and organize clients and events beyond
    the predefined categories, enabling custom workflows and filtering.
    """

    __tablename__ = "tags"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tag details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color code (e.g., "#FF5733")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    business = relationship("Business")
    created_by_user = relationship("User")
    client_tags = relationship("ClientTag", back_populates="tag", cascade="all, delete-orphan")
    event_tags = relationship("EventTag", back_populates="tag", cascade="all, delete-orphan")

    # Unique constraint: tag names must be unique within a business
    __table_args__ = (
        Index("ix_tags_business_name", "business_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', business_id={self.business_id})>"


class ClientTag(Base):
    """Many-to-many relationship between clients and tags."""

    __tablename__ = "client_tags"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    client_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    client = relationship("Client", back_populates="tags")
    tag = relationship("Tag", back_populates="client_tags")
    created_by_user = relationship("User")

    # Unique constraint: each tag can only be applied once to a client
    __table_args__ = (
        Index("ix_client_tags_unique", "client_id", "tag_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ClientTag(client_id={self.client_id}, tag_id={self.tag_id})>"


class EventTag(Base):
    """Many-to-many relationship between events and tags."""

    __tablename__ = "event_tags"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    event_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    event = relationship("Event", back_populates="event_tags")
    tag = relationship("Tag", back_populates="event_tags")
    created_by_user = relationship("User")

    # Unique constraint: each tag can only be applied once to an event
    __table_args__ = (
        Index("ix_event_tags_unique", "event_id", "tag_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<EventTag(event_id={self.event_id}, tag_id={self.tag_id})>"
