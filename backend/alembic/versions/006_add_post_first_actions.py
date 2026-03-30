"""add post-first actions to plan step constraint

Revision ID: 006_add_post_first_actions
Revises: 005_add_check_join_status_action
Create Date: 2026-03-29 03:00:00
"""

from alembic import op


revision = "006_add_post_first_actions"
down_revision = "005_add_check_join_status_action"
branch_labels = None
depends_on = None


NEW_ACTION_CONSTRAINT = (
    "action_type IN ("
    "'SEARCH_GROUPS','CRAWL_FEED','JOIN_GROUP','CHECK_JOIN_STATUS',"
    "'SEARCH_POSTS','CRAWL_COMMENTS','SEARCH_IN_GROUP'"
    ")"
)
OLD_ACTION_CONSTRAINT = "action_type IN ('SEARCH_GROUPS','CRAWL_FEED','JOIN_GROUP','CHECK_JOIN_STATUS')"


def upgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", NEW_ACTION_CONSTRAINT)


def downgrade() -> None:
    with op.batch_alter_table("plan_steps", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_plan_steps_action_type", type_="check")
        batch_op.create_check_constraint("ck_plan_steps_action_type", OLD_ACTION_CONSTRAINT)
