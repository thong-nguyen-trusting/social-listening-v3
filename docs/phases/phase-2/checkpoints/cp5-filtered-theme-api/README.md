# CP5 — Filtered Theme API

**Code:** cp5-filtered-theme-api
**Order:** 5
**Depends On:** cp4-content-labeling-engine
**Estimated Effort:** 1.5 ngay

## Muc tieu

Cap nhat `InsightService` va API de theme analysis doc labels hien tai va ap dung `audience_filter` o read-time. Sau CP nay, backend tra ve `excluded_by_label_count` va breakdown theo policy.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/audience_filter.py | created | Policy engine cho `end_user_only`, `include_seller`, `include_brand` |
| backend/app/services/insight.py | modified | Dung labels thay cho regex exclude thuan |
| backend/app/api/insights.py | modified | Ho tro query param `audience_filter` |
| backend/app/schemas/insights.py | modified | Them fields `audience_filter`, `posts_included`, `excluded_breakdown`, `taxonomy_version` |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `GET /themes?audience_filter=end_user_only` tra payload hop le | ✓ |
| CHECK-02 | `Include seller` thay doi included/excluded counts | ✓ |
| CHECK-03 | Response co `excluded_by_label_count` va breakdown | ✓ |
| CHECK-04 | Theme filtering xay ra o read-time, khong mutate vinh vien record | ✓ |
| CHECK-05 | Taxonomy version va audience filter duoc echo trong response | ✓ |
