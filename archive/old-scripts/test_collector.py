"""Quick test script for the mock collector."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.collectors import get_collector

def test_collector():
    """Test the mock collector functionality."""
    print("=" * 60)
    print("Testing Mock Collector")
    print("=" * 60)

    # Get collector
    print("\n1. Initializing collector...")
    collector = get_collector()
    print(f"   [OK] Collector: {collector.collector_name}")
    print(f"   [OK] Is Mock: {collector.is_mock}")

    # Check rate limit
    print("\n2. Checking rate limit status...")
    rate_limit = collector.get_rate_limit_status()
    print(f"   [OK] Limit: {rate_limit['limit']}")
    print(f"   [OK] Remaining: {rate_limit['remaining']}")
    print(f"   [OK] Reset At: {rate_limit['reset_at']}")

    # Test search with different keywords
    test_queries = [
        ("TechCorp funding", "Should return funding-related news"),
        ("Acme Corp acquisition", "Should return acquisition-related news"),
        ("StartupXYZ CEO", "Should return leadership-related news"),
        ("CompanyABC product launch", "Should return product-related news"),
    ]

    for query, description in test_queries:
        print(f"\n3. Testing search: '{query}'")
        print(f"   Description: {description}")

        from_date = datetime.utcnow() - timedelta(days=30)
        start_time = datetime.utcnow()

        results = collector.search(
            query=query,
            from_date=from_date,
            max_results=5
        )

        duration = (datetime.utcnow() - start_time).total_seconds()

        print(f"   [OK] Found {len(results)} results in {duration:.2f} seconds")

        if results:
            print(f"\n   Sample result:")
            sample = results[0]
            print(f"   - Title: {sample.title}")
            print(f"   - Source: {sample.source}")
            print(f"   - Published: {sample.published_at.strftime('%Y-%m-%d %H:%M')}")
            if sample.raw_data:
                print(f"   - Category: {sample.raw_data.get('category', 'N/A')}")

    # Final rate limit check
    print("\n4. Final rate limit check...")
    rate_limit = collector.get_rate_limit_status()
    print(f"   [OK] Remaining: {rate_limit['remaining']}/{rate_limit['limit']}")

    print("\n" + "=" * 60)
    print("[PASS] All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_collector()
