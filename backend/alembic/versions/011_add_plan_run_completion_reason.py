"""add plan run completion reason

Revision ID: 011_add_plan_run_completion_reason
Revises: 010_add_phase7_retrieval_gating_fields
Create Date: 2026-03-31 11:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "011_add_plan_run_completion_reason"
down_revision = "010_add_phase7_retrieval_gating_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("plan_runs") as batch_op:
        batch_op.add_column(sa.Column("completion_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("plan_runs") as batch_op:
        batch_op.drop_column("completion_reason")
