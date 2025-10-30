"""Verify job_runs table has business_id column."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from app.database.connection import engine

def verify_schema():
    """Verify the job_runs table schema includes business_id."""
    inspector = inspect(engine)

    # Get columns for job_runs table
    columns = inspector.get_columns('job_runs')

    print("job_runs table columns:")
    print("-" * 50)
    for col in columns:
        print(f"  {col['name']}: {col['type']} (nullable={col['nullable']})")

    # Check if business_id exists
    column_names = [col['name'] for col in columns]
    if 'business_id' in column_names:
        print("\n✓ business_id column exists!")
    else:
        print("\n✗ business_id column NOT found!")
        return False

    # Get foreign keys
    print("\nForeign keys:")
    print("-" * 50)
    fks = inspector.get_foreign_keys('job_runs')
    for fk in fks:
        print(f"  {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

    # Get indexes
    print("\nIndexes:")
    print("-" * 50)
    indexes = inspector.get_indexes('job_runs')
    for idx in indexes:
        print(f"  {idx['name']}: {idx['column_names']}")

    return True

if __name__ == "__main__":
    verify_schema()
