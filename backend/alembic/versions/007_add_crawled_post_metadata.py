"""add metadata columns for crawled posts and comments

Revision ID: 007_add_crawled_post_metadata
Revises: 006_add_post_first_actions
Create Date: 2026-03-29 03:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "007_add_crawled_post_metadata"
down_revision = "006_add_post_first_actions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("crawled_posts", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column(
                "record_type",
                sa.Text(),
                nullable=False,
                server_default="POST",
            )
        )
        batch_op.add_column(sa.Column("source_url", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("parent_post_id", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("parent_post_url", sa.Text(), nullable=True))
        batch_op.create_check_constraint(
            "ck_crawled_posts_record_type",
            "record_type IN ('POST','COMMENT')",
        )


def downgrade() -> None:
    with op.batch_alter_table("crawled_posts", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_crawled_posts_record_type", type_="check")
        batch_op.drop_column("parent_post_url")
        batch_op.drop_column("parent_post_id")
        batch_op.drop_column("source_url")
        batch_op.drop_column("record_type")
