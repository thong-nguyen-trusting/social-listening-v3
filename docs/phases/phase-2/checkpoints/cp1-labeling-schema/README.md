# CP1 — Labeling Schema + Migration

**Code:** cp1-labeling-schema
**Order:** 1
**Depends On:** cp0-phase2-setup
**Estimated Effort:** 1 ngay

## Muc tieu

Them schema Phase 2 cho labeling: `label_jobs`, `content_labels`, va cac summary columns tren `crawled_posts`. Sau CP nay, DB co du contracts de luu labeling lifecycle tach biet voi crawl run.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/models/content_label.py | created | SQLAlchemy model cho content_labels |
| backend/app/models/label_job.py | created | SQLAlchemy model cho label_jobs |
| backend/app/models/crawled_post.py | modified | Them `label_status`, `current_label_id` |
| backend/alembic/versions/008_add_labeling_tables.py | created | Migration cho schema Phase 2 |
| backend/app/models/__init__.py | modified | Export models moi |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `alembic upgrade head` chay thanh cong | ✓ |
| CHECK-02 | SQLite co 2 table moi: `label_jobs`, `content_labels` | ✓ |
| CHECK-03 | `crawled_posts` co `label_status`, `current_label_id` | ✓ |
| CHECK-04 | Constraints cho taxonomy values duoc lock trong DB | ✓ |
| CHECK-05 | `alembic downgrade` roi `upgrade` lai sach | ✓ |
