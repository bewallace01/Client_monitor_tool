"""
Abstract base interface for storage implementations.
Defines the contract for all storage backends.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models import ClientDTO, EventDTO, SearchCacheDTO


class BaseStorage(ABC):
    """Abstract base class for storage implementations."""

    # ==================== Connection Management ====================

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the storage backend.

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close connection to the storage backend.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to storage backend.

        Returns:
            bool: True if connected, False otherwise
        """
        pass

    # ==================== Database Management ====================

    @abstractmethod
    def initialize_database(self) -> None:
        """
        Initialize database schema (create tables, indices, etc.).

        Raises:
            RuntimeError: If initialization fails
        """
        pass

    @abstractmethod
    def drop_all_tables(self) -> None:
        """
        Drop all tables from the database. USE WITH CAUTION!

        Raises:
            RuntimeError: If operation fails
        """
        pass

    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database.

        Returns:
            dict: Database metadata (size, tables, version, etc.)
        """
        pass

    # ==================== Client CRUD Operations ====================

    @abstractmethod
    def create_client(self, client: ClientDTO) -> ClientDTO:
        """
        Create a new client record.

        Args:
            client: ClientDTO instance to create

        Returns:
            ClientDTO: Created client with database ID

        Raises:
            ValueError: If client validation fails
            RuntimeError: If database operation fails
        """
        pass

    @abstractmethod
    def get_client(self, client_id: str) -> Optional[ClientDTO]:
        """
        Retrieve a client by ID.

        Args:
            client_id: Client UUID

        Returns:
            ClientDTO if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_clients(self, active_only: bool = True) -> List[ClientDTO]:
        """
        Retrieve all clients.

        Args:
            active_only: If True, return only active clients

        Returns:
            List of ClientDTO instances
        """
        pass

    @abstractmethod
    def update_client(self, client_id: str, updates: Dict[str, Any]) -> Optional[ClientDTO]:
        """
        Update a client record.

        Args:
            client_id: Client UUID
            updates: Dictionary of fields to update

        Returns:
            Updated ClientDTO if found, None otherwise

        Raises:
            ValueError: If updates are invalid
        """
        pass

    @abstractmethod
    def delete_client(self, client_id: str) -> bool:
        """
        Delete a client record.

        Args:
            client_id: Client UUID

        Returns:
            bool: True if deleted, False if not found
        """
        pass

    @abstractmethod
    def search_clients(self, query: str) -> List[ClientDTO]:
        """
        Search clients by name or keywords.

        Args:
            query: Search query string

        Returns:
            List of matching ClientDTO instances
        """
        pass

    # ==================== Event CRUD Operations ====================

    @abstractmethod
    def create_event(self, event: EventDTO) -> EventDTO:
        """
        Create a new event record.

        Args:
            event: EventDTO instance to create

        Returns:
            EventDTO: Created event with database ID

        Raises:
            ValueError: If event validation fails
            RuntimeError: If database operation fails
        """
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[EventDTO]:
        """
        Retrieve an event by ID.

        Args:
            event_id: Event UUID

        Returns:
            EventDTO if found, None otherwise
        """
        pass

    @abstractmethod
    def get_events_by_client(
        self,
        client_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[EventDTO]:
        """
        Retrieve events for a specific client.

        Args:
            client_id: Client UUID
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of EventDTO instances
        """
        pass

    @abstractmethod
    def get_recent_events(
        self,
        days: int = 7,
        min_relevance: float = 0.0,
        limit: int = 100
    ) -> List[EventDTO]:
        """
        Retrieve recent events across all clients.

        Args:
            days: Number of days to look back
            min_relevance: Minimum relevance score (0.0-1.0)
            limit: Maximum number of events

        Returns:
            List of EventDTO instances sorted by date (newest first)
        """
        pass

    @abstractmethod
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[EventDTO]:
        """
        Update an event record.

        Args:
            event_id: Event UUID
            updates: Dictionary of fields to update

        Returns:
            Updated EventDTO if found, None otherwise
        """
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event record.

        Args:
            event_id: Event UUID

        Returns:
            bool: True if deleted, False if not found
        """
        pass

    @abstractmethod
    def search_events(
        self,
        query: str,
        client_id: Optional[str] = None
    ) -> List[EventDTO]:
        """
        Search events by title or summary.

        Args:
            query: Search query string
            client_id: Optional client ID to filter by

        Returns:
            List of matching EventDTO instances
        """
        pass

    # ==================== Cache CRUD Operations ====================

    @abstractmethod
    def create_cache(self, cache: SearchCacheDTO) -> SearchCacheDTO:
        """
        Create a new cache entry.

        Args:
            cache: SearchCacheDTO instance to create

        Returns:
            SearchCacheDTO: Created cache entry
        """
        pass

    @abstractmethod
    def get_cache(self, query_hash: str) -> Optional[SearchCacheDTO]:
        """
        Retrieve cache entry by query hash.

        Args:
            query_hash: SHA256 hash of query

        Returns:
            SearchCacheDTO if found and not expired, None otherwise
        """
        pass

    @abstractmethod
    def delete_expired_cache(self) -> int:
        """
        Delete all expired cache entries.

        Returns:
            int: Number of entries deleted
        """
        pass

    @abstractmethod
    def clear_all_cache(self) -> int:
        """
        Delete all cache entries.

        Returns:
            int: Number of entries deleted
        """
        pass

    # ==================== Statistics & Analytics ====================

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            dict: Statistics including counts, sizes, etc.
        """
        pass

    @abstractmethod
    def get_client_statistics(self, client_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific client.

        Args:
            client_id: Client UUID

        Returns:
            dict: Client-specific statistics
        """
        pass
