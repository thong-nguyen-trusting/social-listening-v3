"""align plan step action constraint with action registry

Revision ID: 004_align_plan_step_actions_with_registry
Revises: 003_add_run_alias_columns
Create Date: 2026-03-29 01:30:00
"""

from alembic import op


revision = "004_align_plan_step_actions_with_registry"
down_revision = "003_add_run_alias_columns"
branch_labels = None
depends_on = None


NEW_ACTION_CONSTRAINT = "action_type IN ('SEARCH_GROUPS','CRAWL_FEED','JOIN_GROUP')"
OLD_ACTION_CONSTRAINT = (
    "action_type IN ('CRAWL_FEED','JOIN_GROUP','CRAWL_COMMENTS','CRAWL_GROUP_META','SEARCH_GROUPS')"
)


def upgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", NEW_ACTION_CONSTRAINT)


def downgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", OLD_ACTION_CONSTRAINT)
