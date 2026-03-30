# CP3 — Label Job Orchestration

**Code:** cp3-label-job-orchestration
**Order:** 3
**Depends On:** cp1-labeling-schema, cp2-taxonomy-prompt
**Estimated Effort:** 1 ngay

## Muc tieu

Implement lifecycle rieng cho labeling jobs: create, start, progress, retry-safe, va summary read model. Sau CP nay, system co the tao `label_job` cho 1 run ma khong pha vo `plan_runs`.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/label_job_service.py | created | Service tao va quan ly label jobs |
| backend/app/api/labels.py | created | API trigger/status co ban cho labeling |
| backend/app/schemas/labels.py | created | Pydantic schemas cho label job summary |
| backend/app/main.py | modified | Register labels router |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Co the tao `label_job` cho `run_id` hop le | ✓ |
| CHECK-02 | `label_job` lifecycle di qua `PENDING -> RUNNING -> DONE/PARTIAL/FAILED` | ✓ |
| CHECK-03 | Summary API tra duoc progress counts | ✓ |
| CHECK-04 | Tao lai label job cho cung run + taxonomy version bi chan hop ly | ✓ |
| CHECK-05 | Labeling khong mutate crawl run status | ✓ |
