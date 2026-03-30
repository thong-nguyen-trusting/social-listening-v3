# CP7 — E2E Smoke Test

**Code:** cp7-smoke-test
**Order:** 7
**Depends On:** cp6-pipeline-dashboard
**Estimated Effort:** 0.5 ngày

## Mục tiêu

Chạy full e2e test (mock + real browser) để verify toàn bộ Phase 3 pipeline: group scoring, heuristic labeling, priority crawl, quality gate, pipeline dashboard. Target: % relevant posts trong CRAWL_COMMENTS tăng từ ~44% lên >70%.

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `docs/phases/phase-3/checkpoints/cp7-smoke-test/DEMO_LOG.md` | created | Log kết quả test với metrics trước/sau |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | Mock mode e2e: session → plan → approve → run completes DONE | ✓ |
| CHECK-02 | pipeline_summary present trong run response với non-zero counts | ✓ |
| CHECK-03 | group_scoring skips ít nhất 1 irrelevant group trong mock run | ✓ |
| CHECK-04 | CRAWL_COMMENTS checkpoint shows tier_counts với high > 0 | ✓ |
| CHECK-05 | Pipeline dashboard hiển thị funnel trên UI (visual check) | ✓ |
| CHECK-06 | Feature flag disabled: pipeline_intelligence_enabled=false → run hoạt động giống pre-Phase 3 | |
| CHECK-07 | Real browser run (nếu có session): topic "VIB Max Card" hoặc tương tự, verify group filtering works | |
