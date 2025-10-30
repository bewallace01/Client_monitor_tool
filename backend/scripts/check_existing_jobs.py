"""Check existing job runs and their business_id assignments."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.job_run import JobRun
from app.models.business import Business

def check_jobs():
    """Check existing job runs."""
    db: Session = SessionLocal()

    try:
        # Get all job runs
        all_jobs = db.query(JobRun).all()
        print(f"Total job runs in database: {len(all_jobs)}")

        # Count jobs by business_id
        jobs_with_business = db.query(JobRun).filter(JobRun.business_id.isnot(None)).count()
        jobs_without_business = db.query(JobRun).filter(JobRun.business_id.is_(None)).count()

        print(f"\nJobs with business_id: {jobs_with_business}")
        print(f"Jobs without business_id (orphaned): {jobs_without_business}")

        # Get all businesses
        businesses = db.query(Business).all()
        print(f"\nTotal businesses: {len(businesses)}")
        for biz in businesses:
            print(f"  - {biz.name} (ID: {biz.id})")

        # Show sample of orphaned jobs
        if jobs_without_business > 0:
            print(f"\nSample orphaned jobs (first 5):")
            orphaned = db.query(JobRun).filter(JobRun.business_id.is_(None)).limit(5).all()
            for job in orphaned:
                print(f"  - Job ID: {job.id}")
                print(f"    Type: {job.job_type}")
                print(f"    Status: {job.status}")
                print(f"    Started: {job.started_at}")
                print(f"    Business ID: {job.business_id}")
                print()

    finally:
        db.close()

if __name__ == "__main__":
    check_jobs()
