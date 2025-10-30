"""Event classification logic."""

import re
from typing import Dict, Optional
from datetime import datetime
import uuid

from src.collectors.base import CollectorResult
from src.models.client_dto import ClientDTO
from src.models.event_dto import EventDTO


# Event type detection keywords
EVENT_TYPE_KEYWORDS = {
    "funding": [
        "raise", "raised", "funding", "series a", "series b", "series c",
        "series d", "investment", "round", "million", "billion", "capital",
        "venture", "investor", "invests", "secures"
    ],
    "acquisition": [
        "acquire", "acquires", "acquired", "acquisition", "merger", "merges",
        "buys", "bought", "purchased", "deal", "takeover"
    ],
    "leadership": [
        "ceo", "cto", "cfo", "executive", "appoint", "appointed", "hire", "hired",
        "joins", "joined", "names", "named", "chief", "director", "president",
        "resignation", "depart", "steps down"
    ],
    "product": [
        "launch", "launches", "launched", "release", "releases", "released",
        "unveils", "unveiled", "announces", "announced", "product", "feature",
        "platform", "service", "introduces"
    ],
    "partnership": [
        "partner", "partnership", "collaboration", "collaborates", "alliance",
        "teams up", "agreement", "deal", "contract"
    ],
    "financial": [
        "earnings", "revenue", "profit", "loss", "quarterly", "q1", "q2", "q3", "q4",
        "financial results", "fiscal", "report", "beats", "misses"
    ],
    "award": [
        "award", "awarded", "wins", "winner", "recognition", "recognizes",
        "honor", "honored", "best", "top"
    ],
    "regulatory": [
        "regulatory", "regulation", "compliance", "fda", "sec", "approval",
        "approved", "license", "lawsuit", "settlement", "fine"
    ],
}

# Sentiment detection keywords
POSITIVE_KEYWORDS = [
    "growth", "grows", "success", "successful", "wins", "win", "expansion",
    "expands", "innovation", "innovative", "breakthrough", "record", "strong",
    "outstanding", "exceeds", "beats", "raises", "secures", "launches", "appoints"
]

NEGATIVE_KEYWORDS = [
    "layoff", "layoffs", "decline", "declines", "loss", "losses", "fails",
    "failed", "cuts", "lawsuit", "fine", "delay", "delays", "misses",
    "departure", "resign", "controversy", "scandal"
]


def classify_event(
    search_result: CollectorResult,
    client: ClientDTO
) -> EventDTO:
    """
    Classify a search result into a structured event.

    Args:
        search_result: Raw search result from collector
        client: Client this event belongs to

    Returns:
        EventDTO with classified event type and sentiment
    """
    # Combine title and description for analysis
    text = f"{search_result.title} {search_result.description or ''}".lower()

    # Detect event type
    event_type = _detect_event_type(text)

    # Detect sentiment
    sentiment = _detect_sentiment(text)
    sentiment_score = _calculate_sentiment_score(text)

    # Create EventDTO
    event = EventDTO(
        id=str(uuid.uuid4()),
        client_id=client.id,
        title=search_result.title,
        summary=search_result.description or "",
        source_name=search_result.source or "Unknown",
        source_url=search_result.url or "",
        published_date=search_result.published_at or datetime.utcnow(),
        discovered_date=datetime.utcnow(),
        event_type=event_type,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        relevance_score=0.5,  # Will be updated by relevance scorer
        status="new",
        tags=[],
        metadata=search_result.raw_data or {}
    )

    return event


def _detect_event_type(text: str) -> str:
    """
    Detect event type from text using keyword matching.

    Args:
        text: Text to analyze (lowercase)

    Returns:
        Event type string
    """
    scores = {}

    for event_type, keywords in EVENT_TYPE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Count occurrences of each keyword
            if keyword in text:
                score += text.count(keyword)
        scores[event_type] = score

    # Return type with highest score, or "news" if no matches
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "news"


def _detect_sentiment(text: str) -> str:
    """
    Detect sentiment from text using keyword matching.

    Args:
        text: Text to analyze (lowercase)

    Returns:
        Sentiment string: "positive", "negative", or "neutral"
    """
    positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text)
    negative_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def _calculate_sentiment_score(text: str) -> float:
    """
    Calculate sentiment score from -1.0 to 1.0.

    Args:
        text: Text to analyze (lowercase)

    Returns:
        Sentiment score
    """
    positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text)
    negative_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)

    total = positive_count + negative_count
    if total == 0:
        return 0.0

    # Normalize to -1.0 to 1.0
    score = (positive_count - negative_count) / total
    return round(score, 2)
