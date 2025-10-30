"""Storage layer for Client Intelligence Monitor."""

# Legacy SQLAlchemy-based storage (existing)
from .database import Database
from .repository import ClientRepository, EventRepository, SearchCacheRepository

# New DTO-based storage (SQLite)
from .base import BaseStorage
from .sqlite_store import SQLiteStorage

__all__ = [
    # Legacy (SQLAlchemy ORM)
    "Database",
    "ClientRepository",
    "EventRepository",
    "SearchCacheRepository",
    # New (DTO-based)
    "BaseStorage",
    "SQLiteStorage",
]
