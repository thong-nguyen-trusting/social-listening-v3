# CP3 — Priority-Based Comment Crawling

**Code:** cp3-priority-crawl
**Order:** 3
**Depends On:** cp2-early-heuristic
**Estimated Effort:** 1 ngày

## Mục tiêu

Modify CRAWL_COMMENTS handler để crawl posts theo thứ tự priority: high-relevance trước, low-relevance sau. Allocate comment budget theo tier (60/30/10). (US-32)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/services/pipeline_intelligence.py` | modified | Thêm `prioritize_post_refs()`, dataclass `PrioritizedPostPlan` |
| `backend/app/services/runner.py` | modified | CRAWL_COMMENTS handler dùng priority order + per-post budget |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `prioritize_post_refs()` trả `PrioritizedPostPlan` với `ordered_refs` sorted high→medium→low | ✓ |
| CHECK-02 | Budget allocation: 60% cho high, 30% cho medium, 10% cho low (configurable) | ✓ |
| CHECK-03 | Khi tất cả posts là `low` relevance, CRAWL_COMMENTS vẫn chạy (không crash) + có warning | ✓ |
| CHECK-04 | Khi heuristic labeling failed (no labels), fallback về thứ tự gốc | ✓ |
| CHECK-05 | CRAWL_COMMENTS checkpoint chứa `tier_counts` và `tier_budgets` | |
| CHECK-06 | Mock e2e: high-relevance posts crawled trước, verify bằng step_run checkpoint | ✓ |
