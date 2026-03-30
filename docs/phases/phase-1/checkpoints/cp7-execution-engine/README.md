# CP7 — Execution Engine

**Code:** cp7-execution-engine
**Order:** 7
**Depends On:** cp6-review-approve, cp2-browser-session
**Estimated Effort:** 3 ngay

## Muc tieu

Implement US-03b: RunnerService chay approved plan steps theo thu tu, voi pause/resume/stop, checkpoint persist, SSE real-time updates, va BrowserAgent.crawl_feed() thuc su crawl Facebook group. Day la CP co risk cao nhat (tuong tac voi Facebook that).

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/runner.py | created | RunnerService: execute_run(), pause, resume, stop, checkpoint |
| backend/app/api/runs.py | created | POST /api/runs, GET /api/runs/{id}, pause/resume/stop, SSE stream |
| backend/app/schemas/runs.py | created | Pydantic schemas cho run API |
| backend/app/infra/browser_agent.py | modified | Implement crawl_feed() voi rate limiting, checkpoint, PII masking |
| backend/app/infra/pii_masker.py | created | PII masking: phone, email, CMND patterns |
| frontend/src/pages/MonitorPage.tsx | created | Real-time execution monitor voi SSE |
| backend/app/main.py | modified | Register runs router |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | POST /api/runs tao PlanRun + StepRuns, status=RUNNING | yes |
| CHECK-02 | Steps execute theo order, StepRun status chuyen PENDING → RUNNING → DONE | yes |
| CHECK-03 | POST /api/runs/{id}/pause → run paused, current step finishes truoc | yes |
| CHECK-04 | POST /api/runs/{id}/resume → tiep tuc tu step chua xong | yes |
| CHECK-05 | BrowserAgent.crawl_feed() crawl duoc posts tu 1 real Facebook group (voi real account) | yes |
| CHECK-06 | Crawled posts luu trong DB voi PII masked (phone/email patterns replaced) | yes |
| CHECK-07 | SSE stream /api/runs/{id}/stream gui events: step_started, step_done, run_done | yes |
| CHECK-08 | StepRun.checkpoint duoc luu — neu restart, co the resume | no |
| CHECK-09 | MonitorPage hien thi step statuses realtime | no |
