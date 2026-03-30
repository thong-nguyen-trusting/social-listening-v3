"""add approval invalidated flag

Revision ID: 002_add_approval_invalidated_flag
Revises: 001_initial_schema
Create Date: 2026-03-28 21:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "002_add_approval_invalidated_flag"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "approval_grants",
        sa.Column("invalidated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("approval_grants", "invalidated")

