"""Event relevance scoring module - calculates how relevant an event is to a client."""

from datetime import datetime, timedelta
from typing import Optional


def calculate_relevance_score(
    event_title: str,
    event_summary: str,
    event_type: str,
    client_name: str,
    client_industry: Optional[str] = None,
    event_date: Optional[datetime] = None,
    sentiment: str = "neutral"
) -> float:
    """
    Calculate relevance score for an event based on multiple factors.

    Scoring factors:
    1. Text relevance (client name/industry mentions): 0-40 points
    2. Event type importance: 0-30 points
    3. Recency: 0-20 points
    4. Sentiment impact: 0-10 points

    Args:
        event_title: Event title
        event_summary: Event summary/description
        event_type: Event type (funding, acquisition, etc.)
        client_name: Client company name
        client_industry: Client industry (optional)
        event_date: Event date (optional, for recency scoring)
        sentiment: Event sentiment (positive, negative, neutral)

    Returns:
        Relevance score from 0.0 to 1.0
    """
    score = 0.0
    text = f"{event_title} {event_summary}".lower()
    client_lower = client_name.lower()

    # 1. Text Relevance (0-40 points)
    text_score = 0.0

    # Direct client name mention
    if client_lower in text:
        text_score += 40.0
    # Partial client name match (e.g., "Acme" in "Acme Corporation")
    elif any(word in text for word in client_lower.split() if len(word) > 3):
        text_score += 25.0
    # Industry match
    elif client_industry and client_industry.lower() in text:
        text_score += 15.0

    score += text_score

    # 2. Event Type Importance (0-30 points)
    event_type_weights = {
        "funding": 30.0,       # High importance
        "acquisition": 30.0,   # High importance
        "financial": 25.0,     # High importance
        "leadership": 20.0,    # Medium-high importance
        "partnership": 20.0,   # Medium-high importance
        "regulatory": 20.0,    # Medium-high importance
        "product": 15.0,       # Medium importance
        "award": 10.0,         # Lower importance
        "news": 5.0,           # Lowest importance
    }

    event_score = event_type_weights.get(event_type.lower(), 5.0)
    score += event_score

    # 3. Recency (0-20 points)
    recency_score = 0.0
    if event_date:
        now = datetime.now()
        days_old = (now - event_date).days

        if days_old <= 1:
            recency_score = 20.0      # Today/yesterday
        elif days_old <= 7:
            recency_score = 15.0      # This week
        elif days_old <= 30:
            recency_score = 10.0      # This month
        elif days_old <= 90:
            recency_score = 5.0       # This quarter
        else:
            recency_score = 2.0       # Older

    score += recency_score

    # 4. Sentiment Impact (0-10 points)
    sentiment_weights = {
        "positive": 10.0,
        "neutral": 5.0,
        "negative": 8.0,  # Negative news can be highly relevant
    }

    sentiment_score = sentiment_weights.get(sentiment.lower(), 5.0)
    score += sentiment_score

    # Normalize to 0.0-1.0 range (max possible score is 100)
    normalized_score = min(1.0, score / 100.0)

    return round(normalized_score, 2)


def calculate_priority_score(
    relevance_score: float,
    event_type: str,
    sentiment: str = "neutral",
    is_urgent: bool = False
) -> float:
    """
    Calculate priority score for an event (used for sorting/filtering).

    Priority considers:
    1. Base relevance score: 0-60 points
    2. Event type urgency: 0-20 points
    3. Sentiment: 0-10 points
    4. Urgent flag: 0-10 points

    Args:
        relevance_score: Base relevance score (0.0-1.0)
        event_type: Event type
        sentiment: Event sentiment
        is_urgent: Whether event is marked as urgent

    Returns:
        Priority score from 0.0 to 1.0
    """
    score = 0.0

    # 1. Base relevance (0-60 points)
    score += relevance_score * 60.0

    # 2. Event type urgency (0-20 points)
    urgency_weights = {
        "regulatory": 20.0,    # Most urgent
        "financial": 18.0,
        "acquisition": 16.0,
        "funding": 14.0,
        "leadership": 12.0,
        "partnership": 10.0,
        "product": 8.0,
        "award": 6.0,
        "news": 4.0,
    }

    urgency_score = urgency_weights.get(event_type.lower(), 4.0)
    score += urgency_score

    # 3. Sentiment (0-10 points)
    # Negative and positive news both increase priority
    sentiment_weights = {
        "positive": 8.0,
        "negative": 10.0,  # Negative news is slightly higher priority
        "neutral": 5.0,
    }

    sentiment_score = sentiment_weights.get(sentiment.lower(), 5.0)
    score += sentiment_score

    # 4. Urgent flag (0-10 points)
    if is_urgent:
        score += 10.0

    # Normalize to 0.0-1.0 range (max possible score is 100)
    normalized_score = min(1.0, score / 100.0)

    return round(normalized_score, 2)


def analyze_event_sentiment(title: str, summary: str = "") -> str:
    """
    Analyze sentiment of an event (simple keyword-based approach).

    Args:
        title: Event title
        summary: Event summary/description

    Returns:
        Sentiment: "positive", "negative", or "neutral"
    """
    text = f"{title} {summary}".lower()

    # Positive keywords
    positive_keywords = [
        "success", "growth", "expansion", "wins", "award", "partnership",
        "innovation", "launch", "record", "breakthrough", "achievement",
        "profit", "revenue growth", "beats", "exceeds", "outperforms",
        "celebrates", "milestone", "leading", "best", "top"
    ]

    # Negative keywords
    negative_keywords = [
        "loss", "lawsuit", "investigation", "fine", "penalty", "breach",
        "decline", "drop", "miss", "disappoints", "fail", "crisis",
        "scandal", "controversy", "layoff", "closure", "bankruptcy",
        "warning", "concern", "problem", "issue", "delay"
    ]

    positive_count = sum(1 for keyword in positive_keywords if keyword in text)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text)

    # Determine sentiment based on keyword counts
    if positive_count > negative_count and positive_count > 0:
        return "positive"
    elif negative_count > positive_count and negative_count > 0:
        return "negative"
    else:
        return "neutral"


def should_notify(
    relevance_score: float,
    priority_score: float,
    min_relevance: float = 0.5,
    min_priority: float = 0.5
) -> bool:
    """
    Determine if an event should trigger a notification.

    Args:
        relevance_score: Event relevance score (0.0-1.0)
        priority_score: Event priority score (0.0-1.0)
        min_relevance: Minimum relevance threshold
        min_priority: Minimum priority threshold

    Returns:
        True if notification should be sent, False otherwise
    """
    # Event must meet BOTH thresholds to trigger notification
    return relevance_score >= min_relevance and priority_score >= min_priority
