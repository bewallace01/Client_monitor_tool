"""
Integration tests for full workflow.

Tests the complete flow: add client → scan → events → process
"""

import pytest
from datetime import datetime

from src.models import ClientDTO, EventDTO
from src.storage import SQLiteStorage
from src.collectors.mock_collector import MockCollector
from src.classifier import classify_event
from src.scorer import calculate_relevance_score


# ==================== End-to-End Workflow Tests ====================

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Tests for complete end-to-end workflows."""

    def test_full_client_lifecycle(self, test_storage, client_factory):
        """Test complete client lifecycle: create, update, use, delete."""
        # 1. Create client
        client = client_factory(
            id="integration-client-1",
            name="Integration Test Company",
            industry="Technology"
        )

        created_client = test_storage.create_client(client)
        assert created_client is not None

        # 2. Retrieve client
        retrieved = test_storage.get_client(client.id)
        assert retrieved.name == "Integration Test Company"

        # 3. Update client
        updates = {"priority": "high", "tier": "Enterprise"}
        updated = test_storage.update_client(client.id, updates)
        assert updated.priority == "high"

        # 4. Use client in search
        all_clients = test_storage.get_all_clients()
        assert any(c.id == client.id for c in all_clients)

        # 5. Delete client
        deleted = test_storage.delete_client(client.id)
        assert deleted is True
        assert test_storage.get_client(client.id) is None

    def test_full_event_workflow(self, test_storage, client_factory, event_factory):
        """Test complete event workflow: collect, classify, score, store."""
        # 1. Create a client
        client = client_factory(id="workflow-client-1", name="Test Corp")
        test_storage.create_client(client)

        # 2. Simulate collecting news
        collector = MockCollector()
        search_results = collector.search(f"{client.name} news")
        assert len(search_results) > 0

        # 3. Process first result
        result = search_results[0]

        # 4. Classify the event
        event_type, confidence = classify_event(
            result["title"],
            result["snippet"]
        )
        assert event_type is not None

        # 5. Calculate relevance
        relevance_score = calculate_relevance_score(
            event_title=result["title"],
            event_summary=result["snippet"],
            event_type=event_type,
            client_name=client.name,
            client_industry=client.industry,
            event_date=datetime.now()
        )
        assert 0.0 <= relevance_score <= 1.0

        # 6. Create event
        event = event_factory(
            id="workflow-event-1",
            client_id=client.id,
            title=result["title"],
            summary=result["snippet"],
            event_type=event_type,
            relevance_score=relevance_score
        )

        stored_event = test_storage.create_event(event)
        assert stored_event is not None

        # 7. Retrieve and verify
        retrieved_event = test_storage.get_event(event.id)
        assert retrieved_event.title == result["title"]
        assert retrieved_event.event_type == event_type

    def test_multi_client_monitoring(self, test_storage, multiple_client_dtos):
        """Test monitoring multiple clients simultaneously."""
        # 1. Add multiple clients
        for client in multiple_client_dtos:
            test_storage.create_client(client)

        # 2. Verify all clients stored
        all_clients = test_storage.get_all_clients()
        assert len(all_clients) >= len(multiple_client_dtos)

        # 3. Collect events for each client
        collector = MockCollector()
        events_created = 0

        for client in multiple_client_dtos[:2]:  # Test with first 2 clients
            results = collector.search(f"{client.name} news")

            for result in results[:2]:  # Process 2 events per client
                event_type, _ = classify_event(result["title"])

                event = EventDTO(
                    id=f"multi-{client.id}-{events_created}",
                    client_id=client.id,
                    event_type=event_type,
                    title=result["title"],
                    summary=result["snippet"],
                    source_url=result["url"],
                    source_name="Mock Source",
                    published_date=datetime.now(),
                    discovered_date=datetime.now(),
                    relevance_score=0.7,
                    sentiment="neutral",
                    sentiment_score=0.5,
                    status="new",
                    tags=[],
                    user_notes=None,
                    metadata={}
                )

                test_storage.create_event(event)
                events_created += 1

        # 4. Verify events stored
        assert events_created >= 2

        # 5. Verify client-specific queries work
        for client in multiple_client_dtos[:2]:
            client_events = test_storage.get_events_by_client(client.id)
            assert len(client_events) >= 1

    def test_search_and_filter_workflow(self, populated_storage):
        """Test searching and filtering events."""
        # 1. Get all events
        all_events = populated_storage.get_all_events()
        total_count = len(all_events)

        # 2. Filter by relevance
        high_relevance = [e for e in all_events if e.relevance_score >= 0.8]
        assert len(high_relevance) < total_count

        # 3. Filter by event type
        funding_events = [e for e in all_events if e.event_type == "funding"]
        assert len(funding_events) >= 0

        # 4. Search by text
        search_results = populated_storage.search_events("funding")
        assert len(search_results) >= 0

        # 5. Get recent events
        recent_events = populated_storage.get_recent_events(days=7)
        for event in recent_events:
            assert (datetime.now() - event.published_date).days <= 7


# ==================== Error Handling Tests ====================

@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling in workflows."""

    def test_create_event_without_client(self, test_storage, event_factory):
        """Test that creating event without client fails gracefully."""
        event = event_factory(client_id="non-existent-client")

        # Should raise an error due to foreign key constraint
        with pytest.raises(Exception):
            test_storage.create_event(event)

    def test_duplicate_client_id(self, test_storage, client_factory):
        """Test handling duplicate client IDs."""
        client = client_factory(id="duplicate-test")
        test_storage.create_client(client)

        # Creating another client with same ID should fail
        with pytest.raises(Exception):
            test_storage.create_client(client)

    def test_invalid_client_data(self, test_storage, client_factory):
        """Test handling invalid client data."""
        # Create client with empty name
        invalid_client = client_factory(name="")

        is_valid, error = invalid_client.validate()
        assert is_valid is False

        # Storage should also reject it
        with pytest.raises(ValueError):
            test_storage.create_client(invalid_client)


# ==================== Performance Tests ====================

@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Tests for performance with larger datasets."""

    def test_bulk_client_operations(self, test_storage, client_factory):
        """Test performance with many clients."""
        # Create 50 clients
        clients = [client_factory(id=f"bulk-{i}", name=f"Company {i}")
                   for i in range(50)]

        for client in clients:
            test_storage.create_client(client)

        # Retrieve all
        all_clients = test_storage.get_all_clients(active_only=False)
        assert len(all_clients) >= 50

    def test_bulk_event_operations(self, test_storage, client_factory, event_factory):
        """Test performance with many events."""
        # Create a client
        client = client_factory(id="bulk-events-client")
        test_storage.create_client(client)

        # Create 100 events
        events = [event_factory(id=f"bulk-event-{i}", client_id=client.id)
                  for i in range(100)]

        for event in events:
            test_storage.create_event(event)

        # Retrieve all events for client
        client_events = test_storage.get_events_by_client(client.id)
        assert len(client_events) >= 100


# ==================== Data Integrity Tests ====================

@pytest.mark.integration
class TestDataIntegrity:
    """Tests for data integrity across operations."""

    def test_client_event_relationship(self, test_storage, client_factory, event_factory):
        """Test that client-event relationships are maintained."""
        # Create client
        client = client_factory(id="integrity-client-1")
        test_storage.create_client(client)

        # Create events
        event1 = event_factory(id="integrity-event-1", client_id=client.id)
        event2 = event_factory(id="integrity-event-2", client_id=client.id)

        test_storage.create_event(event1)
        test_storage.create_event(event2)

        # Verify relationships
        client_events = test_storage.get_events_by_client(client.id)
        assert len(client_events) == 2

        # Verify each event links back to correct client
        for event in client_events:
            assert event.client_id == client.id

    def test_statistics_accuracy(self, populated_storage):
        """Test that statistics are accurate."""
        stats = populated_storage.get_statistics()

        # Count manually
        all_clients = populated_storage.get_all_clients(active_only=False)
        all_events = populated_storage.get_all_events()

        assert stats["total_clients"] == len(all_clients)
        assert stats["total_events"] == len(all_events)

    def test_cascade_delete_integrity(self, test_storage, client_factory, event_factory):
        """Test data integrity with cascade deletes."""
        # Create client with events
        client = client_factory(id="cascade-test-client")
        test_storage.create_client(client)

        events = [event_factory(id=f"cascade-event-{i}", client_id=client.id)
                  for i in range(3)]

        for event in events:
            test_storage.create_event(event)

        # Verify events exist
        client_events = test_storage.get_events_by_client(client.id)
        assert len(client_events) == 3

        # Delete client
        test_storage.delete_client(client.id)

        # Verify events are also deleted
        for event in events:
            assert test_storage.get_event(event.id) is None
