"""
Unit tests for storage layer (SQLiteStorage).
"""

import pytest
from datetime import datetime, timedelta

from src.storage import SQLiteStorage
from src.models import ClientDTO, EventDTO


# ==================== Connection Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestStorageConnection:
    """Tests for database connection management."""

    def test_storage_initialization(self, temp_db_path):
        """Test creating a storage instance."""
        storage = SQLiteStorage(db_path=temp_db_path)
        assert storage.db_path == temp_db_path
        assert storage.is_connected() is False

    def test_storage_connect(self, temp_db_path):
        """Test connecting to database."""
        storage = SQLiteStorage(db_path=temp_db_path)
        storage.connect()
        assert storage.is_connected() is True
        storage.disconnect()

    def test_storage_disconnect(self, test_storage):
        """Test disconnecting from database."""
        assert test_storage.is_connected() is True
        test_storage.disconnect()
        assert test_storage.is_connected() is False

    def test_storage_initialize_database(self, test_storage):
        """Test database schema initialization."""
        # Should complete without errors
        test_storage.initialize_database()

        # Verify tables exist
        db_info = test_storage.get_database_info()
        assert "clients" in db_info["tables"]
        assert "events" in db_info["tables"]


# ==================== Client CRUD Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestClientCRUD:
    """Tests for client CRUD operations."""

    def test_create_client(self, test_storage, sample_client_dto):
        """Test creating a client."""
        created_client = test_storage.create_client(sample_client_dto)

        assert created_client.id == sample_client_dto.id
        assert created_client.name == sample_client_dto.name
        assert created_client.industry == sample_client_dto.industry

    def test_get_client(self, test_storage, sample_client_dto):
        """Test retrieving a client by ID."""
        test_storage.create_client(sample_client_dto)

        retrieved_client = test_storage.get_client(sample_client_dto.id)

        assert retrieved_client is not None
        assert retrieved_client.id == sample_client_dto.id
        assert retrieved_client.name == sample_client_dto.name

    def test_get_client_not_found(self, test_storage):
        """Test retrieving a non-existent client returns None."""
        result = test_storage.get_client("non-existent-id")
        assert result is None

    def test_get_all_clients(self, test_storage, multiple_client_dtos):
        """Test retrieving all clients."""
        for client in multiple_client_dtos:
            test_storage.create_client(client)

        all_clients = test_storage.get_all_clients(active_only=False)

        assert len(all_clients) == len(multiple_client_dtos)

    def test_get_all_clients_active_only(self, test_storage, client_factory):
        """Test retrieving only active clients."""
        # Create active and inactive clients
        active_client = client_factory(id="active-1", is_active=True)
        inactive_client = client_factory(id="inactive-1", is_active=False)

        test_storage.create_client(active_client)
        test_storage.create_client(inactive_client)

        active_clients = test_storage.get_all_clients(active_only=True)

        assert len(active_clients) == 1
        assert active_clients[0].id == "active-1"

    def test_update_client(self, test_storage, sample_client_dto):
        """Test updating a client."""
        test_storage.create_client(sample_client_dto)

        updates = {
            "name": "Updated Name",
            "priority": "low"
        }

        updated_client = test_storage.update_client(sample_client_dto.id, updates)

        assert updated_client is not None
        assert updated_client.name == "Updated Name"
        assert updated_client.priority == "low"

    def test_update_client_not_found(self, test_storage):
        """Test updating a non-existent client returns None."""
        result = test_storage.update_client("non-existent-id", {"name": "Test"})
        assert result is None

    def test_delete_client(self, test_storage, sample_client_dto):
        """Test deleting a client."""
        test_storage.create_client(sample_client_dto)

        result = test_storage.delete_client(sample_client_dto.id)

        assert result is True
        assert test_storage.get_client(sample_client_dto.id) is None

    def test_delete_client_not_found(self, test_storage):
        """Test deleting a non-existent client returns False."""
        result = test_storage.delete_client("non-existent-id")
        assert result is False

    def test_search_clients(self, test_storage, multiple_client_dtos):
        """Test searching clients by query."""
        for client in multiple_client_dtos:
            test_storage.create_client(client)

        # Search by name
        results = test_storage.search_clients("Acme")
        assert len(results) >= 1
        assert any("Acme" in c.name for c in results)

    def test_search_clients_no_results(self, test_storage, multiple_client_dtos):
        """Test searching with no matches."""
        for client in multiple_client_dtos:
            test_storage.create_client(client)

        results = test_storage.search_clients("NonExistent")
        assert len(results) == 0


# ==================== Event CRUD Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestEventCRUD:
    """Tests for event CRUD operations."""

    def test_create_event(self, test_storage, sample_client_dto, sample_event_dto):
        """Test creating an event."""
        test_storage.create_client(sample_client_dto)
        created_event = test_storage.create_event(sample_event_dto)

        assert created_event.id == sample_event_dto.id
        assert created_event.title == sample_event_dto.title
        assert created_event.event_type == sample_event_dto.event_type

    def test_get_event(self, test_storage, sample_client_dto, sample_event_dto):
        """Test retrieving an event by ID."""
        test_storage.create_client(sample_client_dto)
        test_storage.create_event(sample_event_dto)

        retrieved_event = test_storage.get_event(sample_event_dto.id)

        assert retrieved_event is not None
        assert retrieved_event.id == sample_event_dto.id
        assert retrieved_event.title == sample_event_dto.title

    def test_get_event_not_found(self, test_storage):
        """Test retrieving a non-existent event returns None."""
        result = test_storage.get_event("non-existent-id")
        assert result is None

    def test_get_events_by_client(self, populated_storage):
        """Test retrieving events for a specific client."""
        events = populated_storage.get_events_by_client("test-client-1")

        assert len(events) >= 1
        assert all(e.client_id == "test-client-1" for e in events)

    def test_get_recent_events(self, populated_storage):
        """Test retrieving recent events."""
        events = populated_storage.get_recent_events(days=30)

        assert len(events) >= 1
        # All events should be within last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        assert all(e.published_date >= cutoff_date for e in events)

    def test_get_recent_events_with_min_relevance(self, populated_storage):
        """Test retrieving recent events with minimum relevance."""
        events = populated_storage.get_recent_events(days=30, min_relevance=0.8)

        # All events should have relevance >= 0.8
        assert all(e.relevance_score >= 0.8 for e in events)

    def test_get_all_events(self, populated_storage):
        """Test retrieving all events."""
        events = populated_storage.get_all_events()

        assert len(events) >= 3  # Based on fixture data

    def test_update_event(self, test_storage, sample_client_dto, sample_event_dto):
        """Test updating an event."""
        test_storage.create_client(sample_client_dto)
        test_storage.create_event(sample_event_dto)

        updates = {
            "status": "reviewed",
            "user_notes": "Updated notes"
        }

        updated_event = test_storage.update_event(sample_event_dto.id, updates)

        assert updated_event is not None
        assert updated_event.status == "reviewed"
        assert updated_event.user_notes == "Updated notes"

    def test_delete_event(self, test_storage, sample_client_dto, sample_event_dto):
        """Test deleting an event."""
        test_storage.create_client(sample_client_dto)
        test_storage.create_event(sample_event_dto)

        result = test_storage.delete_event(sample_event_dto.id)

        assert result is True
        assert test_storage.get_event(sample_event_dto.id) is None

    def test_search_events(self, populated_storage):
        """Test searching events by query."""
        results = populated_storage.search_events("funding")

        assert len(results) >= 1
        assert any("funding" in e.title.lower() or "funding" in e.summary.lower() for e in results)

    def test_search_events_by_client(self, populated_storage):
        """Test searching events for a specific client."""
        results = populated_storage.search_events("raises", client_id="test-client-1")

        assert len(results) >= 1
        assert all(e.client_id == "test-client-1" for e in results)


# ==================== Statistics Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestStatistics:
    """Tests for database statistics."""

    def test_get_statistics(self, populated_storage):
        """Test retrieving database statistics."""
        stats = populated_storage.get_statistics()

        assert "total_clients" in stats
        assert "active_clients" in stats
        assert "total_events" in stats
        assert "new_events" in stats

        assert stats["total_clients"] >= 3
        assert stats["total_events"] >= 3

    def test_get_client_statistics(self, populated_storage):
        """Test retrieving statistics for a specific client."""
        stats = populated_storage.get_client_statistics("test-client-1")

        assert "total_events" in stats
        assert "events_by_status" in stats
        assert "events_by_type" in stats
        assert "average_relevance" in stats

        assert stats["total_events"] >= 1

    def test_get_database_info(self, test_storage):
        """Test retrieving database info."""
        info = test_storage.get_database_info()

        assert "path" in info
        assert "exists" in info
        assert "size_bytes" in info
        assert "tables" in info

        assert info["exists"] is True
        assert len(info["tables"]) > 0


# ==================== Cascade Delete Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestCascadeOperations:
    """Tests for cascade delete and related operations."""

    def test_delete_client_cascades_to_events(self, test_storage, sample_client_dto, sample_event_dto):
        """Test that deleting a client also deletes its events."""
        test_storage.create_client(sample_client_dto)
        test_storage.create_event(sample_event_dto)

        # Verify event exists
        assert test_storage.get_event(sample_event_dto.id) is not None

        # Delete client
        test_storage.delete_client(sample_client_dto.id)

        # Event should also be deleted
        assert test_storage.get_event(sample_event_dto.id) is None


# ==================== Transaction Tests ====================

@pytest.mark.unit
@pytest.mark.database
class TestTransactions:
    """Tests for transaction handling."""

    def test_rollback_on_error(self, test_storage, client_factory):
        """Test that errors cause rollback."""
        valid_client = client_factory(id="valid-1")
        test_storage.create_client(valid_client)

        # Try to create duplicate - should fail
        with pytest.raises(Exception):
            test_storage.create_client(valid_client)

        # Only one client should exist
        all_clients = test_storage.get_all_clients(active_only=False)
        assert len(all_clients) == 1


# ==================== Edge Cases ====================

@pytest.mark.unit
@pytest.mark.database
class TestStorageEdgeCases:
    """Tests for storage edge cases."""

    def test_client_with_empty_keywords(self, test_storage, client_factory):
        """Test creating client with empty keywords list."""
        client = client_factory(keywords=[])
        created = test_storage.create_client(client)

        retrieved = test_storage.get_client(created.id)
        assert retrieved.keywords == []

    def test_event_with_null_notes(self, test_storage, sample_client_dto, event_factory):
        """Test creating event with null user notes."""
        test_storage.create_client(sample_client_dto)

        event = event_factory(client_id=sample_client_dto.id, user_notes=None)
        created = test_storage.create_event(event)

        retrieved = test_storage.get_event(created.id)
        assert retrieved.user_notes is None

    def test_update_with_empty_dict(self, test_storage, sample_client_dto):
        """Test updating with empty updates dict."""
        test_storage.create_client(sample_client_dto)

        result = test_storage.update_client(sample_client_dto.id, {})

        # Should return the client unchanged
        assert result is not None
        assert result.name == sample_client_dto.name

    def test_special_characters_in_search(self, test_storage, client_factory):
        """Test search with special characters."""
        client = client_factory(name="Test & Co.")
        test_storage.create_client(client)

        results = test_storage.search_clients("&")
        assert len(results) >= 1

    def test_very_long_text_fields(self, test_storage, client_factory):
        """Test storing very long text fields."""
        long_description = "A" * 10000
        client = client_factory(description=long_description)
        created = test_storage.create_client(client)

        retrieved = test_storage.get_client(created.id)
        assert len(retrieved.description) == 10000
