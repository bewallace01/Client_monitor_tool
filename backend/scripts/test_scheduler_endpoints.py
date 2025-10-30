"""Test Scheduler API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_get_job_runs():
    """Test GET /scheduler/jobs - list with pagination."""
    print("\n[TEST] GET /scheduler/jobs - List with pagination")
    response = requests.get(f"{BASE_URL}/scheduler/jobs", params={"limit": 10})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10
    print(f"  [OK] Returned {len(data['items'])} of {data['total']} total job runs")
    return data


def test_get_job_run_by_id():
    """Test GET /scheduler/jobs/{id} - get single job run."""
    print("\n[TEST] GET /scheduler/jobs/1 - Get single job run")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/1")
    assert response.status_code == 200
    job = response.json()
    assert "id" in job
    assert job["id"] == 1
    print(f"  [OK] Retrieved job run: {job['job_type']} - {job['status']}")
    return job


def test_get_job_run_not_found():
    """Test GET /scheduler/jobs/{id} with invalid ID - should return 404."""
    print("\n[TEST] GET /scheduler/jobs/99999 - Non-existent job")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/99999")
    assert response.status_code == 404
    print(f"  [OK] Correctly returned 404")


def test_filter_by_status():
    """Test filtering job runs by status."""
    print("\n[TEST] GET /scheduler/jobs?status=completed")
    response = requests.get(f"{BASE_URL}/scheduler/jobs", params={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    # Verify all returned jobs have completed status
    for job in data["items"]:
        assert job["status"] == "completed"
    print(f"  [OK] Found {data['total']} completed jobs")


def test_get_job_stats():
    """Test GET /scheduler/jobs/stats."""
    print("\n[TEST] GET /scheduler/jobs/stats")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_runs" in stats
    assert "completed_runs" in stats
    assert "failed_runs" in stats
    assert "running_runs" in stats
    assert "pending_runs" in stats
    assert "runs_by_job_type" in stats
    assert "recent_runs" in stats
    print(f"  [OK] Total runs: {stats['total_runs']}")
    print(f"       Completed: {stats['completed_runs']}, Failed: {stats['failed_runs']}")
    print(f"       Running: {stats['running_runs']}, Pending: {stats['pending_runs']}")
    print(f"       Average duration: {stats.get('average_duration_seconds', 'N/A')} seconds")
    return stats


def test_get_recent_jobs():
    """Test GET /scheduler/jobs/recent."""
    print("\n[TEST] GET /scheduler/jobs/recent")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/recent", params={"limit": 5})
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    assert len(jobs) <= 5
    print(f"  [OK] Retrieved {len(jobs)} recent jobs")
    if jobs:
        print(f"       Most recent: {jobs[0]['job_type']} - {jobs[0]['status']}")


def test_get_active_jobs():
    """Test GET /scheduler/jobs/active."""
    print("\n[TEST] GET /scheduler/jobs/active")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/active")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    # Verify all are pending or running
    for job in jobs:
        assert job["status"] in ["pending", "running"]
    print(f"  [OK] Found {len(jobs)} active jobs")


def test_get_job_types():
    """Test GET /scheduler/jobs/types."""
    print("\n[TEST] GET /scheduler/jobs/types")
    response = requests.get(f"{BASE_URL}/scheduler/jobs/types")
    assert response.status_code == 200
    types = response.json()
    assert isinstance(types, list)
    print(f"  [OK] Found {len(types)} job types: {', '.join(types)}")


def test_trigger_job():
    """Test POST /scheduler/jobs/trigger - trigger new job."""
    print("\n[TEST] POST /scheduler/jobs/trigger - Trigger new job")
    trigger_data = {
        "job_type": "test_job",
        "job_metadata": {"test": True, "source": "api_test"}
    }
    response = requests.post(f"{BASE_URL}/scheduler/jobs/trigger", json=trigger_data)
    assert response.status_code == 201
    job = response.json()
    assert job["job_type"] == "test_job"
    assert job["status"] == "pending"
    assert "job_id" in job
    print(f"  [OK] Triggered job with ID: {job['id']}, job_id: {job['job_id']}")
    return job


def test_start_job(job_id):
    """Test POST /scheduler/jobs/{id}/start - start job."""
    print(f"\n[TEST] POST /scheduler/jobs/{job_id}/start - Start job")
    response = requests.post(f"{BASE_URL}/scheduler/jobs/{job_id}/start")
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "running"
    print(f"  [OK] Job started successfully")
    return job


def test_complete_job(job_id):
    """Test POST /scheduler/jobs/{id}/complete - complete job."""
    print(f"\n[TEST] POST /scheduler/jobs/{job_id}/complete - Complete job")
    response = requests.post(f"{BASE_URL}/scheduler/jobs/{job_id}/complete", params={
        "events_found": 10,
        "events_new": 5,
        "clients_processed": 3
    })
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "completed"
    assert job["events_found"] == 10
    assert job["events_new"] == 5
    assert job["clients_processed"] == 3
    print(f"  [OK] Job completed - {job['events_found']} events found, {job['events_new']} new")
    return job


def test_fail_job():
    """Test POST /scheduler/jobs/{id}/fail - fail job."""
    # First trigger a new job
    trigger_data = {"job_type": "test_fail_job"}
    response = requests.post(f"{BASE_URL}/scheduler/jobs/trigger", json=trigger_data)
    job = response.json()
    job_id = job["id"]

    print(f"\n[TEST] POST /scheduler/jobs/{job_id}/fail - Fail job")
    response = requests.post(
        f"{BASE_URL}/scheduler/jobs/{job_id}/fail",
        params={"error_message": "Test error message"}
    )
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "failed"
    assert job["error_message"] == "Test error message"
    print(f"  [OK] Job marked as failed with error message")
    return job


def test_create_job_run():
    """Test POST /scheduler/jobs - create job run."""
    print("\n[TEST] POST /scheduler/jobs - Create job run")
    new_job = {
        "job_id": "test-job-123",
        "job_type": "manual_test",
        "status": "pending",
        "events_found": 0,
        "events_new": 0,
        "clients_processed": 0
    }
    response = requests.post(f"{BASE_URL}/scheduler/jobs", json=new_job)
    assert response.status_code == 201
    job = response.json()
    assert job["job_type"] == "manual_test"
    print(f"  [OK] Created job run with ID: {job['id']}")
    return job


def test_update_job_run(job_id):
    """Test PUT /scheduler/jobs/{id} - update job run."""
    print(f"\n[TEST] PUT /scheduler/jobs/{job_id} - Update job run")
    update_data = {
        "events_found": 25,
        "events_new": 12
    }
    response = requests.put(f"{BASE_URL}/scheduler/jobs/{job_id}", json=update_data)
    assert response.status_code == 200
    job = response.json()
    assert job["events_found"] == 25
    assert job["events_new"] == 12
    print(f"  [OK] Updated job run successfully")


def test_delete_job_run(job_id):
    """Test DELETE /scheduler/jobs/{id} - delete job run."""
    print(f"\n[TEST] DELETE /scheduler/jobs/{job_id} - Delete job run")
    response = requests.delete(f"{BASE_URL}/scheduler/jobs/{job_id}")
    assert response.status_code == 200
    print(f"  [OK] Deleted job run successfully")

    # Verify it's gone
    response = requests.get(f"{BASE_URL}/scheduler/jobs/{job_id}")
    assert response.status_code == 404
    print(f"  [OK] Verified job run is deleted")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Scheduler API Endpoint Tests")
    print("=" * 60)

    try:
        # Read operations
        test_get_job_runs()
        test_get_job_run_by_id()
        test_get_job_run_not_found()
        test_filter_by_status()
        test_get_job_stats()
        test_get_recent_jobs()
        test_get_active_jobs()
        test_get_job_types()

        # Job lifecycle operations
        new_job = test_trigger_job()
        test_start_job(new_job["id"])
        test_complete_job(new_job["id"])
        test_fail_job()

        # CRUD operations
        created_job = test_create_job_run()
        test_update_job_run(created_job["id"])
        test_delete_job_run(created_job["id"])

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
