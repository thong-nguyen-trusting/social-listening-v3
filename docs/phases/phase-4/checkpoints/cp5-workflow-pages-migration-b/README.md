# CP5 — Workflow Pages Migration B

**Code:** cp5-workflow-pages-migration-b
**Order:** 5
**Depends On:** cp4-workflow-pages-migration-a
**Estimated Effort:** 1 ngay

## Muc tieu

Migrate hai pages phuc tap nhat (`MonitorPage`, `ThemesPage`) sang shell/primitives moi, dac biet gom central status rendering, label chips, segmented filters, event log container, va metadata panels.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/src/pages/MonitorPage.tsx` | modified | Dung `StatusBadge`, `ActionBar`, `KeyValueRow`, `Paper`, `Badge` cho run/step/labeling monitor |
| `frontend/src/pages/ThemesPage.tsx` | modified | Dung `SegmentedControl`, `StatusBadge`, `Badge`, `Paper`, `Stack/List` cho theme insight UI |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `MonitorPage.tsx` dung `StatusBadge` cho `streamStatus`, `run.status`, `step.status`, `labelSummary.status` | ✓ |
| CHECK-02 | `MonitorPage.tsx` dung Mantine containers cho event log, label chips, va metadata rows | ✓ |
| CHECK-03 | `ThemesPage.tsx` dung `SegmentedControl` va `StatusBadge` cho sentiment | ✓ |
| CHECK-04 | `ThemesPage.tsx` khong con `filter-chip`, `theme-card`, `sentiment-*` CSS classes | ✓ |
| CHECK-05 | `cd frontend && npm run build` thanh cong sau workflow migration B | ✓ |
