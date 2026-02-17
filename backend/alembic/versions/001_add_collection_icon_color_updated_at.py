"""Add icon, color, updated_at to collections table.

Revision ID: 001
Revises: None
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import time

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

_now_ms = int(time.time() * 1000)


def upgrade() -> None:
    with op.batch_alter_table("collections") as batch_op:
        batch_op.add_column(sa.Column("icon", sa.Text(), nullable=True, server_default="📁"))
        batch_op.add_column(sa.Column("color", sa.Text(), nullable=True, server_default="#7C5CFC"))
        batch_op.add_column(sa.Column("updated_at", sa.Integer(), nullable=False, server_default=str(_now_ms)))


def downgrade() -> None:
    with op.batch_alter_table("collections") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("color")
        batch_op.drop_column("icon")
