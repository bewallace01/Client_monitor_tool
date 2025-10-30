"""Test Client API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_get_clients():
    """Test GET /clients - list with pagination."""
    print("\n[TEST] GET /clients - List with pagination")
    response = requests.get(f"{BASE_URL}/clients", params={"limit": 5})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 5
    print(f"  [OK] Returned {len(data['items'])} of {data['total']} total clients")
    return data

def test_get_client_by_id():
    """Test GET /clients/{id} - get single client."""
    print("\n[TEST] GET /clients/1 - Get single client")
    response = requests.get(f"{BASE_URL}/clients/1")
    assert response.status_code == 200
    client = response.json()
    assert "id" in client
    assert client["id"] == 1
    print(f"  [OK] Retrieved client: {client['name']}")
    return client

def test_get_client_not_found():
    """Test GET /clients/{id} with invalid ID - should return 404."""
    print("\n[TEST] GET /clients/99999 - Non-existent client")
    response = requests.get(f"{BASE_URL}/clients/99999")
    assert response.status_code == 404
    print(f"  [OK] Correctly returned 404")

def test_filter_by_industry():
    """Test filtering clients by industry."""
    print("\n[TEST] GET /clients?industry=Technology")
    response = requests.get(f"{BASE_URL}/clients", params={"industry": "Technology"})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['total']} Technology clients")

def test_search_clients():
    """Test search functionality."""
    print("\n[TEST] GET /clients?search=salesforce")
    response = requests.get(f"{BASE_URL}/clients", params={"search": "salesforce"})
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Search returned {data['total']} results")

def test_get_stats():
    """Test GET /clients/stats."""
    print("\n[TEST] GET /clients/stats")
    response = requests.get(f"{BASE_URL}/clients/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_clients" in stats
    assert "active_clients" in stats
    print(f"  [OK] Total: {stats['total_clients']}, Active: {stats['active_clients']}")

def test_get_industries():
    """Test GET /clients/industries."""
    print("\n[TEST] GET /clients/industries")
    response = requests.get(f"{BASE_URL}/clients/industries")
    assert response.status_code == 200
    industries = response.json()
    assert isinstance(industries, list)
    print(f"  [OK] Found {len(industries)} unique industries: {', '.join(industries[:5])}...")

def test_get_tiers():
    """Test GET /clients/tiers."""
    print("\n[TEST] GET /clients/tiers")
    response = requests.get(f"{BASE_URL}/clients/tiers")
    assert response.status_code == 200
    tiers = response.json()
    assert isinstance(tiers, list)
    print(f"  [OK] Found {len(tiers)} unique tiers: {', '.join(tiers)}")

def test_create_client():
    """Test POST /clients - create new client."""
    print("\n[TEST] POST /clients - Create new client")
    new_client = {
        "name": "Test Client API",
        "domain": "testclient.api",
        "industry": "Technology",
        "description": "Test client created via API",
        "is_active": True,
        "tier": "Test"
    }
    response = requests.post(f"{BASE_URL}/clients", json=new_client)
    assert response.status_code == 201
    client = response.json()
    assert client["name"] == new_client["name"]
    print(f"  [OK] Created client with ID: {client['id']}")
    return client

def test_update_client(client_id):
    """Test PUT /clients/{id} - update client."""
    print(f"\n[TEST] PUT /clients/{client_id} - Update client")
    update_data = {
        "notes": "Updated via API test",
        "is_active": False
    }
    response = requests.put(f"{BASE_URL}/clients/{client_id}", json=update_data)
    assert response.status_code == 200
    client = response.json()
    assert client["notes"] == update_data["notes"]
    assert client["is_active"] == update_data["is_active"]
    print(f"  [OK] Updated client successfully")

def test_delete_client(client_id):
    """Test DELETE /clients/{id} - delete client."""
    print(f"\n[TEST] DELETE /clients/{client_id} - Delete client")
    response = requests.delete(f"{BASE_URL}/clients/{client_id}")
    assert response.status_code == 200
    print(f"  [OK] Deleted client successfully")

    # Verify it's gone
    response = requests.get(f"{BASE_URL}/clients/{client_id}")
    assert response.status_code == 404
    print(f"  [OK] Verified client is deleted")

def test_sorting():
    """Test sorting functionality."""
    print("\n[TEST] GET /clients?sort_by=name&sort_desc=false")
    response = requests.get(f"{BASE_URL}/clients", params={
        "sort_by": "name",
        "sort_desc": False,
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    names = [client["name"] for client in data["items"]]
    print(f"  [OK] First 5 clients sorted by name: {', '.join(names)}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Client API Endpoint Tests")
    print("=" * 60)

    try:
        # Read operations
        test_get_clients()
        test_get_client_by_id()
        test_get_client_not_found()
        test_filter_by_industry()
        test_search_clients()
        test_get_stats()
        test_get_industries()
        test_get_tiers()
        test_sorting()

        # Write operations
        new_client = test_create_client()
        test_update_client(new_client["id"])
        test_delete_client(new_client["id"])

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
