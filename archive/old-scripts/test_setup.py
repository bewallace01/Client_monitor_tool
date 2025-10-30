"""
Quick test script to verify the setup is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all modules can be imported."""
    print("[*] Testing imports...")

    try:
        from config import settings
        print("  [OK] Config imported")

        from src.models import Client, Event, SearchCache
        print("  [OK] Models imported")

        from src.storage import Database, ClientRepository, EventRepository
        print("  [OK] Storage imported")

        from src.collectors import MockCollector
        print("  [OK] Collectors imported")

        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_database():
    """Test database creation and basic operations."""
    print("\n[*] Testing database...")

    try:
        from src.storage import Database
        db = Database()
        db.create_tables()
        print("  [OK] Database tables created")

        # Test session
        with db.get_session() as session:
            print("  [OK] Database session created")

        return True
    except Exception as e:
        print(f"  [FAIL] Database test failed: {e}")
        return False


def test_mock_collector():
    """Test mock collector."""
    print("\n[*] Testing mock collector...")

    try:
        from src.collectors import MockCollector
        from datetime import datetime, timedelta

        collector = MockCollector()
        results = collector.get_company_news(
            company_name="TestCorp",
            from_date=datetime.utcnow() - timedelta(days=7),
            max_results=5
        )

        print(f"  [OK] Generated {len(results)} mock news items")

        if results:
            print(f"  [OK] Sample: {results[0].title}")

        return True
    except Exception as e:
        print(f"  [FAIL] Mock collector test failed: {e}")
        return False


def test_repository():
    """Test repository operations."""
    print("\n[*] Testing repository operations...")

    try:
        from src.storage import Database, ClientRepository
        db = Database()

        with db.get_session() as session:
            # Create a test client
            client = ClientRepository.create(
                session,
                name="Test Company",
                industry="Technology"
            )
            print(f"  [OK] Created test client: {client.name}")

            # Retrieve it
            retrieved = ClientRepository.get_by_id(session, client.id)
            assert retrieved.name == "Test Company"
            print(f"  [OK] Retrieved client by ID")

            # Clean up
            ClientRepository.delete(session, client.id)
            print(f"  [OK] Deleted test client")

        return True
    except Exception as e:
        print(f"  [FAIL] Repository test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running setup tests...\n")

    tests = [
        test_imports,
        test_database,
        test_mock_collector,
        test_repository,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 50)
    if all(results):
        print("[SUCCESS] All tests passed! Setup is working correctly.")
        print("\nNext steps:")
        print("  1. Run: python scripts/seed_data.py")
        print("  2. Run: streamlit run app.py")
    else:
        print("[FAILED] Some tests failed. Please check the errors above.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
