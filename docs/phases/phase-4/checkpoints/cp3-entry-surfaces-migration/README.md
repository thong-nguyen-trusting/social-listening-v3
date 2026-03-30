# CP3 — Entry Surfaces Migration

**Code:** cp3-entry-surfaces-migration
**Order:** 3
**Depends On:** cp2-shared-shell-primitives
**Estimated Effort:** 1 ngay

## Muc tieu

Migrate cac entry surfaces sang shell/primitives moi ma khong doi business logic: bo hero va checkpoint cards khoi `App.tsx`, chuan hoa `HealthBadge`, va dua `SetupPage` ve status-driven product panel.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/src/App.tsx` | modified | Remove hero/checkpoint cards, wrap content bang `AppLayout` + `SimpleGrid` |
| `frontend/src/components/HealthBadge.tsx` | modified | Dung `PageSection`, `StatusBadge`, `KeyValueRow` thay local CSS/status classes |
| `frontend/src/pages/SetupPage.tsx` | modified | Dung `PageHeader`, `StatusBadge`, Mantine `Button`, `Code`, `Text` |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `App.tsx` khong con hero section va checkpoint cards; dung `AppLayout` + `SimpleGrid` | ✓ |
| CHECK-02 | `HealthBadge.tsx` khong con local color map/class badge; dung `StatusBadge` | ✓ |
| CHECK-03 | `SetupPage.tsx` render `session_status` va `health_status` bang `StatusBadge` | ✓ |
| CHECK-04 | `SetupPage.tsx` dung Mantine components thay button/code/plain paragraph cu | ✓ |
| CHECK-05 | `cd frontend && npm run build` thanh cong sau migration entry surfaces | ✓ |
