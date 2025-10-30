"""Event data transfer object (DTO) with dataclass implementation."""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Literal, Optional


@dataclass
class EventDTO:
    """
    Event data transfer object for business logic.
    Represents a business event for a client company.
    """

    id: str
    client_id: str
    event_type: Literal["funding", "acquisition", "leadership", "product", "news", "other"]
    title: str
    summary: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    published_date: datetime = field(default_factory=datetime.utcnow)
    discovered_date: datetime = field(default_factory=datetime.utcnow)
    relevance_score: float = 0.5  # 0.0 to 1.0
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    status: Literal["new", "reviewed", "actioned", "archived"] = "new"
    tags: List[str] = field(default_factory=list)
    user_notes: Optional[str] = None

    # Additional metadata
    sentiment_score: Optional[float] = None  # -1.0 to 1.0 (more granular than sentiment)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation with ISO format dates
        """
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.published_date:
            data["published_date"] = self.published_date.isoformat()
        if self.discovered_date:
            data["discovered_date"] = self.discovered_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventDTO":
        """
        Create EventDTO from dictionary.

        Args:
            data: Dictionary with event data

        Returns:
            EventDTO instance
        """
        # Parse datetime strings
        if isinstance(data.get("published_date"), str):
            data["published_date"] = datetime.fromisoformat(data["published_date"])
        if isinstance(data.get("discovered_date"), str):
            data["discovered_date"] = datetime.fromisoformat(data["discovered_date"])

        return cls(**data)

    def is_relevant(self, threshold: float = 0.5) -> bool:
        """
        Check if event meets relevance threshold.

        Args:
            threshold: Minimum relevance score (0.0 to 1.0)

        Returns:
            True if event is relevant
        """
        return self.relevance_score >= threshold

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate event data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.title or len(self.title.strip()) == 0:
            return False, "Event title is required"

        if len(self.title) > 500:
            return False, "Title must be 500 characters or less"

        valid_event_types = [
            "funding", "acquisition", "leadership", "product",
            "partnership", "financial", "award", "regulatory", "news", "other"
        ]
        if self.event_type not in valid_event_types:
            return False, "Invalid event type"

        if not 0.0 <= self.relevance_score <= 1.0:
            return False, "Relevance score must be between 0.0 and 1.0"

        if self.sentiment not in ["positive", "neutral", "negative"]:
            return False, "Sentiment must be positive, neutral, or negative"

        if self.sentiment_score is not None and not -1.0 <= self.sentiment_score <= 1.0:
            return False, "Sentiment score must be between -1.0 and 1.0"

        if self.status not in ["new", "reviewed", "actioned", "archived"]:
            return False, "Invalid status"

        return True, None

    @classmethod
    def create_sample(
        cls,
        client_id: str = None,
        event_type: str = "product",
        relevance_score: float = 0.8,
    ) -> "EventDTO":
        """
        Factory method to create a sample event for testing.

        Args:
            client_id: Client ID (generates random UUID if None)
            event_type: Type of event
            relevance_score: Relevance score

        Returns:
            Sample EventDTO instance
        """
        if client_id is None:
            client_id = str(uuid.uuid4())

        return cls(
            id=str(uuid.uuid4()),
            client_id=client_id,
            event_type=event_type,  # type: ignore
            title="Sample Company Launches New AI Platform",
            summary="Sample Company announced the launch of their new AI-powered platform designed to revolutionize enterprise operations. The platform integrates machine learning capabilities with existing business tools.",
            source_url="https://techcrunch.com/sample-article",
            source_name="TechCrunch",
            published_date=datetime.utcnow(),
            discovered_date=datetime.utcnow(),
            relevance_score=relevance_score,
            sentiment="positive",
            status="new",
            tags=["AI", "platform", "product launch"],
            user_notes=None,
            sentiment_score=0.7,
            metadata={
                "word_count": 450,
                "image_url": "https://example.com/image.jpg",
                "author": "Jane Smith",
            },
        )

    def get_relevance_label(self) -> str:
        """Get human-readable relevance label."""
        if self.relevance_score >= 0.7:
            return "high"
        elif self.relevance_score >= 0.4:
            return "medium"
        else:
            return "low"

    def get_sentiment_emoji(self) -> str:
        """Get emoji representation of sentiment."""
        sentiment_map = {
            "positive": "😊",
            "neutral": "😐",
            "negative": "😟",
        }
        return sentiment_map.get(self.sentiment, "❓")

    def mark_as_reviewed(self) -> None:
        """Mark event as reviewed."""
        self.status = "reviewed"

    def mark_as_actioned(self) -> None:
        """Mark event as actioned."""
        self.status = "actioned"

    def archive(self) -> None:
        """Archive the event."""
        self.status = "archived"

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "EventDTO":
        """Create EventDTO from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation."""
        return f"Event({self.title[:50]}..., type={self.event_type}, relevance={self.relevance_score:.2f})"
