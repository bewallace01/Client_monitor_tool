"""Notification rule model for automated alerts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Literal
import uuid


@dataclass
class NotificationRule:
    """Represents a notification rule for automated alerts."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    is_active: bool = True

    # Trigger conditions
    event_types: List[str] = field(default_factory=list)  # Categories to monitor
    min_relevance_score: float = 0.7  # Minimum relevance to trigger
    client_ids: List[str] = field(default_factory=list)  # Specific clients (empty = all)
    keywords: List[str] = field(default_factory=list)  # Keywords to match in events

    # Notification settings
    frequency: Literal["immediate", "hourly", "daily", "weekly"] = "immediate"
    recipient_emails: List[str] = field(default_factory=list)
    notification_type: Literal["email", "digest"] = "email"

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def matches_event(self, event) -> bool:
        """
        Check if an event matches this notification rule.

        Args:
            event: EventDTO to check

        Returns:
            bool: True if event matches all criteria
        """
        # Check if rule is active
        if not self.is_active:
            return False

        # Check relevance score
        if event.relevance_score < self.min_relevance_score:
            return False

        # Check event types (if specified)
        if self.event_types and hasattr(event, 'event_type'):
            if event.event_type not in self.event_types:
                return False

        # Check client IDs (if specified)
        if self.client_ids and event.client_id not in self.client_ids:
            return False

        # Check keywords (if specified)
        if self.keywords:
            # Use event.summary (not description) for EventDTO compatibility
            event_text = f"{event.title} {event.summary or ''}".lower()
            if not any(keyword.lower() in event_text for keyword in self.keywords):
                return False

        return True

    def should_trigger_now(self, last_notification_time: Optional[datetime] = None) -> bool:
        """
        Check if notification should be sent based on frequency settings.

        Args:
            last_notification_time: Time of last notification for this rule

        Returns:
            bool: True if notification should be sent now
        """
        if self.frequency == "immediate":
            return True

        if last_notification_time is None:
            return True

        now = datetime.utcnow()
        time_diff = now - last_notification_time

        if self.frequency == "hourly":
            return time_diff.total_seconds() >= 3600
        elif self.frequency == "daily":
            return time_diff.total_seconds() >= 86400
        elif self.frequency == "weekly":
            return time_diff.total_seconds() >= 604800

        return False

    def mark_triggered(self):
        """Mark this rule as triggered and update counters."""
        self.last_triggered = datetime.utcnow()
        self.trigger_count += 1
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "event_types": self.event_types,
            "min_relevance_score": self.min_relevance_score,
            "client_ids": self.client_ids,
            "keywords": self.keywords,
            "frequency": self.frequency,
            "recipient_emails": self.recipient_emails,
            "notification_type": self.notification_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationRule":
        """Create from dictionary."""
        # Parse datetime fields
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("last_triggered") and isinstance(data["last_triggered"], str):
            data["last_triggered"] = datetime.fromisoformat(data["last_triggered"])

        return cls(**data)
