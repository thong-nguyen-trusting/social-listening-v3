# CP2 — Early Heuristic Labeling

**Code:** cp2-early-heuristic
**Order:** 2
**Depends On:** cp0-phase3-setup
**Estimated Effort:** 1 ngày

## Mục tiêu

Chạy `labeling_heuristics.classify_content()` ngay sau SEARCH_POSTS persist — trước khi CRAWL_COMMENTS bắt đầu. Gán `user_feedback_relevance` sớm để downstream steps biết post nào seller, post nào end-user. (US-31)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `backend/app/services/pipeline_intelligence.py` | modified | Thêm `heuristic_label_posts()` method |
| `backend/app/services/runner.py` | modified | Thêm interceptor sau SEARCH_POSTS: gọi heuristic labeling, cập nhật label_status → HEURISTIC_LABELED |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | `heuristic_label_posts()` trả list of `HeuristicLabelResult` | ✓ |
| CHECK-02 | Post có "ib mình nhé, ship nha" được label `seller_affiliate` + `relevance=low` | ✓ |
| CHECK-03 | Post có "mình dùng thấy da mịn hơn" được label `end_user` + `relevance=high` | ✓ |
| CHECK-04 | Sau SEARCH_POSTS, posts trong DB có `label_status=HEURISTIC_LABELED` | ✓ |
| CHECK-05 | Nếu heuristic fails, posts giữ `label_status=PENDING` — graceful degradation | ✓ |
| CHECK-06 | SEARCH_POSTS checkpoint chứa `label_summary` object (high/medium/low counts) | |
