"""Search cache model to avoid redundant API calls."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from .client import Base


class SearchCache(Base):
    """Caches search results to reduce API calls and costs."""

    __tablename__ = "search_cache"
    __table_args__ = (
        Index("ix_search_cache_lookup", "query_hash", "cached_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Query identification
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query_text: Mapped[str] = mapped_column(String(500), nullable=False)

    # Cache data
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of results
    result_count: Mapped[int] = mapped_column(default=0, nullable=False)

    # Metadata
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "mock", "newsapi", "google"

    def __repr__(self) -> str:
        return f"<SearchCache(id={self.id}, query='{self.query_text[:50]}...', results={self.result_count})>"

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary for API/UI use."""
        return {
            "id": self.id,
            "query_hash": self.query_hash,
            "query_text": self.query_text,
            "result_count": self.result_count,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "is_expired": self.is_expired(),
        }
