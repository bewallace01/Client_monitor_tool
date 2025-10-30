"""Relevance scoring logic."""

from datetime import datetime, timedelta
from typing import Tuple

from src.models.event_dto import EventDTO
from src.models.client_dto import ClientDTO


# Reputable news sources
REPUTABLE_SOURCES = [
    "TechCrunch", "Reuters", "Bloomberg", "The Wall Street Journal",
    "Financial Times", "Forbes", "CNBC", "Business Wire", "PR Newswire",
    "VentureBeat", "The Information", "Axios", "The Verge", "Wired"
]

# High-value event types
HIGH_VALUE_EVENT_TYPES = ["funding", "acquisition", "partnership"]


def calculate_relevance(
    event: EventDTO,
    client: ClientDTO
) -> Tuple[float, str]:
    """
    Calculate relevance score for an event.

    Args:
        event: Event to score
        client: Client the event belongs to

    Returns:
        Tuple of (score, explanation)
    """
    score = 0.0
    explanations = []

    # Factor 1: Client name exact match in title (+0.4)
    if client.name.lower() in event.title.lower():
        score += 0.4
        explanations.append(f"Client name '{client.name}' in title (+0.4)")

    # Factor 2: Client name in summary (+0.2)
    if client.name.lower() in event.summary.lower():
        score += 0.2
        explanations.append(f"Client name '{client.name}' in summary (+0.2)")

    # Factor 3: Reputable source (+0.2)
    if event.source_name in REPUTABLE_SOURCES:
        score += 0.2
        explanations.append(f"Reputable source '{event.source_name}' (+0.2)")

    # Factor 4: Recent event < 7 days (+0.1)
    days_old = (datetime.utcnow() - event.published_date).days
    if days_old < 7:
        score += 0.1
        explanations.append(f"Recent event ({days_old} days old) (+0.1)")

    # Factor 5: High-value event type (+0.1)
    if event.event_type in HIGH_VALUE_EVENT_TYPES:
        score += 0.1
        explanations.append(f"High-value event type '{event.event_type}' (+0.1)")

    # Cap score at 1.0
    score = min(score, 1.0)

    # Create explanation
    explanation = " | ".join(explanations) if explanations else "No relevance factors found"

    return round(score, 2), explanation


def update_event_relevance(
    event: EventDTO,
    client: ClientDTO
) -> EventDTO:
    """
    Update event with calculated relevance score.

    Args:
        event: Event to update
        client: Client the event belongs to

    Returns:
        Updated event with relevance score
    """
    score, explanation = calculate_relevance(event, client)
    event.relevance_score = score

    # Add explanation to metadata
    if event.metadata is None:
        event.metadata = {}
    event.metadata["relevance_explanation"] = explanation

    return event
