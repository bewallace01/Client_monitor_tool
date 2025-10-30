"""Event collector implementations."""

from .base import BaseCollector, CollectorResult
from .mock_collector import MockCollector
from .google_search import GoogleSearchCollector
from .news_api import NewsAPICollector
from .factory import get_collector, list_available_collectors

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "MockCollector",
    "GoogleSearchCollector",
    "NewsAPICollector",
    "get_collector",
    "list_available_collectors",
]
