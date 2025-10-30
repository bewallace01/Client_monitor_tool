"""Data models for Client Intelligence Monitor."""

# SQLAlchemy ORM Models (for database)
from .client import Client
from .event import Event, EventCategory
from .search_cache import SearchCache

# Data Transfer Objects (for business logic)
from .client_dto import ClientDTO
from .event_dto import EventDTO
from .cache_dto import SearchCacheDTO

__all__ = [
    # ORM Models
    "Client",
    "Event",
    "EventCategory",
    "SearchCache",
    # DTOs
    "ClientDTO",
    "EventDTO",
    "SearchCacheDTO",
]
