# CP0 — Phase 3 Environment Setup

**Code:** cp0-phase3-setup
**Order:** 0
**Depends On:** —
**Estimated Effort:** 0.5 ngày

## Mục tiêu

Chuẩn bị môi trường cho Phase 3: thêm settings mới, tạo migration cho `HEURISTIC_LABELED` status, extract `text_utils.py` shared utility, và tạo skeleton `pipeline_intelligence.py`.

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/infra/text_utils.py` | created | Shared Vietnamese text utils: strip_diacritics, tokenize_vn, token_overlap_score |
| `backend/app/services/pipeline_intelligence.py` | created | Skeleton class PipelineIntelligence với __init__ |
| `backend/app/infrastructure/config.py` | modified | Thêm 6 settings: thresholds, feature flag |
| `backend/app/domain/label_taxonomy.py` | modified | Thêm HEURISTIC_LABELED vào LABEL_RECORD_STATUSES |
| `backend/alembic/versions/007_add_heuristic_labeled_status.py` | created | Migration cho label_status constraint |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `text_utils.py` tồn tại và import được: `from app.infra.text_utils import strip_diacritics, tokenize_vn, token_overlap_score` | ✓ |
| CHECK-02 | `strip_diacritics("mỹ phẩm")` trả về `"my pham"` | ✓ |
| CHECK-03 | `token_overlap_score("mỹ phẩm thiên nhiên", "REVIEW MỸ PHẨM SKINCARE")` > 0.3 | ✓ |
| CHECK-04 | `pipeline_intelligence.py` import được: `from app.services.pipeline_intelligence import PipelineIntelligence` | ✓ |
| CHECK-05 | Settings có `pipeline_intelligence_enabled`, `group_relevance_threshold`, `group_quality_threshold` | ✓ |
| CHECK-06 | `HEURISTIC_LABELED` có trong `LABEL_RECORD_STATUSES` | ✓ |
| CHECK-07 | Migration 007 chạy thành công: `alembic upgrade head` | ✓ |
