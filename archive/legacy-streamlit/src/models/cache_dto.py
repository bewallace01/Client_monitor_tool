"""SearchCache data transfer object (DTO) with dataclass implementation."""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


@dataclass
class SearchCacheDTO:
    """
    Search cache data transfer object for API result caching.
    Helps reduce API calls and associated costs.
    """

    query: str
    api_source: str  # e.g., "newsapi", "google_news", "mock"
    results: List[Dict[str, Any]] = field(default_factory=list)
    cached_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))

    # Optional metadata
    result_count: int = 0
    query_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize computed fields after dataclass initialization."""
        # Auto-compute result count if not set
        if self.result_count == 0:
            self.result_count = len(self.results)

        # Auto-generate query hash if not set
        if self.query_hash is None:
            self.query_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """
        Generate a unique hash for the query and source combination.

        Returns:
            SHA256 hash string
        """
        content = f"{self.query}:{self.api_source}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def is_expired(self) -> bool:
        """
        Check if the cache entry has expired.

        Returns:
            True if expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at

    def time_until_expiry(self) -> timedelta:
        """
        Calculate time remaining until expiry.

        Returns:
            timedelta object (negative if already expired)
        """
        return self.expires_at - datetime.utcnow()

    def is_valid(self) -> bool:
        """
        Check if cache is still valid (not expired).

        Returns:
            True if valid, False otherwise
        """
        return not self.is_expired()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation with ISO format dates
        """
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.cached_at:
            data["cached_at"] = self.cached_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchCacheDTO":
        """
        Create SearchCacheDTO from dictionary.

        Args:
            data: Dictionary with cache data

        Returns:
            SearchCacheDTO instance
        """
        # Parse datetime strings
        if isinstance(data.get("cached_at"), str):
            data["cached_at"] = datetime.fromisoformat(data["cached_at"])
        if isinstance(data.get("expires_at"), str):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])

        return cls(**data)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate cache data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.query or len(self.query.strip()) == 0:
            return False, "Query is required"

        if not self.api_source or len(self.api_source.strip()) == 0:
            return False, "API source is required"

        if self.expires_at <= self.cached_at:
            return False, "Expiry date must be after cached date"

        if not isinstance(self.results, list):
            return False, "Results must be a list"

        return True, None

    @classmethod
    def create_sample(
        cls,
        query: str = "Sample Company",
        api_source: str = "mock",
        ttl_hours: int = 24,
    ) -> "SearchCacheDTO":
        """
        Factory method to create a sample cache entry for testing.

        Args:
            query: Search query
            api_source: API source name
            ttl_hours: Time-to-live in hours

        Returns:
            Sample SearchCacheDTO instance
        """
        now = datetime.utcnow()
        sample_results = [
            {
                "title": f"{query} announces new product launch",
                "url": "https://example.com/article1",
                "source": "TechCrunch",
                "published_at": now.isoformat(),
            },
            {
                "title": f"{query} raises $50M in Series B funding",
                "url": "https://example.com/article2",
                "source": "Reuters",
                "published_at": (now - timedelta(days=2)).isoformat(),
            },
            {
                "title": f"{query} partners with major enterprise",
                "url": "https://example.com/article3",
                "source": "Bloomberg",
                "published_at": (now - timedelta(days=5)).isoformat(),
            },
        ]

        return cls(
            query=query,
            api_source=api_source,
            results=sample_results,
            cached_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
            result_count=len(sample_results),
            metadata={
                "api_response_time_ms": 245,
                "total_results_available": 156,
                "results_returned": 3,
            },
        )

    def refresh(self, new_results: List[Dict[str, Any]], ttl_hours: int = 24) -> None:
        """
        Refresh the cache with new results.

        Args:
            new_results: New search results
            ttl_hours: New time-to-live in hours
        """
        self.results = new_results
        self.result_count = len(new_results)
        self.cached_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

    def extend_expiry(self, hours: int = 24) -> None:
        """
        Extend the cache expiry time.

        Args:
            hours: Number of hours to extend
        """
        self.expires_at = self.expires_at + timedelta(hours=hours)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "SearchCacheDTO":
        """Create SearchCacheDTO from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_cache_age(self) -> timedelta:
        """Get the age of the cache entry."""
        return datetime.utcnow() - self.cached_at

    def __str__(self) -> str:
        """String representation."""
        expired_str = "EXPIRED" if self.is_expired() else "VALID"
        return f"SearchCache(query='{self.query[:30]}...', source={self.api_source}, status={expired_str}, results={self.result_count})"
