"""Verify database tables were created."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import inspect
from app.database.connection import engine

def verify_tables():
    """Verify all tables exist in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Database Tables:")
    print("-" * 60)
    for table in sorted(tables):
        print(f"  - {table}")
        columns = inspector.get_columns(table)
        print(f"    Columns: {len(columns)}")
        for col in columns:
            print(f"      {col['name']}: {col['type']}")
    print("-" * 60)
    print(f"Total tables: {len(tables)}")

    # Expected tables
    expected = {"clients", "events", "search_cache", "job_runs", "alembic_version"}
    missing = expected - set(tables)

    if missing:
        print(f"\n[WARNING] Missing tables: {missing}")
        return False
    else:
        print("\n[OK] All expected tables found!")
        return True

if __name__ == "__main__":
    success = verify_tables()
    sys.exit(0 if success else 1)
