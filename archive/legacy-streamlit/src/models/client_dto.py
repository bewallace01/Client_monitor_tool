"""Client data transfer object (DTO) with dataclass implementation."""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Literal, Optional


@dataclass
class ClientDTO:
    """
    Client data transfer object for business logic.
    Separate from SQLAlchemy ORM model for flexibility.
    """

    id: str
    name: str
    industry: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"
    keywords: List[str] = field(default_factory=list)
    monitoring_since: datetime = field(default_factory=datetime.utcnow)
    last_checked: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Additional fields for CS management
    domain: Optional[str] = None
    description: Optional[str] = None
    account_owner: Optional[str] = None
    tier: Optional[str] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation with ISO format dates
        """
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.monitoring_since:
            data["monitoring_since"] = self.monitoring_since.isoformat()
        if self.last_checked:
            data["last_checked"] = self.last_checked.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientDTO":
        """
        Create ClientDTO from dictionary.

        Args:
            data: Dictionary with client data

        Returns:
            ClientDTO instance
        """
        # Parse datetime strings
        if isinstance(data.get("monitoring_since"), str):
            data["monitoring_since"] = datetime.fromisoformat(data["monitoring_since"])
        if isinstance(data.get("last_checked"), str):
            data["last_checked"] = datetime.fromisoformat(data["last_checked"])

        return cls(**data)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate client data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Client name is required"

        if len(self.name) > 200:
            return False, "Client name must be 200 characters or less"

        if self.priority not in ["high", "medium", "low"]:
            return False, "Priority must be high, medium, or low"

        if self.domain and len(self.domain) > 200:
            return False, "Domain must be 200 characters or less"

        # Validate keywords
        if not isinstance(self.keywords, list):
            return False, "Keywords must be a list"

        return True, None

    @classmethod
    def create_sample(cls, name: str = "Sample Corp", priority: str = "medium") -> "ClientDTO":
        """
        Factory method to create a sample client for testing.

        Args:
            name: Client name
            priority: Priority level

        Returns:
            Sample ClientDTO instance
        """
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            industry="Technology",
            priority=priority,  # type: ignore
            keywords=["AI", "cloud", "enterprise"],
            monitoring_since=datetime.utcnow(),
            last_checked=None,
            metadata={
                "company_size": "500-1000",
                "headquarters": "San Francisco, CA",
                "founded": 2015,
            },
            domain=f"{name.lower().replace(' ', '')}.com",
            description=f"{name} is a leading technology company.",
            account_owner="Sample Owner",
            tier="Enterprise",
            is_active=True,
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ClientDTO":
        """Create ClientDTO from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation."""
        return f"Client({self.name}, priority={self.priority}, industry={self.industry})"
