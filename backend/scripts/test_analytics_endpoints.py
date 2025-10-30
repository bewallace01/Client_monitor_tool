"""Test Analytics API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_dashboard_summary():
    """Test GET /analytics/dashboard - complete dashboard summary."""
    print("\n[TEST] GET /analytics/dashboard - Dashboard summary")
    response = requests.get(f"{BASE_URL}/analytics/dashboard")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    # Verify required fields
    assert "total_clients" in data
    assert "total_events" in data
    assert "sentiment_distribution" in data
    assert "events_by_category" in data
    assert "avg_relevance_score" in data

    print(f"  [OK] Total Clients: {data['total_clients']}, Total Events: {data['total_events']}")
    print(f"       Active Clients: {data['active_clients']}, Unread Events: {data['unread_events']}")
    print(f"       Avg Relevance: {data['avg_relevance_score']}")
    print(f"       Events Today: {data['events_today']}, This Week: {data['events_this_week']}, This Month: {data['events_this_month']}")
    return data


def test_top_clients_activity():
    """Test GET /analytics/clients/top-activity."""
    print("\n[TEST] GET /analytics/clients/top-activity")
    response = requests.get(f"{BASE_URL}/analytics/clients/top-activity", params={
        "limit": 5,
        "days": 30
    })
    assert response.status_code == 200
    data = response.json()

    assert "clients" in data
    assert "period_days" in data
    assert data["period_days"] == 30

    print(f"  [OK] Top 5 clients by activity (last 30 days):")
    for i, client in enumerate(data["clients"][:5], 1):
        print(f"       {i}. {client['client_name']}: {client['total_events']} events ({client['unread_events']} unread)")
    return data


def test_event_timeline():
    """Test GET /analytics/events/timeline."""
    print("\n[TEST] GET /analytics/events/timeline - 30 days")
    response = requests.get(f"{BASE_URL}/analytics/events/timeline", params={
        "days": 30
    })
    assert response.status_code == 200
    data = response.json()

    assert "timeline" in data
    assert "total_events" in data
    assert "period_start" in data
    assert "period_end" in data

    print(f"  [OK] Timeline from {data['period_start']} to {data['period_end']}")
    print(f"       Total events in period: {data['total_events']}")
    print(f"       Data points: {len(data['timeline'])}")

    # Show last 5 days
    print(f"       Last 5 days:")
    for point in data['timeline'][-5:]:
        print(f"         {point['date']}: {point['value']} events")

    return data


def test_event_timeline_7_days():
    """Test GET /analytics/events/timeline - 7 days."""
    print("\n[TEST] GET /analytics/events/timeline - 7 days")
    response = requests.get(f"{BASE_URL}/analytics/events/timeline", params={
        "days": 7
    })
    assert response.status_code == 200
    data = response.json()

    print(f"  [OK] Last 7 days: {data['total_events']} events")
    return data


def test_category_analytics():
    """Test GET /analytics/events/categories."""
    print("\n[TEST] GET /analytics/events/categories")
    response = requests.get(f"{BASE_URL}/analytics/events/categories")
    assert response.status_code == 200
    data = response.json()

    assert "distribution" in data
    assert "total_events" in data
    assert "unique_categories" in data

    print(f"  [OK] {data['unique_categories']} unique categories, {data['total_events']} total events")
    print(f"       Top categories:")
    for cat in data["distribution"][:5]:
        print(f"         {cat['category']}: {cat['count']} ({cat['percentage']}%)")

    return data


def test_sentiment_analytics():
    """Test GET /analytics/events/sentiment."""
    print("\n[TEST] GET /analytics/events/sentiment")
    response = requests.get(f"{BASE_URL}/analytics/events/sentiment")
    assert response.status_code == 200
    data = response.json()

    assert "distribution" in data
    assert "total_events" in data
    assert "avg_sentiment_score" in data

    dist = data["distribution"]
    print(f"  [OK] Sentiment distribution (total: {data['total_events']}):")
    print(f"       Positive: {dist['positive']} ({dist['positive_percentage']}%)")
    print(f"       Neutral: {dist['neutral']} ({dist['neutral_percentage']}%)")
    print(f"       Negative: {dist['negative']} ({dist['negative_percentage']}%)")
    print(f"       Average sentiment score: {data['avg_sentiment_score']}")

    return data


def test_relevance_metrics():
    """Test GET /analytics/events/relevance."""
    print("\n[TEST] GET /analytics/events/relevance")
    response = requests.get(f"{BASE_URL}/analytics/events/relevance")
    assert response.status_code == 200
    data = response.json()

    assert "avg_score" in data
    assert "high_relevance_count" in data
    assert "medium_relevance_count" in data
    assert "low_relevance_count" in data

    print(f"  [OK] Relevance metrics:")
    print(f"       Average score: {data['avg_score']}")
    print(f"       High (>= 0.7): {data['high_relevance_count']} ({data['high_relevance_percentage']}%)")
    print(f"       Medium (0.4-0.7): {data['medium_relevance_count']}")
    print(f"       Low (< 0.4): {data['low_relevance_count']}")

    return data


def test_growth_metrics():
    """Test GET /analytics/growth - 7 day trend."""
    print("\n[TEST] GET /analytics/growth - 7 day comparison")
    response = requests.get(f"{BASE_URL}/analytics/growth", params={
        "period_days": 7
    })
    assert response.status_code == 200
    data = response.json()

    assert "events_trend" in data
    assert "clients_trend" in data
    assert "period" in data

    print(f"  [OK] Growth metrics ({data['period']}):")

    events = data["events_trend"]
    print(f"       Events: {events['current_value']} (prev: {events['previous_value']})")
    print(f"         Change: {events['change']} ({events['change_percentage']}%) - {events['trend']}")

    clients = data["clients_trend"]
    print(f"       New Clients: {clients['current_value']} (prev: {clients['previous_value']})")
    print(f"         Change: {clients['change']} ({clients['change_percentage']}%) - {clients['trend']}")

    return data


def test_growth_metrics_30_days():
    """Test GET /analytics/growth - 30 day trend."""
    print("\n[TEST] GET /analytics/growth - 30 day comparison")
    response = requests.get(f"{BASE_URL}/analytics/growth", params={
        "period_days": 30
    })
    assert response.status_code == 200
    data = response.json()

    print(f"  [OK] 30-day growth: Events {data['events_trend']['trend']}, Clients {data['clients_trend']['trend']}")
    return data


def test_top_clients_limited():
    """Test GET /analytics/clients/top-activity with different limit."""
    print("\n[TEST] GET /analytics/clients/top-activity - limit=3")
    response = requests.get(f"{BASE_URL}/analytics/clients/top-activity", params={
        "limit": 3,
        "days": 7
    })
    assert response.status_code == 200
    data = response.json()

    assert len(data["clients"]) <= 3
    print(f"  [OK] Returned {len(data['clients'])} clients (last 7 days)")
    return data


def main():
    """Run all tests."""
    print("=" * 60)
    print("Analytics API Endpoint Tests")
    print("=" * 60)

    try:
        # Dashboard and summary
        test_dashboard_summary()

        # Client analytics
        test_top_clients_activity()
        test_top_clients_limited()

        # Event analytics
        test_event_timeline()
        test_event_timeline_7_days()
        test_category_analytics()
        test_sentiment_analytics()
        test_relevance_metrics()

        # Growth metrics
        test_growth_metrics()
        test_growth_metrics_30_days()

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
