"""
Pytest configuration and shared fixtures.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from src.models import ClientDTO, EventDTO
from src.storage import SQLiteStorage


# ==================== Fixture Data Loaders ====================

@pytest.fixture
def fixture_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_clients_data(fixture_dir) -> List[Dict]:
    """Load sample clients from JSON fixture."""
    with open(fixture_dir / "sample_clients.json", "r") as f:
        data = json.load(f)
    return data["clients"]


@pytest.fixture
def sample_events_data(fixture_dir) -> List[Dict]:
    """Load sample events from JSON fixture."""
    with open(fixture_dir / "sample_events.json", "r") as f:
        data = json.load(f)
    return data["events"]


@pytest.fixture
def mock_api_responses(fixture_dir) -> Dict:
    """Load mock API responses from JSON fixture."""
    with open(fixture_dir / "mock_api_responses.json", "r") as f:
        return json.load(f)


# ==================== Model Fixtures ====================

@pytest.fixture
def sample_client_dto() -> ClientDTO:
    """Create a sample ClientDTO for testing."""
    return ClientDTO(
        id="test-client-1",
        name="Test Company",
        industry="Technology",
        priority="high",
        keywords=["software", "cloud"],
        monitoring_since=datetime(2024, 1, 1),
        last_checked=datetime(2024, 10, 15),
        metadata={"test": True},
        domain="testcompany.com",
        description="A test company",
        account_owner="Test Owner",
        tier="Enterprise",
        is_active=True
    )


@pytest.fixture
def sample_event_dto(sample_client_dto) -> EventDTO:
    """Create a sample EventDTO for testing."""
    return EventDTO(
        id="test-event-1",
        client_id=sample_client_dto.id,
        event_type="funding",
        title="Test Company raises $10M",
        summary="Test Company announced $10M in funding",
        source_url="https://example.com/news",
        source_name="Test News",
        published_date=datetime(2024, 10, 10),
        discovered_date=datetime(2024, 10, 10),
        relevance_score=0.85,
        sentiment="positive",
        sentiment_score=0.75,
        status="new",
        tags=["funding", "test"],
        user_notes=None,
        metadata={"test": True}
    )


@pytest.fixture
def multiple_client_dtos(sample_clients_data) -> List[ClientDTO]:
    """Create multiple ClientDTO objects from fixture data."""
    clients = []
    for client_data in sample_clients_data:
        clients.append(ClientDTO(
            id=client_data["id"],
            name=client_data["name"],
            industry=client_data["industry"],
            priority=client_data["priority"],
            keywords=client_data["keywords"],
            monitoring_since=datetime.fromisoformat(client_data["monitoring_since"]),
            last_checked=datetime.fromisoformat(client_data["last_checked"]) if client_data.get("last_checked") else None,
            metadata=client_data.get("metadata", {}),
            domain=client_data.get("domain"),
            description=client_data.get("description"),
            account_owner=client_data.get("account_owner"),
            tier=client_data.get("tier"),
            is_active=client_data.get("is_active", True)
        ))
    return clients


@pytest.fixture
def multiple_event_dtos(sample_events_data) -> List[EventDTO]:
    """Create multiple EventDTO objects from fixture data."""
    events = []
    for event_data in sample_events_data:
        events.append(EventDTO(
            id=event_data["id"],
            client_id=event_data["client_id"],
            event_type=event_data["event_type"],
            title=event_data["title"],
            summary=event_data["summary"],
            source_url=event_data["source_url"],
            source_name=event_data["source_name"],
            published_date=datetime.fromisoformat(event_data["published_date"]),
            discovered_date=datetime.fromisoformat(event_data["discovered_date"]),
            relevance_score=event_data["relevance_score"],
            sentiment=event_data["sentiment"],
            sentiment_score=event_data.get("sentiment_score"),
            status=event_data["status"],
            tags=event_data.get("tags", []),
            user_notes=event_data.get("user_notes"),
            metadata=event_data.get("metadata", {})
        ))
    return events


# ==================== Storage Fixtures ====================

@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    yield temp_path

    # Cleanup
    try:
        Path(temp_path).unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def test_storage(temp_db_path):
    """Create a test storage instance with temporary database."""
    storage = SQLiteStorage(db_path=temp_db_path)
    storage.connect()
    storage.initialize_database()

    yield storage

    # Cleanup
    storage.disconnect()


@pytest.fixture
def populated_storage(test_storage, multiple_client_dtos, multiple_event_dtos):
    """Create a test storage instance populated with sample data."""
    # Add clients
    for client in multiple_client_dtos:
        test_storage.create_client(client)

    # Add events
    for event in multiple_event_dtos:
        test_storage.create_event(event)

    return test_storage


# ==================== Test Data Generators ====================

@pytest.fixture
def client_factory():
    """Factory for creating test client DTOs."""
    def _create_client(
        id: str = "test-client",
        name: str = "Test Company",
        industry: str = "Technology",
        **kwargs
    ) -> ClientDTO:
        defaults = {
            "priority": "medium",
            "keywords": ["test"],
            "monitoring_since": datetime.now(),
            "last_checked": None,
            "metadata": {},
            "domain": "test.com",
            "description": "Test description",
            "account_owner": "Test Owner",
            "tier": "Growth",
            "is_active": True
        }
        defaults.update(kwargs)

        return ClientDTO(
            id=id,
            name=name,
            industry=industry,
            **defaults
        )

    return _create_client


@pytest.fixture
def event_factory():
    """Factory for creating test event DTOs."""
    def _create_event(
        id: str = "test-event",
        client_id: str = "test-client",
        event_type: str = "news",
        title: str = "Test Event",
        **kwargs
    ) -> EventDTO:
        defaults = {
            "summary": "Test event summary",
            "source_url": "https://example.com",
            "source_name": "Test Source",
            "published_date": datetime.now(),
            "discovered_date": datetime.now(),
            "relevance_score": 0.5,
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "status": "new",
            "tags": [],
            "user_notes": None,
            "metadata": {}
        }
        defaults.update(kwargs)

        return EventDTO(
            id=id,
            client_id=client_id,
            event_type=event_type,
            title=title,
            **defaults
        )

    return _create_event


# ==================== Cleanup Helpers ====================

@pytest.fixture
def cleanup_temp_files():
    """Cleanup temporary files created during tests."""
    temp_files = []

    def _register(file_path: str):
        temp_files.append(file_path)

    yield _register

    # Cleanup all registered temp files
    for file_path in temp_files:
        try:
            Path(file_path).unlink()
        except FileNotFoundError:
            pass


# ==================== Pytest Configuration ====================

def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "database: Tests that use database"
    )
    config.addinivalue_line(
        "markers", "api: Tests that use external APIs"
    )
    config.addinivalue_line(
        "markers", "ui: Tests for UI components"
    )
