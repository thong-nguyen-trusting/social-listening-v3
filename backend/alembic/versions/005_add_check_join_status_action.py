"""add check join status action to plan step constraint

Revision ID: 005_add_check_join_status_action
Revises: 004_align_plan_step_actions_with_registry
Create Date: 2026-03-29 02:05:00
"""

from alembic import op


revision = "005_add_check_join_status_action"
down_revision = "004_align_plan_step_actions_with_registry"
branch_labels = None
depends_on = None


NEW_ACTION_CONSTRAINT = "action_type IN ('SEARCH_GROUPS','CRAWL_FEED','JOIN_GROUP','CHECK_JOIN_STATUS')"
OLD_ACTION_CONSTRAINT = "action_type IN ('SEARCH_GROUPS','CRAWL_FEED','JOIN_GROUP')"


def upgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", NEW_ACTION_CONSTRAINT)


def downgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", OLD_ACTION_CONSTRAINT)
