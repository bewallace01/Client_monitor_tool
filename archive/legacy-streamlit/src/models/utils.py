"""Utility functions for model operations."""

import uuid
from typing import Union, Optional
from datetime import datetime, timedelta

from .client import Client
from .event import Event
from .search_cache import SearchCache
from .client_dto import ClientDTO
from .event_dto import EventDTO
from .cache_dto import SearchCacheDTO


def generate_uuid() -> str:
    """
    Generate a new UUID string.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def orm_to_client_dto(orm_client: Client) -> ClientDTO:
    """
    Convert SQLAlchemy Client ORM to ClientDTO.

    Args:
        orm_client: SQLAlchemy Client instance

    Returns:
        ClientDTO instance
    """
    import json

    # Parse keywords from JSON string if stored as JSON
    keywords = []
    if orm_client.search_keywords:
        try:
            keywords = json.loads(orm_client.search_keywords)
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON, treat as comma-separated string
            keywords = [k.strip() for k in orm_client.search_keywords.split(",") if k.strip()]

    # Map tier to priority (you can customize this mapping)
    priority_map = {
        "Enterprise": "high",
        "Mid-Market": "medium",
        "SMB": "low",
    }
    priority = priority_map.get(orm_client.tier, "medium")

    return ClientDTO(
        id=str(orm_client.id),  # Convert int to string for DTO
        name=orm_client.name,
        industry=orm_client.industry,
        priority=priority,  # type: ignore
        keywords=keywords,
        monitoring_since=orm_client.created_at,
        last_checked=orm_client.last_checked_at,
        metadata={
            "description": orm_client.description,
            "notes": orm_client.notes,
        },
        domain=orm_client.domain,
        description=orm_client.description,
        account_owner=orm_client.account_owner,
        tier=orm_client.tier,
        is_active=orm_client.is_active,
    )


def orm_to_event_dto(orm_event: Event) -> EventDTO:
    """
    Convert SQLAlchemy Event ORM to EventDTO.

    Args:
        orm_event: SQLAlchemy Event instance

    Returns:
        EventDTO instance
    """
    # Map ORM category to DTO event_type
    event_type_map = {
        "funding": "funding",
        "acquisition": "acquisition",
        "leadership_change": "leadership",
        "product_launch": "product",
        "partnership": "news",
        "financial_results": "news",
        "regulatory": "news",
        "award": "news",
        "other": "other",
    }
    event_type = event_type_map.get(orm_event.category, "other")

    # Map sentiment score to sentiment label
    sentiment = "neutral"
    if orm_event.sentiment_score is not None:
        if orm_event.sentiment_score > 0.3:
            sentiment = "positive"
        elif orm_event.sentiment_score < -0.3:
            sentiment = "negative"

    # Map read/starred status to DTO status
    if orm_event.is_starred:
        status = "actioned"
    elif orm_event.is_read:
        status = "reviewed"
    else:
        status = "new"

    return EventDTO(
        id=str(orm_event.id),  # Convert int to string
        client_id=str(orm_event.client_id),  # Convert int to string
        event_type=event_type,  # type: ignore
        title=orm_event.title,
        summary=orm_event.description,
        source_url=orm_event.url,
        source_name=orm_event.source,
        published_date=orm_event.event_date,
        discovered_date=orm_event.discovered_at,
        relevance_score=orm_event.relevance_score,
        sentiment=sentiment,  # type: ignore
        status=status,  # type: ignore
        tags=[],  # ORM doesn't have tags yet
        user_notes=orm_event.user_notes,
        sentiment_score=orm_event.sentiment_score,
        metadata={
            "content_hash": orm_event.content_hash,
            "category": orm_event.category,
        },
    )


def orm_to_cache_dto(orm_cache: SearchCache) -> SearchCacheDTO:
    """
    Convert SQLAlchemy SearchCache ORM to SearchCacheDTO.

    Args:
        orm_cache: SQLAlchemy SearchCache instance

    Returns:
        SearchCacheDTO instance
    """
    import json

    # Parse results from JSON string
    results = []
    if orm_cache.results_json:
        try:
            results = json.loads(orm_cache.results_json)
        except (json.JSONDecodeError, TypeError):
            results = []

    return SearchCacheDTO(
        query=orm_cache.query_text,
        api_source=orm_cache.source,
        results=results,
        cached_at=orm_cache.cached_at,
        expires_at=orm_cache.expires_at,
        result_count=orm_cache.result_count,
        query_hash=orm_cache.query_hash,
        metadata={},
    )


def validate_priority(priority: str) -> bool:
    """
    Validate client priority value.

    Args:
        priority: Priority string

    Returns:
        True if valid
    """
    return priority in ["high", "medium", "low"]


def validate_event_type(event_type: str) -> bool:
    """
    Validate event type value.

    Args:
        event_type: Event type string

    Returns:
        True if valid
    """
    return event_type in ["funding", "acquisition", "leadership", "product", "news", "other"]


def validate_sentiment(sentiment: str) -> bool:
    """
    Validate sentiment value.

    Args:
        sentiment: Sentiment string

    Returns:
        True if valid
    """
    return sentiment in ["positive", "neutral", "negative"]


def validate_status(status: str) -> bool:
    """
    Validate event status value.

    Args:
        status: Status string

    Returns:
        True if valid
    """
    return status in ["new", "reviewed", "actioned", "archived"]


def calculate_cache_expiry(ttl_hours: int = 24) -> datetime:
    """
    Calculate cache expiry datetime.

    Args:
        ttl_hours: Time-to-live in hours

    Returns:
        Expiry datetime
    """
    return datetime.utcnow() + timedelta(hours=ttl_hours)


def is_cache_expired(expires_at: datetime) -> bool:
    """
    Check if cache has expired.

    Args:
        expires_at: Expiry datetime

    Returns:
        True if expired
    """
    return datetime.utcnow() > expires_at


def normalize_relevance_score(score: float) -> float:
    """
    Normalize relevance score to 0.0-1.0 range.

    Args:
        score: Input score

    Returns:
        Normalized score between 0.0 and 1.0
    """
    return max(0.0, min(1.0, score))


def normalize_sentiment_score(score: float) -> float:
    """
    Normalize sentiment score to -1.0 to 1.0 range.

    Args:
        score: Input score

    Returns:
        Normalized score between -1.0 and 1.0
    """
    return max(-1.0, min(1.0, score))


def sentiment_score_to_label(score: Optional[float]) -> str:
    """
    Convert numeric sentiment score to label.

    Args:
        score: Sentiment score (-1.0 to 1.0)

    Returns:
        Sentiment label (positive, neutral, negative)
    """
    if score is None:
        return "neutral"
    if score > 0.3:
        return "positive"
    elif score < -0.3:
        return "negative"
    else:
        return "neutral"


def relevance_score_to_label(score: float) -> str:
    """
    Convert numeric relevance score to label.

    Args:
        score: Relevance score (0.0 to 1.0)

    Returns:
        Relevance label (high, medium, low)
    """
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"


def format_datetime_ago(dt: datetime) -> str:
    """
    Format datetime as human-readable "time ago" string.

    Args:
        dt: Datetime to format

    Returns:
        String like "2 hours ago", "3 days ago"
    """
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"
