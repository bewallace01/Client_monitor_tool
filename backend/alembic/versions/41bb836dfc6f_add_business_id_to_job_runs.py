"""add_business_id_to_job_runs

Revision ID: 41bb836dfc6f
Revises: 1042e3384203
Create Date: 2025-10-27 14:35:35.889505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


# revision identifiers, used by Alembic.
revision: str = '41bb836dfc6f'
down_revision: Union[str, None] = '1042e3384203'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('job_runs', schema=None) as batch_op:
        # Add business_id column to job_runs table
        batch_op.add_column(sa.Column('business_id', sa.CHAR(36), nullable=True))

        # Add foreign key constraint
        batch_op.create_foreign_key(
            'fk_job_runs_business_id',
            'businesses',
            ['business_id'], ['id'],
            ondelete='CASCADE'
        )

        # Add indexes for better query performance
        batch_op.create_index('ix_job_runs_business_id', ['business_id'])
        batch_op.create_index('ix_job_runs_business_status', ['business_id', 'status'])
        batch_op.create_index('ix_job_runs_business_type', ['business_id', 'job_type'])


def downgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('job_runs', schema=None) as batch_op:
        # Drop indexes
        batch_op.drop_index('ix_job_runs_business_type')
        batch_op.drop_index('ix_job_runs_business_status')
        batch_op.drop_index('ix_job_runs_business_id')

        # Drop foreign key constraint
        batch_op.drop_constraint('fk_job_runs_business_id', type_='foreignkey')

        # Drop column
        batch_op.drop_column('business_id')
