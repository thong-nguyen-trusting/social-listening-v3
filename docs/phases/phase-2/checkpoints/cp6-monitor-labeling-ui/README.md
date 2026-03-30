# CP6 — Monitor Labeling UI

**Code:** cp6-monitor-labeling-ui
**Order:** 6
**Depends On:** cp3-label-job-orchestration
**Estimated Effort:** 1 ngay

## Muc tieu

Bo sung monitor section cho labeling progress: status, counts, fallback, failed, taxonomy version. Sau CP nay, user biet crawl da xong chua va labeling dang o trang thai nao.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| frontend/src/pages/MonitorPage.tsx | modified | Hien thi label job progress section |
| frontend/src/lib/api.ts | modified | Them fetch helpers cho label summary |
| backend/app/api/labels.py | modified | Dam bao summary API phuc vu UI |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Monitor co section rieng cho labeling | ✓ |
| CHECK-02 | UI hien `records_total/labeled/fallback/failed` | ✓ |
| CHECK-03 | Labeling progress khong lam roi crawl step stream | ✓ |
| CHECK-04 | Loading/error state ro rang | ✓ |
| CHECK-05 | Khi labeling dang chay, UI canh bao themes co the thay doi | ✓ |
