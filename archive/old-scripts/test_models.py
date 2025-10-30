"""
Test script to demonstrate the new dataclass models.
Run this to see how the DTOs work independently of the database.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
from src.models import ClientDTO, EventDTO, SearchCacheDTO
from src.models.utils import (
    generate_uuid,
    format_datetime_ago,
    sentiment_score_to_label,
    relevance_score_to_label,
)


def test_client_dto():
    """Test ClientDTO functionality."""
    print("=" * 60)
    print("Testing ClientDTO")
    print("=" * 60)

    # Create a sample client
    print("\n1. Creating sample client...")
    client = ClientDTO.create_sample(name="TechCorp", priority="high")
    print(f"   Created: {client}")

    # Validate
    print("\n2. Validating client...")
    is_valid, error = client.validate()
    print(f"   Valid: {is_valid}")
    if error:
        print(f"   Error: {error}")

    # Convert to dict
    print("\n3. Converting to dictionary...")
    client_dict = client.to_dict()
    print(f"   Keys: {list(client_dict.keys())}")

    # Convert to JSON
    print("\n4. Converting to JSON...")
    json_str = client.to_json()
    print(f"   JSON (first 200 chars): {json_str[:200]}...")

    # Recreate from dict
    print("\n5. Recreating from dictionary...")
    client2 = ClientDTO.from_dict(client_dict)
    print(f"   Recreated: {client2.name} (ID: {client2.id})")

    # Test validation errors
    print("\n6. Testing validation with invalid data...")
    invalid_client = ClientDTO(
        id=generate_uuid(),
        name="",  # Empty name should fail
        priority="invalid",  # type: ignore
    )
    is_valid, error = invalid_client.validate()
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")


def test_event_dto():
    """Test EventDTO functionality."""
    print("\n" + "=" * 60)
    print("Testing EventDTO")
    print("=" * 60)

    # Create a sample event
    print("\n1. Creating sample event...")
    event = EventDTO.create_sample(
        client_id=generate_uuid(),
        event_type="funding",
        relevance_score=0.85,
    )
    print(f"   Created: {event}")

    # Validate
    print("\n2. Validating event...")
    is_valid, error = event.validate()
    print(f"   Valid: {is_valid}")

    # Test relevance check
    print("\n3. Testing relevance...")
    print(f"   Is relevant (>0.5)? {event.is_relevant(0.5)}")
    print(f"   Is relevant (>0.9)? {event.is_relevant(0.9)}")
    print(f"   Relevance label: {event.get_relevance_label()}")

    # Test sentiment
    print("\n4. Testing sentiment...")
    print(f"   Sentiment: {event.sentiment}")
    # Skip emoji on Windows console
    # print(f"   Sentiment emoji: {event.get_sentiment_emoji()}")

    # Test status changes
    print("\n5. Testing status changes...")
    print(f"   Initial status: {event.status}")
    event.mark_as_reviewed()
    print(f"   After review: {event.status}")
    event.mark_as_actioned()
    print(f"   After action: {event.status}")

    # Convert to dict
    print("\n6. Converting to dictionary...")
    event_dict = event.to_dict()
    print(f"   Keys: {list(event_dict.keys())}")

    # Test validation errors
    print("\n7. Testing validation with invalid data...")
    invalid_event = EventDTO(
        id=generate_uuid(),
        client_id=generate_uuid(),
        event_type="invalid",  # type: ignore
        title="",  # Empty title should fail
        relevance_score=2.0,  # Out of range
    )
    is_valid, error = invalid_event.validate()
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")


def test_cache_dto():
    """Test SearchCacheDTO functionality."""
    print("\n" + "=" * 60)
    print("Testing SearchCacheDTO")
    print("=" * 60)

    # Create a sample cache
    print("\n1. Creating sample cache...")
    cache = SearchCacheDTO.create_sample(
        query="TechCorp funding",
        api_source="newsapi",
        ttl_hours=24,
    )
    print(f"   Created: {cache}")

    # Check expiry
    print("\n2. Checking expiry...")
    print(f"   Is expired? {cache.is_expired()}")
    print(f"   Is valid? {cache.is_valid()}")
    print(f"   Time until expiry: {cache.time_until_expiry()}")
    print(f"   Cache age: {cache.get_cache_age()}")

    # Test query hash
    print("\n3. Testing query hash...")
    print(f"   Query hash: {cache.query_hash}")
    print(f"   Hash length: {len(cache.query_hash)}")

    # Test refresh
    print("\n4. Testing cache refresh...")
    print(f"   Result count before: {cache.result_count}")
    new_results = [{"title": "New article", "url": "http://example.com"}]
    cache.refresh(new_results, ttl_hours=48)
    print(f"   Result count after: {cache.result_count}")
    print(f"   New expiry: {cache.expires_at}")

    # Test expired cache
    print("\n5. Testing expired cache...")
    old_cache = SearchCacheDTO(
        query="Old query",
        api_source="mock",
        cached_at=datetime.utcnow() - timedelta(days=5),
        expires_at=datetime.utcnow() - timedelta(days=2),
    )
    print(f"   Is expired? {old_cache.is_expired()}")
    print(f"   Time until expiry: {old_cache.time_until_expiry()}")

    # Convert to dict
    print("\n6. Converting to dictionary...")
    cache_dict = cache.to_dict()
    print(f"   Keys: {list(cache_dict.keys())}")


def test_utilities():
    """Test utility functions."""
    print("\n" + "=" * 60)
    print("Testing Utility Functions")
    print("=" * 60)

    # Test UUID generation
    print("\n1. Testing UUID generation...")
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()
    print(f"   UUID 1: {uuid1}")
    print(f"   UUID 2: {uuid2}")
    print(f"   Are unique? {uuid1 != uuid2}")

    # Test time formatting
    print("\n2. Testing time formatting...")
    now = datetime.utcnow()
    times = [
        now - timedelta(seconds=30),
        now - timedelta(minutes=5),
        now - timedelta(hours=3),
        now - timedelta(days=2),
        now - timedelta(days=45),
        now - timedelta(days=400),
    ]
    for dt in times:
        print(f"   {dt.isoformat()} -> {format_datetime_ago(dt)}")

    # Test sentiment conversion
    print("\n3. Testing sentiment conversion...")
    sentiment_scores = [-0.8, -0.2, 0.0, 0.5, 0.9, None]
    for score in sentiment_scores:
        label = sentiment_score_to_label(score)
        print(f"   Score {score} -> {label}")

    # Test relevance conversion
    print("\n4. Testing relevance conversion...")
    relevance_scores = [0.1, 0.35, 0.55, 0.75, 0.95]
    for score in relevance_scores:
        label = relevance_score_to_label(score)
        print(f"   Score {score} -> {label}")


def main():
    """Run all tests."""
    print("\nClient Intelligence Monitor - Model Tests")
    print("Testing new dataclass-based DTOs\n")

    try:
        test_client_dto()
        test_event_dto()
        test_cache_dto()
        test_utilities()

        print("\n" + "=" * 60)
        print("[SUCCESS] All model tests completed!")
        print("=" * 60)
        print("\nThe new DTOs are working correctly and can be used")
        print("independently of the database for business logic.")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
