# CP4 — Group Quality Gate

**Code:** cp4-quality-gate
**Order:** 4
**Depends On:** cp1-group-relevance, cp2-early-heuristic
**Estimated Effort:** 0.5 ngày

## Mục tiêu

Implement `quality_gate_groups()`: filter SEARCH_IN_GROUP to only search groups where SEARCH_POSTS found relevant posts. Skip groups where >70% posts are seller/irrelevant. (US-34)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/services/pipeline_intelligence.py` | modified | Thêm `quality_gate_groups()`, dataclasses `GroupQualityReport`, `GroupQualityDetail` |
| `backend/app/services/runner.py` | modified | SEARCH_IN_GROUP handler dùng quality gate trước khi iterate groups |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `quality_gate_groups()` trả `GroupQualityReport` | ✓ |
| CHECK-02 | Group với 100% seller posts bị skip (quality_ratio < 0.3) | ✓ |
| CHECK-03 | Group với 1 post medium relevance được pass (benefit of doubt) | ✓ |
| CHECK-04 | Khi tất cả groups fail gate, SEARCH_IN_GROUP completes với actual_count=0 | ✓ |
| CHECK-05 | SEARCH_IN_GROUP checkpoint chứa `group_quality` report | |
