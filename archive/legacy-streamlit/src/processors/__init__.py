"""Event processing modules."""

from .event_classifier import classify_event
from .relevance_scorer import calculate_relevance
from .deduplicator import is_duplicate

__all__ = ['classify_event', 'calculate_relevance', 'is_duplicate']
