"""Test multi-tenant job run filtering."""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.job_run import JobRun
from app.models.business import Business
from app.services.scheduler_service import SchedulerService
from app.schemas.job_run import JobRunCreate, JobStatus

def test_multitenant_filtering():
    """Test that job runs are properly filtered by business_id."""
    db: Session = SessionLocal()

    try:
        # Get businesses
        businesses = db.query(Business).all()
        if len(businesses) < 2:
            print("Need at least 2 businesses to test multi-tenancy. Skipping.")
            return

        biz1 = businesses[0]
        biz2 = businesses[1]

        print(f"Testing with:")
        print(f"  Business 1: {biz1.name} ({biz1.id})")
        print(f"  Business 2: {biz2.name} ({biz2.id})")

        # Create test jobs for each business
        print("\n--- Creating test jobs ---")

        # Business 1 jobs
        job1_biz1 = JobRunCreate(
            job_id=str(uuid.uuid4()),
            job_type="test_scan",
            business_id=biz1.id,
            status=JobStatus.COMPLETED,
            started_at=datetime.utcnow()
        )
        created_job1 = SchedulerService.create_job_run(db, job1_biz1)
        print(f"Created job for {biz1.name}: {created_job1.id}")

        job2_biz1 = JobRunCreate(
            job_id=str(uuid.uuid4()),
            job_type="test_report",
            business_id=biz1.id,
            status=JobStatus.COMPLETED,
            started_at=datetime.utcnow()
        )
        created_job2 = SchedulerService.create_job_run(db, job2_biz1)
        print(f"Created job for {biz1.name}: {created_job2.id}")

        # Business 2 jobs
        job1_biz2 = JobRunCreate(
            job_id=str(uuid.uuid4()),
            job_type="test_scan",
            business_id=biz2.id,
            status=JobStatus.COMPLETED,
            started_at=datetime.utcnow()
        )
        created_job3 = SchedulerService.create_job_run(db, job1_biz2)
        print(f"Created job for {biz2.name}: {created_job3.id}")

        # Test filtering
        print("\n--- Testing filtering ---")

        # Query for Business 1
        biz1_jobs, biz1_total = SchedulerService.get_job_runs(db, business_id=biz1.id)
        print(f"\n{biz1.name} jobs (should be 2): {biz1_total}")
        for job in biz1_jobs:
            print(f"  - {job.job_type} (business_id: {job.business_id})")

        # Query for Business 2
        biz2_jobs, biz2_total = SchedulerService.get_job_runs(db, business_id=biz2.id)
        print(f"\n{biz2.name} jobs (should be 1): {biz2_total}")
        for job in biz2_jobs:
            print(f"  - {job.job_type} (business_id: {job.business_id})")

        # Query for system admin (all jobs)
        all_jobs, all_total = SchedulerService.get_job_runs(db, business_id=None)
        print(f"\nSystem Admin view - all jobs (should be 3): {all_total}")
        for job in all_jobs:
            print(f"  - {job.job_type} (business_id: {job.business_id})")

        # Test statistics
        print("\n--- Testing statistics ---")

        biz1_stats = SchedulerService.get_job_run_stats(db, business_id=biz1.id)
        print(f"\n{biz1.name} stats:")
        print(f"  Total runs: {biz1_stats['total_runs']}")
        print(f"  Completed: {biz1_stats['completed_runs']}")

        biz2_stats = SchedulerService.get_job_run_stats(db, business_id=biz2.id)
        print(f"\n{biz2.name} stats:")
        print(f"  Total runs: {biz2_stats['total_runs']}")
        print(f"  Completed: {biz2_stats['completed_runs']}")

        all_stats = SchedulerService.get_job_run_stats(db, business_id=None)
        print(f"\nSystem Admin stats (all businesses):")
        print(f"  Total runs: {all_stats['total_runs']}")
        print(f"  Completed: {all_stats['completed_runs']}")

        # Validation
        print("\n--- Validation ---")
        success = True

        if biz1_total != 2:
            print(f"FAIL: Business 1 should have 2 jobs, but has {biz1_total}")
            success = False

        if biz2_total != 1:
            print(f"FAIL: Business 2 should have 1 job, but has {biz2_total}")
            success = False

        if all_total != 3:
            print(f"FAIL: System admin should see 3 jobs, but sees {all_total}")
            success = False

        if success:
            print("SUCCESS: All multi-tenant filtering tests passed!")
        else:
            print("FAILED: Some tests did not pass")

        # Cleanup test jobs
        print("\n--- Cleaning up test jobs ---")
        for job in [created_job1, created_job2, created_job3]:
            SchedulerService.delete_job_run(db, job.id)
            print(f"Deleted test job: {job.id}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_multitenant_filtering()
