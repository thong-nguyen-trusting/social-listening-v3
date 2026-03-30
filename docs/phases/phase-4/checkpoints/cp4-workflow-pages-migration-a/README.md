# CP4 — Workflow Pages Migration A

**Code:** cp4-workflow-pages-migration-a
**Order:** 4
**Depends On:** cp3-entry-surfaces-migration
**Estimated Effort:** 1 ngay

## Muc tieu

Migrate nhom workflow pages trung binh do phuc tap (`KeywordPage`, `PlanPage`, `ApprovePage`) sang Mantine primitives, giu nguyen state/effect/handler logic va xoa phu thuoc vao class-based styling.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/src/pages/KeywordPage.tsx` | modified | Dung `PageSection`, `PageHeader`, `TextInput`, `Textarea`, `ActionBar`, `Alert`, `Paper` |
| `frontend/src/pages/PlanPage.tsx` | modified | Dung `PageSection`, `StatusBadge`, `Paper`, `Alert` cho step rendering |
| `frontend/src/pages/ApprovePage.tsx` | modified | Dung `Checkbox`, `Paper`, `ActionBar`, `Alert` cho approval review |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `KeywordPage.tsx` khong con `text-input` / `button-row` / `workflow-card`; dung Mantine inputs va `PageSection` | ✓ |
| CHECK-02 | `PlanPage.tsx` dung `StatusBadge` cho READ/WRITE va `Paper` cho step cards | ✓ |
| CHECK-03 | `ApprovePage.tsx` dung `Checkbox` va `Paper` thay label/input CSS pattern cu | ✓ |
| CHECK-04 | Ca 3 pages van giu nguyen fetch/event handler logic va prop contracts | ✓ |
| CHECK-05 | `cd frontend && npm run build` thanh cong sau workflow migration A | ✓ |
