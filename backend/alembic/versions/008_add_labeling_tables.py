"""add phase 2 labeling tables

Revision ID: 008_add_labeling_tables
Revises: 007_add_crawled_post_metadata
Create Date: 2026-03-29 11:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "008_add_labeling_tables"
down_revision = "007_add_crawled_post_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "label_jobs",
        sa.Column("label_job_id", sa.Text(), nullable=False),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("taxonomy_version", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="PENDING"),
        sa.Column("records_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_labeled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_fallback", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.Text(), nullable=True),
        sa.Column("ended_at", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Text(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','DONE','FAILED','CANCELLED','PARTIAL')",
            name="ck_label_jobs_status",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["plan_runs.run_id"]),
        sa.PrimaryKeyConstraint("label_job_id"),
        sa.UniqueConstraint("run_id", "taxonomy_version", name="uq_label_jobs_run_taxonomy_version"),
    )
    op.create_table(
        "content_labels",
        sa.Column("label_id", sa.Text(), nullable=False),
        sa.Column("post_id", sa.Text(), nullable=False),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("label_job_id", sa.Text(), nullable=False),
        sa.Column("taxonomy_version", sa.Text(), nullable=False),
        sa.Column("author_role", sa.Text(), nullable=False),
        sa.Column("content_intent", sa.Text(), nullable=False),
        sa.Column("commerciality_level", sa.Text(), nullable=False),
        sa.Column("user_feedback_relevance", sa.Text(), nullable=False),
        sa.Column("label_confidence", sa.Float(), nullable=False),
        sa.Column("label_reason", sa.Text(), nullable=False),
        sa.Column("label_source", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.Text(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "author_role IN ('end_user','seller_affiliate','brand_official','community_admin','unknown')",
            name="ck_content_labels_author_role",
        ),
        sa.CheckConstraint(
            "content_intent IN ('experience','question','promotion','support_answer','comparison','other')",
            name="ck_content_labels_content_intent",
        ),
        sa.CheckConstraint(
            "commerciality_level IN ('low','medium','high')",
            name="ck_content_labels_commerciality_level",
        ),
        sa.CheckConstraint(
            "user_feedback_relevance IN ('high','medium','low')",
            name="ck_content_labels_user_feedback_relevance",
        ),
        sa.CheckConstraint(
            "label_source IN ('heuristic','ai','hybrid','fallback')",
            name="ck_content_labels_label_source",
        ),
        sa.ForeignKeyConstraint(["label_job_id"], ["label_jobs.label_job_id"]),
        sa.ForeignKeyConstraint(["post_id"], ["crawled_posts.post_id"]),
        sa.ForeignKeyConstraint(["run_id"], ["plan_runs.run_id"]),
        sa.PrimaryKeyConstraint("label_id"),
    )
    with op.batch_alter_table("crawled_posts", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column(
                "label_status",
                sa.Text(),
                nullable=False,
                server_default="PENDING",
            )
        )
        batch_op.add_column(sa.Column("current_label_id", sa.Text(), nullable=True))
        batch_op.create_foreign_key(
            "fk_crawled_posts_current_label_id",
            "content_labels",
            ["current_label_id"],
            ["label_id"],
        )
        batch_op.create_check_constraint(
            "ck_crawled_posts_label_status",
            "label_status IN ('PENDING','LABELED','FALLBACK','FAILED')",
        )


def downgrade() -> None:
    with op.batch_alter_table("crawled_posts", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_crawled_posts_label_status", type_="check")
        batch_op.drop_constraint("fk_crawled_posts_current_label_id", type_="foreignkey")
        batch_op.drop_column("current_label_id")
        batch_op.drop_column("label_status")
    op.drop_table("content_labels")
    op.drop_table("label_jobs")
