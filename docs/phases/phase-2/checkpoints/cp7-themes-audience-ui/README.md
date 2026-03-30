# CP7 — Themes Audience UI

**Code:** cp7-themes-audience-ui
**Order:** 7
**Depends On:** cp5-filtered-theme-api, cp6-monitor-labeling-ui
**Estimated Effort:** 1.5 ngay

## Muc tieu

Them control audience filter tren Themes va summary `excluded by label`. Sau CP nay, user co the chuyen giua `End-user only`, `Include seller`, `Include brand` ma khong can crawl lai.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| frontend/src/pages/ThemesPage.tsx | modified | Filter presets + excluded summary |
| frontend/src/lib/api.ts | modified | Theme API voi `audience_filter` |
| frontend/src/styles.css | modified | Styles cho filter chips va excluded cards |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Themes UI co 3 preset filter | ✓ |
| CHECK-02 | Chuyen filter se refetch themes | ✓ |
| CHECK-03 | Hien `excluded by label` va breakdown | ✓ |
| CHECK-04 | CTA disable khi request dang chay | ✓ |
| CHECK-05 | Default filter la `End-user only` | ✓ |
