"""Base collector interface for event collection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CollectorResult:
    """Result from a news/event collection."""
    title: str
    description: Optional[str]
    url: Optional[str]
    source: str
    published_at: datetime
    raw_data: Optional[dict] = None  # Original API response for debugging


class BaseCollector(ABC):
    """Abstract base class for event collectors."""

    @abstractmethod
    def search(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        max_results: int = 20,
    ) -> List[CollectorResult]:
        """
        Search for news/events matching the query.

        Args:
            query: Search query string
            from_date: Start date for search (inclusive)
            to_date: End date for search (inclusive)
            max_results: Maximum number of results to return

        Returns:
            List of CollectorResult objects
        """
        pass

    @abstractmethod
    def get_company_news(
        self,
        company_name: str,
        from_date: Optional[datetime] = None,
        max_results: int = 20,
    ) -> List[CollectorResult]:
        """
        Get news specifically about a company.

        Args:
            company_name: Name of the company
            from_date: Start date for search
            max_results: Maximum number of results

        Returns:
            List of CollectorResult objects
        """
        pass

    @property
    @abstractmethod
    def collector_name(self) -> str:
        """Name of the collector implementation."""
        pass

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """Whether this is a mock/fake data collector."""
        pass

    @abstractmethod
    def get_rate_limit_status(self) -> dict:
        """
        Get current rate limit status for this collector.

        Returns:
            Dictionary with keys:
                - limit: Total requests allowed per time window
                - remaining: Requests remaining in current window
                - reset_at: When the limit resets (datetime)
                - enabled: Whether rate limiting is enabled
        """
        pass
