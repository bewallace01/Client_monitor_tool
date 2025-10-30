"""Client data model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Client(Base):
    """Represents a client company to monitor."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Search configuration
    search_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Customer Success metadata
    account_owner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Enterprise", "Mid-Market"
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', active={self.is_active})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API/UI use."""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "description": self.description,
            "search_keywords": self.search_keywords,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "account_owner": self.account_owner,
            "tier": self.tier,
            "notes": self.notes,
        }
