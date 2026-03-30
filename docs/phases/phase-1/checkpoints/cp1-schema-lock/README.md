# CP1 — Schema Lock + DB Migration

**Code:** cp1-schema-lock
**Order:** 1
**Depends On:** cp0-environment
**Estimated Effort:** 1 ngay

## Muc tieu

Tao Alembic migration cho toan bo 9 tables da dinh nghia trong architecture.md. Sau CP nay, `alembic upgrade head` tao duoc toan bo schema va SQLAlchemy models map dung voi DB.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/models/base.py | created | SQLAlchemy declarative base |
| backend/app/models/product_context.py | created | ProductContext model |
| backend/app/models/plan.py | created | Plan + PlanStep models |
| backend/app/models/approval.py | created | ApprovalGrant model |
| backend/app/models/run.py | created | PlanRun + StepRun models |
| backend/app/models/crawled_post.py | created | CrawledPost model |
| backend/app/models/theme_result.py | created | ThemeResult model (voi dominant_sentiment) |
| backend/app/models/health.py | created | AccountHealthState + AccountHealthLog models |
| backend/alembic/versions/001_initial_schema.py | created | Migration file cho 9 tables |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `alembic upgrade head` chay thanh cong, khong loi | yes |
| CHECK-02 | SQLite DB chua du 9 tables: product_contexts, plans, plan_steps, approval_grants, plan_runs, step_runs, crawled_posts, theme_results, account_health_state, account_health_log | yes |
| CHECK-03 | theme_results co column `dominant_sentiment` voi CHECK constraint (positive, negative, neutral) | yes |
| CHECK-04 | account_health_state co columns `session_status` va `account_id_hash` | yes |
| CHECK-05 | plan_steps.action_type CHECK constraint chua 5 values: CRAWL_FEED, JOIN_GROUP, CRAWL_COMMENTS, CRAWL_GROUP_META, SEARCH_GROUPS | yes |
| CHECK-06 | `alembic downgrade base` roi `alembic upgrade head` chay lai sach | yes |
| CHECK-07 | SQLAlchemy models import duoc va map dung voi tables | yes |
