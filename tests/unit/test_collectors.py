"""
Unit tests for collectors (Mock and Factory).
"""

import pytest
from datetime import datetime

from src.collectors.mock_collector import MockCollector
from src.collectors.factory import CollectorFactory


# ==================== MockCollector Tests ====================

@pytest.mark.unit
class TestMockCollector:
    """Tests for MockCollector."""

    def test_mock_collector_initialization(self):
        """Test creating a MockCollector instance."""
        collector = MockCollector()
        assert collector is not None
        assert collector.name == "mock"

    def test_mock_collector_search(self):
        """Test MockCollector search method."""
        collector = MockCollector()
        results = collector.search("test company")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_mock_collector_search_returns_realistic_data(self):
        """Test that mock search returns realistic-looking data."""
        collector = MockCollector()
        results = collector.search("funding")

        for result in results:
            assert "title" in result
            assert "url" in result
            assert "snippet" in result
            assert isinstance(result["title"], str)
            assert len(result["title"]) > 0

    def test_mock_collector_different_queries(self):
        """Test that different queries return different results."""
        collector = MockCollector()

        results1 = collector.search("funding")
        results2 = collector.search("acquisition")

        # Results should be different based on query
        assert results1[0]["title"] != results2[0]["title"]

    def test_mock_collector_empty_query(self):
        """Test MockCollector with empty query."""
        collector = MockCollector()
        results = collector.search("")

        # Should still return some results
        assert isinstance(results, list)


# ==================== CollectorFactory Tests ====================

@pytest.mark.unit
class TestCollectorFactory:
    """Tests for CollectorFactory."""

    def test_factory_create_mock_collector(self):
        """Test factory creates mock collector."""
        collector = CollectorFactory.create_collector(use_mock=True)

        assert collector is not None
        assert isinstance(collector, MockCollector)

    def test_factory_create_with_config(self):
        """Test factory creates collector with configuration."""
        config = {
            "use_mock": True,
            "api_key": "test_key"
        }

        collector = CollectorFactory.create_collector(**config)

        assert collector is not None

    def test_factory_fallback_to_mock(self):
        """Test factory falls back to mock on error."""
        # Even with invalid real API config, should fall back to mock
        config = {
            "use_mock": False,
            "api_key": "",  # Invalid
        }

        collector = CollectorFactory.create_collector(**config)

        # Should fall back to mock collector
        assert collector is not None
        assert isinstance(collector, MockCollector)


# ==================== Collector Integration ====================

@pytest.mark.unit
class TestCollectorResults:
    """Tests for collector result formats."""

    def test_collector_result_structure(self):
        """Test that collector results have expected structure."""
        collector = MockCollector()
        results = collector.search("test")

        for result in results:
            # Check required fields
            assert "title" in result
            assert "url" in result
            assert "snippet" in result

            # Check field types
            assert isinstance(result["title"], str)
            assert isinstance(result["url"], str)
            assert isinstance(result["snippet"], str)

    def test_collector_result_not_empty(self):
        """Test that search results are not empty."""
        collector = MockCollector()
        results = collector.search("company news")

        assert len(results) > 0

        for result in results:
            assert len(result["title"]) > 0
            assert len(result["snippet"]) > 0
