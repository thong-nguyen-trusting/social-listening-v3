# CP6 — Pipeline Dashboard UI

**Code:** cp6-pipeline-dashboard
**Order:** 6
**Depends On:** cp5-pipeline-summary
**Estimated Effort:** 1 ngày

## Mục tiêu

Hiển thị pipeline funnel trên MonitorPage: số posts tìm được → labeling breakdown → groups scored → comments crawled per tier → groups searched. (US-33 frontend)

## Artifacts dự kiến

| File/Path | Action | Mô tả |
|-----------|--------|-------|
| `frontend/src/pages/MonitorPage.tsx` | modified | Thêm pipeline funnel section khi `pipeline_summary` có data |
| `frontend/src/styles.css` | modified | Thêm `.pipeline-funnel`, `.funnel-stage`, `.funnel-bar` classes |

## Checklist Validator

| ID | Mô tả | Blocker |
|----|-------|---------|
| CHECK-01 | MonitorPage hiển thị pipeline funnel khi run có `pipeline_summary` | ✓ |
| CHECK-02 | Funnel hiển thị đúng: search_posts total, labeling breakdown, group scoring, comment tiers | ✓ |
| CHECK-03 | Khi `pipeline_summary` null (Phase 3 disabled), funnel section ẩn | ✓ |
| CHECK-04 | Frontend build thành công: `npm run build` | ✓ |
