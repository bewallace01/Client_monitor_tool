"""Client data model."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.business import GUID


class Client(Base):
    """Represents a client company to monitor."""

    __tablename__ = "clients"

    # Primary Key (UUID instead of int)
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Multi-tenancy
    business_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Company Details (New)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "1-10", "11-50", etc.
    revenue_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "$1M-$10M", etc.
    headquarters_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Search configuration
    search_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    monitoring_frequency: Mapped[str] = mapped_column(String(20), default="daily", nullable=False)  # "hourly", "daily", "weekly"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Customer Success (Fixed - FK to User)
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "Enterprise", "Mid-Market", "SMB"
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    business = relationship("Business", back_populates="clients")
    assigned_to_user = relationship(
        "User",
        foreign_keys=[assigned_to_user_id],
        back_populates="assigned_clients"
    )
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    deleted_by_user = relationship("User", foreign_keys=[deleted_by_user_id])
    events = relationship("Event", back_populates="client", cascade="all, delete-orphan")
    tags = relationship("ClientTag", back_populates="client", cascade="all, delete-orphan")
    api_request_logs = relationship("APIRequestLog", back_populates="client", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        Index("ix_clients_business_active", "business_id", "is_active"),
        Index("ix_clients_business_deleted", "business_id", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', active={self.is_active}, business_id={self.business_id})>"
