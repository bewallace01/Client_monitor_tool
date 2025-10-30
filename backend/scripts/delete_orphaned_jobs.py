"""Delete all job runs without a business_id assignment."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.job_run import JobRun

def delete_orphaned_jobs():
    """Delete all job runs that don't have a business_id."""
    db: Session = SessionLocal()

    try:
        # Count orphaned jobs
        orphaned_count = db.query(JobRun).filter(JobRun.business_id.is_(None)).count()

        if orphaned_count == 0:
            print("No orphaned jobs found. Nothing to delete.")
            return

        print(f"Found {orphaned_count} orphaned job runs without business_id")

        # Confirm deletion
        confirmation = input(f"\nAre you sure you want to DELETE all {orphaned_count} orphaned jobs? (yes/no): ")

        if confirmation.lower() != 'yes':
            print("Deletion cancelled.")
            return

        # Delete orphaned jobs
        deleted = db.query(JobRun).filter(JobRun.business_id.is_(None)).delete(synchronize_session=False)
        db.commit()

        print(f"\nSuccessfully deleted {deleted} orphaned job runs!")

        # Verify
        remaining = db.query(JobRun).filter(JobRun.business_id.is_(None)).count()
        total = db.query(JobRun).count()
        print(f"Remaining jobs in database: {total}")
        print(f"Orphaned jobs remaining: {remaining}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_orphaned_jobs()
