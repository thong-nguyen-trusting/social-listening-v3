# CP5 — Pipeline Summary API

**Code:** cp5-pipeline-summary
**Order:** 5
**Depends On:** cp1-group-relevance, cp2-early-heuristic, cp3-priority-crawl, cp4-quality-gate
**Estimated Effort:** 0.5 ngày

## Mục tiêu

Aggregate pipeline intelligence data from step checkpoints into a `pipeline_summary` object on the run response. (US-33 backend)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/services/pipeline_intelligence.py` | modified | Thêm `build_pipeline_summary()` |
| `backend/app/services/runner.py` | modified | `get_run()` enriches response with `pipeline_summary` |
| `backend/app/schemas/runs.py` | modified | Add `pipeline_summary: dict | None` to RunResponse (if schema exists) |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `build_pipeline_summary()` trả dict với keys: search_posts, heuristic_labeling, group_scoring, comment_crawl, group_quality_gate | ✓ |
| CHECK-02 | `GET /api/runs/{run_id}` response chứa `pipeline_summary` key | ✓ |
| CHECK-03 | Pipeline summary có đúng counts khi chạy mock e2e | ✓ |
| CHECK-04 | Pipeline summary là `null` khi `pipeline_intelligence_enabled=false` | |
