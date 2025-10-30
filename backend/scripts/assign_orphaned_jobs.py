"""Assign all orphaned job runs to a specific business."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.job_run import JobRun
from app.models.business import Business
from uuid import UUID

def assign_orphaned_jobs():
    """Assign all job runs without business_id to a specific business."""
    db: Session = SessionLocal()

    try:
        # Count orphaned jobs
        orphaned_count = db.query(JobRun).filter(JobRun.business_id.is_(None)).count()

        if orphaned_count == 0:
            print("No orphaned jobs found. Nothing to assign.")
            return

        print(f"Found {orphaned_count} orphaned job runs without business_id")

        # List available businesses
        businesses = db.query(Business).all()
        print("\nAvailable businesses:")
        for i, biz in enumerate(businesses, 1):
            print(f"  {i}. {biz.name} (ID: {biz.id})")

        # Get user choice
        choice = input(f"\nEnter the number of the business to assign these jobs to (1-{len(businesses)}): ")

        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(businesses):
                print("Invalid choice. Operation cancelled.")
                return

            selected_business = businesses[choice_idx]
        except ValueError:
            print("Invalid input. Operation cancelled.")
            return

        # Confirm assignment
        confirmation = input(f"\nAssign all {orphaned_count} orphaned jobs to '{selected_business.name}'? (yes/no): ")

        if confirmation.lower() != 'yes':
            print("Assignment cancelled.")
            return

        # Update orphaned jobs
        updated = db.query(JobRun).filter(JobRun.business_id.is_(None)).update(
            {JobRun.business_id: selected_business.id},
            synchronize_session=False
        )
        db.commit()

        print(f"\nSuccessfully assigned {updated} orphaned jobs to '{selected_business.name}'!")

        # Verify
        remaining = db.query(JobRun).filter(JobRun.business_id.is_(None)).count()
        print(f"Orphaned jobs remaining: {remaining}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    assign_orphaned_jobs()
