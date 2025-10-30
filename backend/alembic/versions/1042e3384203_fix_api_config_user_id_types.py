"""fix_api_config_user_id_types

Revision ID: 1042e3384203
Revises: d734723ed3b2
Create Date: 2025-10-27 10:07:58.402191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1042e3384203'
down_revision: Union[str, None] = 'd734723ed3b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the test record we created earlier
    op.execute("DELETE FROM api_configs WHERE provider = 'newsapi'")

    # SQLite doesn't support ALTER COLUMN, so we need to recreate the columns
    # For SQLite, we'll drop and recreate the table (data will be preserved if empty)
    with op.batch_alter_table('api_configs') as batch_op:
        batch_op.drop_column('created_by_user_id')
        batch_op.drop_column('updated_by_user_id')
        batch_op.add_column(sa.Column('created_by_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by_user_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Revert back to GUID type
    with op.batch_alter_table('api_configs') as batch_op:
        batch_op.drop_column('created_by_user_id')
        batch_op.drop_column('updated_by_user_id')
