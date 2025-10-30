"""
Unit tests for data models (DTOs).
"""

import pytest
from datetime import datetime, timedelta

from src.models import ClientDTO, EventDTO, SearchCacheDTO


# ==================== ClientDTO Tests ====================

@pytest.mark.unit
class TestClientDTO:
    """Tests for ClientDTO model."""

    def test_create_client_dto(self, sample_client_dto):
        """Test creating a valid ClientDTO."""
        assert sample_client_dto.id == "test-client-1"
        assert sample_client_dto.name == "Test Company"
        assert sample_client_dto.industry == "Technology"
        assert sample_client_dto.priority == "high"
        assert sample_client_dto.is_active is True

    def test_client_dto_validation_valid(self, sample_client_dto):
        """Test validation of a valid ClientDTO."""
        is_valid, error = sample_client_dto.validate()
        assert is_valid is True
        assert error is None

    def test_client_dto_validation_missing_name(self, client_factory):
        """Test validation fails when name is missing."""
        client = client_factory(name="")
        is_valid, error = client.validate()
        assert is_valid is False
        assert "name" in error.lower()

    def test_client_dto_validation_invalid_priority(self, client_factory):
        """Test validation fails for invalid priority."""
        client = client_factory(priority="invalid")
        is_valid, error = client.validate()
        assert is_valid is False
        assert "priority" in error.lower()

    def test_client_dto_to_dict(self, sample_client_dto):
        """Test converting ClientDTO to dictionary."""
        data = sample_client_dto.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test Company"
        assert data["industry"] == "Technology"
        assert data["is_active"] is True

    def test_client_dto_from_dict(self, sample_clients_data):
        """Test creating ClientDTO from dictionary."""
        client_data = sample_clients_data[0]
        client = ClientDTO.from_dict(client_data)

        assert client.name == client_data["name"]
        assert client.industry == client_data["industry"]
        assert client.priority == client_data["priority"]

    def test_client_dto_keywords_default_empty_list(self, client_factory):
        """Test that keywords default to empty list."""
        client = client_factory(keywords=None)
        assert client.keywords == []

    def test_client_dto_metadata_default_empty_dict(self, client_factory):
        """Test that metadata defaults to empty dict."""
        client = client_factory(metadata=None)
        assert client.metadata == {}


# ==================== EventDTO Tests ====================

@pytest.mark.unit
class TestEventDTO:
    """Tests for EventDTO model."""

    def test_create_event_dto(self, sample_event_dto):
        """Test creating a valid EventDTO."""
        assert sample_event_dto.id == "test-event-1"
        assert sample_event_dto.event_type == "funding"
        assert sample_event_dto.title == "Test Company raises $10M"
        assert sample_event_dto.relevance_score == 0.85
        assert sample_event_dto.sentiment == "positive"

    def test_event_dto_validation_valid(self, sample_event_dto):
        """Test validation of a valid EventDTO."""
        is_valid, error = sample_event_dto.validate()
        assert is_valid is True
        assert error is None

    def test_event_dto_validation_missing_title(self, event_factory):
        """Test validation fails when title is missing."""
        event = event_factory(title="")
        is_valid, error = event.validate()
        assert is_valid is False
        assert "title" in error.lower()

    def test_event_dto_validation_invalid_relevance_score(self, event_factory):
        """Test validation fails for invalid relevance score."""
        event = event_factory(relevance_score=1.5)  # Should be between 0 and 1
        is_valid, error = event.validate()
        assert is_valid is False
        assert "relevance" in error.lower()

    def test_event_dto_validation_negative_relevance_score(self, event_factory):
        """Test validation fails for negative relevance score."""
        event = event_factory(relevance_score=-0.1)
        is_valid, error = event.validate()
        assert is_valid is False

    def test_event_dto_to_dict(self, sample_event_dto):
        """Test converting EventDTO to dictionary."""
        data = sample_event_dto.to_dict()
        assert isinstance(data, dict)
        assert data["title"] == "Test Company raises $10M"
        assert data["event_type"] == "funding"
        assert data["relevance_score"] == 0.85

    def test_event_dto_from_dict(self, sample_events_data):
        """Test creating EventDTO from dictionary."""
        event_data = sample_events_data[0]
        event = EventDTO.from_dict(event_data)

        assert event.title == event_data["title"]
        assert event.event_type == event_data["event_type"]
        assert event.relevance_score == event_data["relevance_score"]

    def test_event_dto_tags_default_empty_list(self, event_factory):
        """Test that tags default to empty list."""
        event = event_factory(tags=None)
        assert event.tags == []

    def test_event_dto_sentiment_default_neutral(self, event_factory):
        """Test that sentiment defaults to neutral."""
        event = event_factory(sentiment=None)
        assert event.sentiment == "neutral"

    def test_event_dto_status_default_new(self, event_factory):
        """Test that status defaults to new."""
        event = event_factory(status=None)
        assert event.status == "new"


# ==================== SearchCacheDTO Tests ====================

@pytest.mark.unit
class TestSearchCacheDTO:
    """Tests for SearchCacheDTO model."""

    def test_create_search_cache_dto(self):
        """Test creating a valid SearchCacheDTO."""
        cache = SearchCacheDTO(
            query="test query",
            api_source="google",
            results=[{"title": "Result 1"}],
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            result_count=1,
            query_hash="hash123",
            metadata={}
        )

        assert cache.query == "test query"
        assert cache.api_source == "google"
        assert cache.result_count == 1
        assert len(cache.results) == 1

    def test_search_cache_dto_validation_valid(self):
        """Test validation of a valid SearchCacheDTO."""
        cache = SearchCacheDTO(
            query="test",
            api_source="google",
            results=[],
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            result_count=0,
            query_hash="hash",
            metadata={}
        )

        is_valid, error = cache.validate()
        assert is_valid is True
        assert error is None

    def test_search_cache_dto_validation_missing_query(self):
        """Test validation fails when query is missing."""
        cache = SearchCacheDTO(
            query="",
            api_source="google",
            results=[],
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            result_count=0,
            query_hash="hash",
            metadata={}
        )

        is_valid, error = cache.validate()
        assert is_valid is False
        assert "query" in error.lower()

    def test_search_cache_dto_is_expired_true(self):
        """Test cache expiration check when expired."""
        cache = SearchCacheDTO(
            query="test",
            api_source="google",
            results=[],
            cached_at=datetime.now() - timedelta(hours=25),
            expires_at=datetime.now() - timedelta(hours=1),  # Expired 1 hour ago
            result_count=0,
            query_hash="hash",
            metadata={}
        )

        assert cache.is_expired() is True

    def test_search_cache_dto_is_expired_false(self):
        """Test cache expiration check when not expired."""
        cache = SearchCacheDTO(
            query="test",
            api_source="google",
            results=[],
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=23),  # Expires in 23 hours
            result_count=0,
            query_hash="hash",
            metadata={}
        )

        assert cache.is_expired() is False

    def test_search_cache_dto_to_dict(self):
        """Test converting SearchCacheDTO to dictionary."""
        cache = SearchCacheDTO(
            query="test",
            api_source="google",
            results=[{"title": "Test"}],
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            result_count=1,
            query_hash="hash",
            metadata={"source": "test"}
        )

        data = cache.to_dict()
        assert isinstance(data, dict)
        assert data["query"] == "test"
        assert data["api_source"] == "google"
        assert data["result_count"] == 1


# ==================== Edge Cases and Validation ====================

@pytest.mark.unit
class TestModelEdgeCases:
    """Tests for model edge cases and boundary conditions."""

    def test_client_dto_very_long_name(self, client_factory):
        """Test ClientDTO handles very long names."""
        long_name = "A" * 1000
        client = client_factory(name=long_name)
        assert len(client.name) == 1000

    def test_event_dto_relevance_score_boundaries(self, event_factory):
        """Test EventDTO with boundary relevance scores."""
        # Test minimum boundary
        event_min = event_factory(relevance_score=0.0)
        is_valid, _ = event_min.validate()
        assert is_valid is True

        # Test maximum boundary
        event_max = event_factory(relevance_score=1.0)
        is_valid, _ = event_max.validate()
        assert is_valid is True

    def test_event_dto_empty_summary(self, event_factory):
        """Test EventDTO with empty summary."""
        event = event_factory(summary="")
        # Should be valid as summary is optional
        is_valid, _ = event.validate()
        assert is_valid is True

    def test_client_dto_special_characters_in_name(self, client_factory):
        """Test ClientDTO handles special characters."""
        special_name = "Test & Co. (UK) Ltd."
        client = client_factory(name=special_name)
        assert client.name == special_name

    def test_event_dto_future_published_date(self, event_factory):
        """Test EventDTO with future published date."""
        future_date = datetime.now() + timedelta(days=365)
        event = event_factory(published_date=future_date)
        # Future dates might be invalid depending on business logic
        # For now, just test that it's created
        assert event.published_date == future_date

    def test_client_dto_unicode_characters(self, client_factory):
        """Test ClientDTO handles unicode characters."""
        unicode_name = "Test Company 中文 العربية"
        client = client_factory(name=unicode_name)
        assert client.name == unicode_name

    def test_event_dto_very_long_title(self, event_factory):
        """Test EventDTO handles very long titles."""
        long_title = "A" * 500
        event = event_factory(title=long_title)
        assert len(event.title) == 500
