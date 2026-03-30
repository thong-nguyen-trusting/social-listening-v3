# CP4 — Content Labeling Engine

**Code:** cp4-content-labeling-engine
**Order:** 4
**Depends On:** cp3-label-job-orchestration
**Estimated Effort:** 2 ngay

## Muc tieu

Implement engine gan nhan cho tung `POST`/`COMMENT` bang hybrid flow `heuristic -> AI -> fallback`. Sau CP nay, system co the label batched records va persist current label cho tung crawled record.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/content_labeling.py | created | Engine xu ly batch labeling |
| backend/app/infra/ai_client.py | modified | Ho tro content labeling prompt call |
| backend/app/services/labeling_heuristics.py | modified | Pre-score va signals |
| backend/app/models/crawled_post.py | modified | Update current label pointers |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Engine label duoc mot batch records va persist vao `content_labels` | ✓ |
| CHECK-02 | `COMMENT` duoc label doc lap voi `POST` cha | ✓ |
| CHECK-03 | AI error -> fallback label van persist | ✓ |
| CHECK-04 | `crawled_posts.current_label_id` duoc cap nhat | ✓ |
| CHECK-05 | Batch call khong goi model 1 request/record | ✓ |
