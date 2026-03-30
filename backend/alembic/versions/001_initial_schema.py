"""initial schema - core phase 1 tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-28 20:50:00
"""

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_contexts",
        sa.Column("context_id", sa.Text(), nullable=False),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("keyword_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("context_id"),
    )
    op.create_table(
        "plans",
        sa.Column("plan_id", sa.Text(), nullable=False),
        sa.Column("context_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.CheckConstraint("status IN ('draft','ready','archived')", name="ck_plans_status"),
        sa.ForeignKeyConstraint(["context_id"], ["product_contexts.context_id"]),
        sa.PrimaryKeyConstraint("plan_id"),
    )
    op.create_table(
        "plan_steps",
        sa.Column("step_id", sa.Text(), nullable=False),
        sa.Column("plan_id", sa.Text(), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("read_or_write", sa.Text(), nullable=False),
        sa.Column("target", sa.Text(), nullable=False),
        sa.Column("estimated_count", sa.Integer(), nullable=True),
        sa.Column("estimated_duration_sec", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.Text(), nullable=False),
        sa.Column("dependency_step_ids", sa.Text(), nullable=False, server_default="[]"),
        sa.CheckConstraint(
            "action_type IN ('CRAWL_FEED','JOIN_GROUP','CRAWL_COMMENTS','CRAWL_GROUP_META','SEARCH_GROUPS')",
            name="ck_plan_steps_action_type",
        ),
        sa.CheckConstraint("read_or_write IN ('READ','WRITE')", name="ck_plan_steps_read_or_write"),
        sa.CheckConstraint("risk_level IN ('LOW','MEDIUM','HIGH')", name="ck_plan_steps_risk_level"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.plan_id"]),
        sa.PrimaryKeyConstraint("step_id"),
    )
    op.create_table(
        "approval_grants",
        sa.Column("grant_id", sa.Text(), nullable=False),
        sa.Column("plan_id", sa.Text(), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False),
        sa.Column("approved_step_ids", sa.Text(), nullable=False),
        sa.Column("approver_id", sa.Text(), nullable=False, server_default="local_user"),
        sa.Column("approved_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.Column("expires_at", sa.Text(), nullable=True),
        sa.Column("invalidated_at", sa.Text(), nullable=True),
        sa.Column("invalidated_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.plan_id"]),
        sa.PrimaryKeyConstraint("grant_id"),
    )
    op.create_table(
        "plan_runs",
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("plan_id", sa.Text(), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False),
        sa.Column("grant_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("started_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.Column("ended_at", sa.Text(), nullable=True),
        sa.Column("total_records", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "status IN ('RUNNING','PAUSED','DONE','FAILED','CANCELLED')",
            name="ck_plan_runs_status",
        ),
        sa.ForeignKeyConstraint(["grant_id"], ["approval_grants.grant_id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.plan_id"]),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_table(
        "step_runs",
        sa.Column("step_run_id", sa.Text(), nullable=False),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("step_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("started_at", sa.Text(), nullable=True),
        sa.Column("ended_at", sa.Text(), nullable=True),
        sa.Column("actual_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("checkpoint_json", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','DONE','FAILED','SKIPPED')",
            name="ck_step_runs_status",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["plan_runs.run_id"]),
        sa.ForeignKeyConstraint(["step_id"], ["plan_steps.step_id"]),
        sa.PrimaryKeyConstraint("step_run_id"),
    )
    op.create_table(
        "crawled_posts",
        sa.Column("post_id", sa.Text(), nullable=False),
        sa.Column("step_run_id", sa.Text(), nullable=False),
        sa.Column("group_id_hash", sa.Text(), nullable=False),
        sa.Column("content_masked", sa.Text(), nullable=False),
        sa.Column("posted_at", sa.Text(), nullable=True),
        sa.Column("reaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_excluded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("exclude_reason", sa.Text(), nullable=True),
        sa.Column("crawled_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.ForeignKeyConstraint(["step_run_id"], ["step_runs.step_run_id"]),
        sa.PrimaryKeyConstraint("post_id"),
    )
    op.create_table(
        "theme_results",
        sa.Column("theme_id", sa.Text(), nullable=False),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("dominant_sentiment", sa.Text(), nullable=False),
        sa.Column("post_count", sa.Integer(), nullable=False),
        sa.Column("sample_quotes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.CheckConstraint(
            "label IN ('pain_point','positive_feedback','question','comparison','other')",
            name="ck_theme_results_label",
        ),
        sa.CheckConstraint(
            "dominant_sentiment IN ('positive','negative','neutral')",
            name="ck_theme_results_dominant_sentiment",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["plan_runs.run_id"]),
        sa.PrimaryKeyConstraint("theme_id"),
    )
    op.create_table(
        "account_health_log",
        sa.Column("log_id", sa.Text(), nullable=False),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("status_before", sa.Text(), nullable=False),
        sa.Column("status_after", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("cooldown_until", sa.Text(), nullable=True),
        sa.Column("raw_signal", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "signal_type IN ('CAPTCHA','ACTION_BLOCKED','RATE_LIMIT','REDUCED_REACH','SESSION_EXPIRED','MANUAL_RESET')",
            name="ck_account_health_log_signal_type",
        ),
        sa.PrimaryKeyConstraint("log_id"),
    )
    op.create_table(
        "account_health_state",
        sa.Column("id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.Text(), nullable=False, server_default="HEALTHY"),
        sa.Column("session_status", sa.Text(), nullable=False, server_default="NOT_SETUP"),
        sa.Column("account_id_hash", sa.Text(), nullable=True),
        sa.Column("last_checked", sa.Text(), nullable=True),
        sa.Column("cooldown_until", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.Text(), nullable=False, server_default="CURRENT_TIMESTAMP"),
        sa.CheckConstraint("id = 1", name="ck_account_health_state_singleton"),
        sa.CheckConstraint(
            "status IN ('HEALTHY','CAUTION','BLOCKED')",
            name="ck_account_health_state_status",
        ),
        sa.CheckConstraint(
            "session_status IN ('NOT_SETUP','VALID','EXPIRED')",
            name="ck_account_health_state_session_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("account_health_state")
    op.drop_table("account_health_log")
    op.drop_table("theme_results")
    op.drop_table("crawled_posts")
    op.drop_table("step_runs")
    op.drop_table("plan_runs")
    op.drop_table("approval_grants")
    op.drop_table("plan_steps")
    op.drop_table("plans")
    op.drop_table("product_contexts")

