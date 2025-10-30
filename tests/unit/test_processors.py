"""
Unit tests for processors (classifier, scorer, deduplicator).
"""

import pytest
from datetime import datetime, timedelta

from src.classifier import classify_event
from src.scorer import calculate_relevance_score
from src.deduplicator import EventDeduplicator


# ==================== Classifier Tests ====================

@pytest.mark.unit
class TestClassifier:
    """Tests for event classifier."""

    def test_classify_funding_event(self):
        """Test classifying a funding event."""
        title = "Company X raises $10M in Series A funding"
        event_type, confidence = classify_event(title)

        assert event_type == "funding"
        assert confidence > 0.5

    def test_classify_acquisition_event(self):
        """Test classifying an acquisition event."""
        title = "Tech Giant acquires startup for $100M"
        event_type, confidence = classify_event(title)

        assert event_type == "acquisition"
        assert confidence > 0.5

    def test_classify_product_launch(self):
        """Test classifying a product launch event."""
        title = "Company launches new AI-powered platform"
        summary = "Today we announced the launch of our revolutionary product"
        event_type, confidence = classify_event(title, summary)

        assert event_type == "product"
        assert confidence > 0.5

    def test_classify_leadership_change(self):
        """Test classifying a leadership change event."""
        title = "Company appoints new CEO"
        event_type, confidence = classify_event(title)

        assert event_type == "leadership"
        assert confidence > 0.5

    def test_classify_partnership(self):
        """Test classifying a partnership event."""
        title = "Company A partners with Company B"
        event_type, confidence = classify_event(title)

        assert event_type == "partnership"
        assert confidence > 0.5

    def test_classify_returns_confidence(self):
        """Test that classifier returns confidence score."""
        title = "Company raises funding"
        event_type, confidence = classify_event(title)

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_classify_ambiguous_event(self):
        """Test classifying an ambiguous event."""
        title = "Company makes announcement"
        event_type, confidence = classify_event(title)

        # Should return some classification
        assert event_type is not None
        # Confidence might be lower for ambiguous events
        assert confidence >= 0.0

    def test_classify_with_summary(self):
        """Test that classifier uses summary for better accuracy."""
        title = "Breaking News"
        summary = "Company X raises $50 million in venture capital funding round"

        event_type, confidence = classify_event(title, summary)

        assert event_type == "funding"


# ==================== Scorer Tests ====================

@pytest.mark.unit
class TestScorer:
    """Tests for relevance scorer."""

    def test_calculate_high_relevance(self):
        """Test calculating high relevance score."""
        score = calculate_relevance_score(
            event_title="Acme Corporation raises $50M funding",
            event_summary="Major funding round for enterprise software",
            event_type="funding",
            client_name="Acme Corporation",
            client_industry="Technology",
            event_date=datetime.now(),
            sentiment="positive"
        )

        assert 0.7 <= score <= 1.0

    def test_calculate_low_relevance(self):
        """Test calculating low relevance score."""
        score = calculate_relevance_score(
            event_title="Random company does something",
            event_summary="Unrelated event",
            event_type="other",
            client_name="My Company",
            client_industry="Finance",
            event_date=datetime.now() - timedelta(days=365),
            sentiment="neutral"
        )

        assert score < 0.7

    def test_recency_affects_score(self):
        """Test that recent events score higher."""
        recent_score = calculate_relevance_score(
            event_title="Company News",
            event_summary="Recent update",
            event_type="news",
            client_name="Company",
            event_date=datetime.now()
        )

        old_score = calculate_relevance_score(
            event_title="Company News",
            event_summary="Recent update",
            event_type="news",
            client_name="Company",
            event_date=datetime.now() - timedelta(days=90)
        )

        assert recent_score > old_score

    def test_sentiment_affects_score(self):
        """Test that sentiment affects scoring."""
        positive_score = calculate_relevance_score(
            event_title="Great News for Company",
            event_summary="Positive development",
            event_type="news",
            client_name="Company",
            sentiment="positive"
        )

        negative_score = calculate_relevance_score(
            event_title="Bad News for Company",
            event_summary="Negative development",
            event_type="news",
            client_name="Company",
            sentiment="negative"
        )

        # Positive sentiment should generally score higher
        assert positive_score >= negative_score

    def test_score_bounds(self):
        """Test that scores are within valid bounds."""
        score = calculate_relevance_score(
            event_title="Test Event",
            event_summary="Test summary",
            event_type="news",
            client_name="Test Company"
        )

        assert 0.0 <= score <= 1.0

    def test_event_type_affects_score(self):
        """Test that important event types score higher."""
        funding_score = calculate_relevance_score(
            event_title="Company raises funding",
            event_summary="Major funding round",
            event_type="funding",
            client_name="Company"
        )

        news_score = calculate_relevance_score(
            event_title="Company in the news",
            event_summary="General news",
            event_type="news",
            client_name="Company"
        )

        # Funding should score higher than general news
        assert funding_score > news_score


# ==================== Deduplicator Tests ====================

@pytest.mark.unit
class TestDeduplicator:
    """Tests for event deduplicator."""

    def test_deduplicator_initialization(self):
        """Test creating a deduplicator instance."""
        deduplicator = EventDeduplicator(similarity_threshold=0.8)
        assert deduplicator is not None

    def test_identify_exact_duplicates(self, multiple_event_dtos):
        """Test identifying exact duplicate events."""
        deduplicator = EventDeduplicator()

        # Create duplicate
        events = [multiple_event_dtos[0], multiple_event_dtos[0]]

        duplicates = deduplicator.find_duplicates(events)

        assert len(duplicates) > 0

    def test_identify_similar_events(self, event_factory):
        """Test identifying similar events."""
        deduplicator = EventDeduplicator(similarity_threshold=0.85)

        event1 = event_factory(
            id="event-1",
            title="Company raises $10M in funding",
            summary="Major funding round announced"
        )

        event2 = event_factory(
            id="event-2",
            title="Company secures $10M funding round",
            summary="Major funding round announced today"
        )

        duplicates = deduplicator.find_duplicates([event1, event2])

        # Should identify as similar
        assert len(duplicates) > 0

    def test_different_events_not_duplicates(self, event_factory):
        """Test that different events are not marked as duplicates."""
        deduplicator = EventDeduplicator()

        event1 = event_factory(
            id="event-1",
            title="Company raises funding"
        )

        event2 = event_factory(
            id="event-2",
            title="Company launches new product"
        )

        duplicates = deduplicator.find_duplicates([event1, event2])

        # Should not be duplicates
        assert len(duplicates) == 0

    def test_remove_duplicates(self, event_factory):
        """Test removing duplicate events."""
        deduplicator = EventDeduplicator()

        event1 = event_factory(id="event-1", title="Same title")
        event2 = event_factory(id="event-2", title="Same title")
        event3 = event_factory(id="event-3", title="Different title")

        deduplicated = deduplicator.remove_duplicates([event1, event2, event3])

        # Should remove one duplicate
        assert len(deduplicated) == 2

    def test_similarity_threshold(self, event_factory):
        """Test that similarity threshold works correctly."""
        strict_deduplicator = EventDeduplicator(similarity_threshold=0.95)
        lenient_deduplicator = EventDeduplicator(similarity_threshold=0.7)

        event1 = event_factory(id="event-1", title="Company news today")
        event2 = event_factory(id="event-2", title="Company news item")

        # Strict should not find duplicates
        strict_duplicates = strict_deduplicator.find_duplicates([event1, event2])

        # Lenient might find duplicates
        lenient_duplicates = lenient_deduplicator.find_duplicates([event1, event2])

        # Lenient should find same or more duplicates
        assert len(lenient_duplicates) >= len(strict_duplicates)
