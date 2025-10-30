"""Cleanup orphaned job runs without business_id

This data migration removes any job runs that were created before
multi-tenancy was implemented and don't have a business_id assigned.

Revision ID: 42_cleanup_orphaned
Revises: 41bb836dfc6f
Create Date: 2025-10-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42_cleanup_orphaned'
down_revision: Union[str, None] = '41bb836dfc6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Delete all job runs without a business_id (orphaned from before multi-tenancy)."""
    # Get connection
    conn = op.get_bind()

    # Count orphaned jobs
    result = conn.execute(sa.text("SELECT COUNT(*) FROM job_runs WHERE business_id IS NULL"))
    count = result.scalar()

    if count > 0:
        print(f"Found {count} orphaned job runs without business_id. Deleting...")
        # Delete orphaned jobs
        conn.execute(sa.text("DELETE FROM job_runs WHERE business_id IS NULL"))
        print(f"Deleted {count} orphaned job runs.")
    else:
        print("No orphaned job runs found. Skipping cleanup.")


def downgrade() -> None:
    """Cannot restore deleted data."""
    # This is a data migration - we cannot restore deleted job runs
    # Just log a message
    print("Warning: This migration deleted orphaned job runs. Data cannot be restored.")
    pass
