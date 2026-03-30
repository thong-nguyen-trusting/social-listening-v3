# CP1 — Group Relevance Scoring

**Code:** cp1-group-relevance
**Order:** 1
**Depends On:** cp0-phase3-setup
**Estimated Effort:** 1 ngày

## Mục tiêu

Implement `score_group_relevance()` trong PipelineIntelligence. Tích hợp vào runner: sau SEARCH_POSTS, score discovered groups và filter groups không liên quan khỏi JOIN_GROUP + SEARCH_IN_GROUP. (US-30)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/services/pipeline_intelligence.py` | modified | Thêm `score_group_relevance()`, `score_groups()`, dataclasses `GroupRelevanceResult`, `GroupScoringReport` |
| `backend/app/services/runner.py` | modified | Inject PipelineIntelligence, thêm interceptor sau SEARCH_POSTS (score groups), filter trong JOIN_GROUP và SEARCH_IN_GROUP |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `score_group_relevance()` trả đúng kiểu `GroupRelevanceResult` | ✓ |
| CHECK-02 | Group "Ăn Vặt BMT" scored < 0.15 cho topic "sản phẩm làm đẹp thiên nhiên" | ✓ |
| CHECK-03 | Group "REVIEW MỸ PHẨM SKINCARE" scored >= 0.15 cho cùng topic | ✓ |
| CHECK-04 | SEARCH_POSTS checkpoint chứa `group_scoring` object | ✓ |
| CHECK-05 | JOIN_GROUP skips groups với `relevant=false` và ghi `skipped_groups` trong checkpoint | ✓ |
| CHECK-06 | Mock mode e2e: tạo session + plan + run, verify group filtering hoạt động | ✓ |
