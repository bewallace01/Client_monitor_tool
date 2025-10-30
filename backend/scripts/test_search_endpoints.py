"""Test Search and Cache API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_perform_search():
    """Test POST /search/query - perform search with caching."""
    print("\n[TEST] POST /search/query - Perform search")
    search_data = {
        "query": "Acme Corporation funding",
        "source": "news_api",
        "use_cache": True,
        "max_results": 20
    }
    response = requests.post(f"{BASE_URL}/search/query", json=search_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "cached" in data
    assert "results" in data
    print(f"  [OK] Search performed - {data['total_results']} results, cached: {data['cached']}")
    return data


def test_search_cached():
    """Test that second search returns cached results."""
    print("\n[TEST] POST /search/query - Verify caching works")
    search_data = {
        "query": "Acme Corporation funding",
        "source": "news_api",
        "use_cache": True,
        "max_results": 20
    }
    response = requests.post(f"{BASE_URL}/search/query", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] == True, "Second search should be cached"
    print(f"  [OK] Cached result returned successfully")


def test_list_cache_entries():
    """Test GET /search/cache - list cached entries."""
    print("\n[TEST] GET /search/cache - List cache entries")
    response = requests.get(f"{BASE_URL}/search/cache", params={"limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    print(f"  [OK] Found {data['total']} cache entries")
    return data


def test_get_cache_by_id():
    """Test GET /search/cache/{id} - get single cache entry."""
    # First get list to find an ID
    list_response = requests.get(f"{BASE_URL}/search/cache", params={"limit": 1})
    list_data = list_response.json()

    if list_data["total"] == 0:
        print("\n[SKIP] GET /search/cache/{id} - No cache entries to test")
        return

    cache_id = list_data["items"][0]["id"]

    print(f"\n[TEST] GET /search/cache/{cache_id} - Get single cache entry")
    response = requests.get(f"{BASE_URL}/search/cache/{cache_id}")
    assert response.status_code == 200
    cache_entry = response.json()
    assert cache_entry["id"] == cache_id
    print(f"  [OK] Retrieved cache entry: {cache_entry['query_text'][:50]}...")


def test_get_cache_not_found():
    """Test GET /search/cache/{id} with invalid ID - should return 404."""
    print("\n[TEST] GET /search/cache/99999 - Non-existent cache entry")
    response = requests.get(f"{BASE_URL}/search/cache/99999")
    assert response.status_code == 404
    print(f"  [OK] Correctly returned 404")


def test_get_cache_stats():
    """Test GET /search/cache/stats - get cache statistics."""
    print("\n[TEST] GET /search/cache/stats - Get cache statistics")
    response = requests.get(f"{BASE_URL}/search/cache/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_entries" in stats
    assert "active_entries" in stats
    assert "expired_entries" in stats
    assert "entries_by_source" in stats
    print(f"  [OK] Total entries: {stats['total_entries']}")
    print(f"       Active: {stats['active_entries']}, Expired: {stats['expired_entries']}")
    return stats


def test_search_cache_entries():
    """Test GET /search/cache/search/{query_text} - search cache entries."""
    print("\n[TEST] GET /search/cache/search/Acme - Search cache entries")
    response = requests.get(f"{BASE_URL}/search/cache/search/Acme", params={"limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    print(f"  [OK] Found {data['total']} matching cache entries")


def test_filter_by_source():
    """Test filtering cache entries by source."""
    print("\n[TEST] GET /search/cache?source=news_api - Filter by source")
    response = requests.get(f"{BASE_URL}/search/cache", params={"source": "news_api"})
    assert response.status_code == 200
    data = response.json()
    # Verify all returned entries have news_api source
    for item in data["items"]:
        assert item["source"] == "news_api"
    print(f"  [OK] Found {data['total']} cache entries for news_api")


def test_cleanup_expired_cache():
    """Test DELETE /search/cache/expired/cleanup - cleanup expired entries."""
    print("\n[TEST] DELETE /search/cache/expired/cleanup - Cleanup expired entries")
    response = requests.delete(f"{BASE_URL}/search/cache/expired/cleanup")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print(f"  [OK] {data['message']}")


def test_delete_cache_by_source():
    """Test DELETE /search/cache/source/{source} - delete by source."""
    # First create a cache entry for a specific source
    search_data = {
        "query": "Test query for deletion",
        "source": "test_source",
        "use_cache": False,
        "max_results": 5
    }
    requests.post(f"{BASE_URL}/search/query", json=search_data)

    print("\n[TEST] DELETE /search/cache/source/test_source - Delete by source")
    response = requests.delete(f"{BASE_URL}/search/cache/source/test_source")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print(f"  [OK] {data['message']}")


def test_delete_single_cache_entry():
    """Test DELETE /search/cache/{id} - delete single entry."""
    # First create a cache entry
    search_data = {
        "query": "Entry to be deleted",
        "source": "test_delete",
        "use_cache": False,
        "max_results": 5
    }
    requests.post(f"{BASE_URL}/search/query", json=search_data)

    # Get the cache entry
    list_response = requests.get(f"{BASE_URL}/search/cache", params={"source": "test_delete", "limit": 1})
    list_data = list_response.json()

    if list_data["total"] == 0:
        print("\n[SKIP] DELETE /search/cache/{id} - No entry to delete")
        return

    cache_id = list_data["items"][0]["id"]

    print(f"\n[TEST] DELETE /search/cache/{cache_id} - Delete single cache entry")
    response = requests.delete(f"{BASE_URL}/search/cache/{cache_id}")
    assert response.status_code == 200
    print(f"  [OK] Cache entry deleted successfully")

    # Verify it's gone
    response = requests.get(f"{BASE_URL}/search/cache/{cache_id}")
    assert response.status_code == 404
    print(f"  [OK] Verified cache entry is deleted")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Search & Cache API Endpoint Tests")
    print("=" * 60)

    try:
        # Search operations
        test_perform_search()
        test_search_cached()

        # Cache listing and retrieval
        test_list_cache_entries()
        test_get_cache_by_id()
        test_get_cache_not_found()
        test_get_cache_stats()
        test_search_cache_entries()
        test_filter_by_source()

        # Cache management
        test_delete_single_cache_entry()
        test_cleanup_expired_cache()
        test_delete_cache_by_source()

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
