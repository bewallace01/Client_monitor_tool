"""Test script to validate Pydantic schemas."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import (
    # Client schemas
    ClientCreate, ClientUpdate, ClientResponse,
    # Event schemas
    EventCreate, EventUpdate, EventResponse, EventCategory,
    # SearchCache schemas
    SearchCacheCreate, SearchCacheResponse,
    # JobRun schemas
    JobRunCreate, JobRunUpdate, JobRunResponse, JobStatus,
    # Base schemas
    PaginationParams, MessageResponse, HealthResponse,
)


def test_client_schemas():
    """Test Client schemas."""
    print("Testing Client Schemas...")

    # Test ClientCreate
    client_create = ClientCreate(
        name="Test Corp",
        domain="https://test.com/",  # Should be normalized
        industry="Technology",
        description="Test company",
        search_keywords="Test, Corp, Testing",  # Should be trimmed
        is_active=True,
        account_owner="John Doe",
        tier="Enterprise"
    )
    assert client_create.domain == "test.com", f"Domain normalization failed: {client_create.domain}"
    assert client_create.search_keywords == "Test, Corp, Testing", "Keywords normalization failed"
    print("  [OK] ClientCreate validation passed")

    # Test ClientUpdate
    client_update = ClientUpdate(
        is_active=False,
        notes="Updated notes"
    )
    print("  [OK] ClientUpdate validation passed")

    print("[OK] Client schemas validated successfully\n")


def test_event_schemas():
    """Test Event schemas."""
    print("Testing Event Schemas...")

    # Test EventCreate
    event_create = EventCreate(
        client_id=1,
        title="Test Event",
        description="Test description",
        url="techcrunch.com/article",  # Should add https://
        source="TechCrunch",
        category=EventCategory.FUNDING,
        relevance_score=0.95,
        sentiment_score=0.8,
        event_date=datetime.utcnow()
    )
    assert event_create.url == "https://techcrunch.com/article", f"URL normalization failed: {event_create.url}"
    print("  [OK] EventCreate validation passed")

    # Test EventUpdate
    event_update = EventUpdate(
        is_read=True,
        is_starred=True,
        user_notes="Important event"
    )
    print("  [OK] EventUpdate validation passed")

    # Test category enum
    assert EventCategory.FUNDING.value == "funding"
    assert EventCategory.LEADERSHIP_CHANGE.value == "leadership_change"
    print("  [OK] EventCategory enum validated")

    print("[OK] Event schemas validated successfully\n")


def test_search_cache_schemas():
    """Test SearchCache schemas."""
    print("Testing SearchCache Schemas...")

    # Test SearchCacheCreate
    cache_create = SearchCacheCreate(
        query_hash="abc123def456",
        query_text="Test query",
        results_json='[{"title": "Test"}]',
        result_count=1,
        source="news_api",
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    print("  [OK] SearchCacheCreate validation passed")

    print("[OK] SearchCache schemas validated successfully\n")


def test_job_run_schemas():
    """Test JobRun schemas."""
    print("Testing JobRun Schemas...")

    # Test JobRunCreate
    job_create = JobRunCreate(
        job_id="test-job-001",
        job_name="test_job",
        start_time=datetime.utcnow(),
        job_metadata='{"key": "value"}'
    )
    print("  [OK] JobRunCreate validation passed")

    # Test JobRunUpdate
    job_update = JobRunUpdate(
        end_time=datetime.utcnow(),
        status=JobStatus.COMPLETED,
        results_summary="Job completed successfully"
    )
    print("  [OK] JobRunUpdate validation passed")

    # Test status enum
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
    print("  [OK] JobStatus enum validated")

    print("[OK] JobRun schemas validated successfully\n")


def test_base_schemas():
    """Test base schemas."""
    print("Testing Base Schemas...")

    # Test PaginationParams
    pagination = PaginationParams(page=2, page_size=20)
    assert pagination.offset == 20, f"Pagination offset calculation failed: {pagination.offset}"
    assert pagination.limit == 20, f"Pagination limit failed: {pagination.limit}"
    print("  [OK] PaginationParams validation passed")

    # Test MessageResponse
    message = MessageResponse(message="Test message")
    print("  [OK] MessageResponse validation passed")

    # Test HealthResponse
    health = HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )
    print("  [OK] HealthResponse validation passed")

    print("[OK] Base schemas validated successfully\n")


def test_field_validation():
    """Test field validation rules."""
    print("Testing Field Validation...")

    # Test min_length validation
    try:
        ClientCreate(name="", is_active=True)
        print("  [ERROR] Empty name should have failed validation")
        return False
    except Exception:
        print("  [OK] Empty name validation works")

    # Test relevance_score range validation
    try:
        EventCreate(
            client_id=1,
            title="Test",
            relevance_score=1.5,  # Invalid: > 1.0
            event_date=datetime.utcnow()
        )
        print("  [ERROR] relevance_score > 1.0 should have failed")
        return False
    except Exception:
        print("  [OK] Relevance score range validation works")

    # Test sentiment_score range validation
    try:
        EventCreate(
            client_id=1,
            title="Test",
            sentiment_score=-2.0,  # Invalid: < -1.0
            event_date=datetime.utcnow()
        )
        print("  [ERROR] sentiment_score < -1.0 should have failed")
        return False
    except Exception:
        print("  [OK] Sentiment score range validation works")

    print("[OK] Field validation working correctly\n")
    return True


def main():
    """Run all schema tests."""
    print("=" * 60)
    print("Pydantic Schema Validation Tests")
    print("=" * 60)
    print()

    try:
        test_client_schemas()
        test_event_schemas()
        test_search_cache_schemas()
        test_job_run_schemas()
        test_base_schemas()

        if not test_field_validation():
            print("\n[ERROR] Field validation tests failed")
            return False

        print("=" * 60)
        print("[OK] All schema tests passed successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
