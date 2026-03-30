# CP1 — Mantine Theme Foundation

**Code:** cp1-mantine-theme-foundation
**Order:** 1
**Depends On:** cp0-phase4-setup
**Estimated Effort:** 1 ngay

## Muc tieu

Dat UI foundation chung cho Phase 4: Mantine la UI library duy nhat, theme va token structure ro rang, status mapping tap trung, va `main.tsx` da wrap app trong `ThemeProvider`.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/package.json` | modified | Them Mantine + notifications + hooks + Inter font package |
| `frontend/package-lock.json` | created | Lockfile sau khi install packages |
| `frontend/src/theme/tokens.ts` | created | Primitive design tokens cho colors, spacing, radius, shadows |
| `frontend/src/theme/status.ts` | created | STATUS_MAP, normalize helper, status-to-color helpers |
| `frontend/src/theme/index.ts` | created | `createTheme()` va Mantine overrides |
| `frontend/src/app/providers/ThemeProvider.tsx` | created | `MantineProvider` + `Notifications` host |
| `frontend/src/main.tsx` | modified | Import Mantine CSS, notifications CSS, Inter font, wrap `<App />` |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `frontend/package.json` co `@mantine/core`, `@mantine/hooks`, `@mantine/notifications`, `@fontsource-variable/inter` | ✓ |
| CHECK-02 | `theme/status.ts` dung uppercase `STATUS_MAP`, normalize status, fallback `neutral` | ✓ |
| CHECK-03 | `theme/index.ts` export `createTheme()` voi typography/spacing/radius overrides | ✓ |
| CHECK-04 | `ThemeProvider.tsx` mount `MantineProvider` va `Notifications` | ✓ |
| CHECK-05 | `main.tsx` import styles va wrap app trong `ThemeProvider` | ✓ |
| CHECK-06 | `cd frontend && npm run build` thanh cong sau foundation wiring | ✓ |
