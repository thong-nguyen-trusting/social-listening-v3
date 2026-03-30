"""add run-compatible alias columns for validator queries

Revision ID: 003_add_run_alias_columns
Revises: 002_add_approval_invalidated_flag
Create Date: 2026-03-28 21:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "003_add_run_alias_columns"
down_revision = "002_add_approval_invalidated_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("step_runs", sa.Column("checkpoint", sa.Text(), nullable=True))
    op.add_column("crawled_posts", sa.Column("run_id", sa.Text(), nullable=True))
    op.add_column("crawled_posts", sa.Column("content", sa.Text(), nullable=True))

    op.execute("UPDATE step_runs SET checkpoint = checkpoint_json WHERE checkpoint IS NULL")
    op.execute("UPDATE crawled_posts SET content = content_masked WHERE content IS NULL")
    op.execute(
        """
        UPDATE crawled_posts
        SET run_id = (
            SELECT step_runs.run_id
            FROM step_runs
            WHERE step_runs.step_run_id = crawled_posts.step_run_id
        )
        WHERE run_id IS NULL
        """
    )

    with op.batch_alter_table("crawled_posts") as batch_op:
        batch_op.alter_column("run_id", existing_type=sa.Text(), nullable=False)
        batch_op.alter_column("content", existing_type=sa.Text(), nullable=False)
        batch_op.create_foreign_key(
            "fk_crawled_posts_run_id_plan_runs",
            "plan_runs",
            ["run_id"],
            ["run_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("crawled_posts") as batch_op:
        batch_op.drop_constraint("fk_crawled_posts_run_id_plan_runs", type_="foreignkey")
        batch_op.drop_column("content")
        batch_op.drop_column("run_id")
    op.drop_column("step_runs", "checkpoint")
