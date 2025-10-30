"""Event deduplication logic."""

from typing import List
from difflib import SequenceMatcher

from src.models.event_dto import EventDTO


def is_duplicate(
    new_event: EventDTO,
    existing_events: List[EventDTO],
    url_match: bool = True,
    title_similarity_threshold: float = 0.85
) -> bool:
    """
    Check if an event is a duplicate of existing events.

    Args:
        new_event: Event to check
        existing_events: List of existing events to compare against
        url_match: Whether to check URL exact match (default: True)
        title_similarity_threshold: Minimum similarity ratio for title match (default: 0.85)

    Returns:
        True if duplicate found, False otherwise
    """
    for existing in existing_events:
        # Check 1: URL exact match
        if url_match and new_event.source_url and existing.source_url:
            if new_event.source_url == existing.source_url:
                return True

        # Check 2: Title similarity
        similarity = _calculate_similarity(new_event.title, existing.title)
        if similarity >= title_similarity_threshold:
            return True

    return False


def _calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity ratio between two strings.

    Args:
        text1: First string
        text2: Second string

    Returns:
        Similarity ratio between 0.0 and 1.0
    """
    # Normalize texts
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()

    # Use SequenceMatcher for similarity calculation
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def filter_duplicates(
    new_events: List[EventDTO],
    existing_events: List[EventDTO]
) -> List[EventDTO]:
    """
    Filter out duplicate events from a list of new events.

    Args:
        new_events: List of new events to filter
        existing_events: List of existing events to compare against

    Returns:
        List of unique events (duplicates removed)
    """
    unique_events = []

    for new_event in new_events:
        # Check against existing events
        if not is_duplicate(new_event, existing_events):
            # Also check against already processed new events
            if not is_duplicate(new_event, unique_events):
                unique_events.append(new_event)

    return unique_events
