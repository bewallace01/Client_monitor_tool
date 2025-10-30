"""Test Event API endpoints."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"


def test_get_events():
    """Test GET /events - list with pagination."""
    print("\n[TEST] GET /events - List with pagination")
    response = requests.get(f"{BASE_URL}/events", params={"limit": 10})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10
    print(f"  [OK] Returned {len(data['items'])} of {data['total']} total events")
    return data


def test_get_event_by_id():
    """Test GET /events/{id} - get single event."""
    print("\n[TEST] GET /events/1 - Get single event")
    response = requests.get(f"{BASE_URL}/events/1")
    assert response.status_code == 200
    event = response.json()
    assert "id" in event
    assert event["id"] == 1
    print(f"  [OK] Retrieved event: {event['title'][:50]}...")
    return event


def test_get_event_not_found():
    """Test GET /events/{id} with invalid ID - should return 404."""
    print("\n[TEST] GET /events/99999 - Non-existent event")
    response = requests.get(f"{BASE_URL}/events/99999")
    assert response.status_code == 404
    print(f"  [OK] Correctly returned 404")


def test_filter_by_client():
    """Test filtering events by client ID."""
    print("\n[TEST] GET /events?client_id=1")
    response = requests.get(f"{BASE_URL}/events", params={"client_id": 1})
    assert response.status_code == 200
    data = response.json()
    # Verify all returned events belong to client 1
    for event in data["items"]:
        assert event["client_id"] == 1
    print(f"  [OK] Found {data['total']} events for client 1")


def test_filter_by_category():
    """Test filtering events by category."""
    print("\n[TEST] GET /events?category=funding")
    response = requests.get(f"{BASE_URL}/events", params={"category": "funding"})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['total']} funding events")


def test_filter_unread():
    """Test filtering unread events."""
    print("\n[TEST] GET /events?is_read=false")
    response = requests.get(f"{BASE_URL}/events", params={"is_read": False})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['total']} unread events")


def test_filter_starred():
    """Test filtering starred events."""
    print("\n[TEST] GET /events?is_starred=true")
    response = requests.get(f"{BASE_URL}/events", params={"is_starred": True})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['total']} starred events")


def test_filter_by_date_range():
    """Test filtering events by date range."""
    print("\n[TEST] GET /events with date range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    response = requests.get(f"{BASE_URL}/events", params={
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": 10
    })
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['total']} events in last 30 days")


def test_search_events():
    """Test search functionality."""
    print("\n[TEST] GET /events?search=AI")
    response = requests.get(f"{BASE_URL}/events", params={"search": "AI"})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Search returned {data['total']} results")


def test_filter_by_relevance():
    """Test filtering by minimum relevance score."""
    print("\n[TEST] GET /events?min_relevance=0.7")
    response = requests.get(f"{BASE_URL}/events", params={"min_relevance": 0.7})
    assert response.status_code == 200
    data = response.json()
    # Verify all returned events have relevance >= 0.7
    for event in data["items"]:
        assert event["relevance_score"] >= 0.7
    print(f"  [OK] Found {data['total']} high-relevance events (>= 0.7)")


def test_get_stats():
    """Test GET /events/stats."""
    print("\n[TEST] GET /events/stats")
    response = requests.get(f"{BASE_URL}/events/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_events" in stats
    assert "unread_events" in stats
    assert "starred_events" in stats
    assert "events_by_category" in stats
    assert "events_by_sentiment" in stats
    print(f"  [OK] Total: {stats['total_events']}, Unread: {stats['unread_events']}, Starred: {stats['starred_events']}")
    print(f"       Sentiment - Positive: {stats['events_by_sentiment']['positive']}, Neutral: {stats['events_by_sentiment']['neutral']}, Negative: {stats['events_by_sentiment']['negative']}")


def test_get_categories():
    """Test GET /events/categories."""
    print("\n[TEST] GET /events/categories")
    response = requests.get(f"{BASE_URL}/events/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    print(f"  [OK] Found {len(categories)} unique categories: {', '.join(categories[:5])}...")


def test_create_event():
    """Test POST /events - create new event."""
    print("\n[TEST] POST /events - Create new event")
    new_event = {
        "client_id": 1,
        "title": "Test Event API",
        "description": "Test event created via API",
        "url": "https://test.com/event",
        "source": "Test Source",
        "category": "other",
        "relevance_score": 0.8,
        "sentiment_score": 0.5,
        "event_date": datetime.now().isoformat()
    }
    response = requests.post(f"{BASE_URL}/events", json=new_event)
    assert response.status_code == 201
    event = response.json()
    assert event["title"] == new_event["title"]
    assert event["is_read"] == False
    assert event["is_starred"] == False
    print(f"  [OK] Created event with ID: {event['id']}")
    return event


def test_update_event(event_id):
    """Test PUT /events/{id} - update event."""
    print(f"\n[TEST] PUT /events/{event_id} - Update event")
    update_data = {
        "is_read": True,
        "is_starred": True,
        "description": "Updated via API test"
    }
    response = requests.put(f"{BASE_URL}/events/{event_id}", json=update_data)
    assert response.status_code == 200
    event = response.json()
    assert event["is_read"] == True
    assert event["is_starred"] == True
    assert event["description"] == update_data["description"]
    print(f"  [OK] Updated event successfully")


def test_bulk_update_events(event_ids):
    """Test POST /events/bulk-update."""
    print(f"\n[TEST] POST /events/bulk-update - Mark multiple events as read")
    bulk_update = {
        "event_ids": event_ids,
        "is_read": True
    }
    response = requests.post(f"{BASE_URL}/events/bulk-update", json=bulk_update)
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    print(f"  [OK] {result['message']}")

    # Verify updates
    for event_id in event_ids:
        response = requests.get(f"{BASE_URL}/events/{event_id}")
        event = response.json()
        assert event["is_read"] == True
    print(f"  [OK] Verified all events marked as read")


def test_delete_event(event_id):
    """Test DELETE /events/{id} - delete event."""
    print(f"\n[TEST] DELETE /events/{event_id} - Delete event")
    response = requests.delete(f"{BASE_URL}/events/{event_id}")
    assert response.status_code == 200
    print(f"  [OK] Deleted event successfully")

    # Verify it's gone
    response = requests.get(f"{BASE_URL}/events/{event_id}")
    assert response.status_code == 404
    print(f"  [OK] Verified event is deleted")


def test_bulk_delete_events(event_ids):
    """Test POST /events/bulk-delete."""
    print(f"\n[TEST] POST /events/bulk-delete - Delete multiple events")
    response = requests.post(f"{BASE_URL}/events/bulk-delete", json=event_ids)
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    print(f"  [OK] {result['message']}")

    # Verify deletions
    for event_id in event_ids:
        response = requests.get(f"{BASE_URL}/events/{event_id}")
        assert response.status_code == 404
    print(f"  [OK] Verified all events deleted")


def test_sorting():
    """Test sorting functionality."""
    print("\n[TEST] GET /events?sort_by=relevance_score&sort_desc=true")
    response = requests.get(f"{BASE_URL}/events", params={
        "sort_by": "relevance_score",
        "sort_desc": True,
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    scores = [event["relevance_score"] for event in data["items"]]
    print(f"  [OK] Top 5 events by relevance: {scores}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Event API Endpoint Tests")
    print("=" * 60)

    try:
        # Read operations
        test_get_events()
        test_get_event_by_id()
        test_get_event_not_found()
        test_filter_by_client()
        test_filter_by_category()
        test_filter_unread()
        test_filter_starred()
        test_filter_by_date_range()
        test_search_events()
        test_filter_by_relevance()
        test_get_stats()
        test_get_categories()
        test_sorting()

        # Write operations - create test events
        new_event1 = test_create_event()
        new_event2 = test_create_event()
        new_event3 = test_create_event()

        # Test individual update
        test_update_event(new_event1["id"])

        # Test bulk update
        test_bulk_update_events([new_event2["id"], new_event3["id"]])

        # Test individual delete
        test_delete_event(new_event1["id"])

        # Test bulk delete
        test_bulk_delete_events([new_event2["id"], new_event3["id"]])

        print("\n" + "=" * 60)
        print("[OK] All tests passed!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
