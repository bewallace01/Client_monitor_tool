"""Notification log model for tracking sent notifications."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal
import uuid


@dataclass
class NotificationLog:
    """Represents a log entry for a sent notification."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: Optional[str] = None
    rule_name: str = ""
    notification_type: Literal["email", "in_app", "alert"] = "email"
    recipient: str = ""
    subject: str = ""
    content: str = ""
    status: Literal["sent", "failed", "pending"] = "pending"
    error_message: Optional[str] = None
    sent_at: datetime = field(default_factory=datetime.utcnow)
    event_id: Optional[str] = None  # Associated event if applicable

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "notification_type": self.notification_type,
            "recipient": self.recipient,
            "subject": self.subject,
            "content": self.content,
            "status": self.status,
            "error_message": self.error_message,
            "sent_at": self.sent_at.isoformat(),
            "event_id": self.event_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationLog":
        """Create from dictionary."""
        if isinstance(data.get("sent_at"), str):
            data["sent_at"] = datetime.fromisoformat(data["sent_at"])
        return cls(**data)
