"""add clarification state to product contexts

Revision ID: 009_add_context_clarification_state
Revises: 008_add_labeling_tables
Create Date: 2026-03-29 20:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "009_add_context_clarification_state"
down_revision = "008_add_labeling_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("product_contexts", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("clarifying_question_json", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("clarification_history_json", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("product_contexts", recreate="always") as batch_op:
        batch_op.drop_column("clarification_history_json")
        batch_op.drop_column("clarifying_question_json")
