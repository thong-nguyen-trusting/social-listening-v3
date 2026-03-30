# CP2 — Shared Shell + UI Primitives

**Code:** cp2-shared-shell-primitives
**Order:** 2
**Depends On:** cp1-mantine-theme-foundation
**Estimated Effort:** 1 ngay

## Muc tieu

Tao shell va primitive dung chung cho product app: compact `AppHeader`, `AppLayout`, va cac UI building blocks de page migration ve sau chi can doi JSX, khong can tao one-off styles moi.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/src/app/shell/AppHeader.tsx` | created | Header 60px voi app name, API links, theme toggle |
| `frontend/src/app/shell/AppLayout.tsx` | created | `AppShell` + `Container` wrapper cho app |
| `frontend/src/components/ui/PageSection.tsx` | created | Wrapper thay the `workflow-card`, `setup-card`, `health-panel`, `card` |
| `frontend/src/components/ui/PageHeader.tsx` | created | Primitive cho eyebrow + title + optional description |
| `frontend/src/components/ui/StatusBadge.tsx` | created | Badge dung central status map va safe normalization |
| `frontend/src/components/ui/ActionBar.tsx` | created | Wrapper cho button groups |
| `frontend/src/components/ui/KeyValueRow.tsx` | created | Primitive hien thi label:value va optional monospace |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `AppLayout.tsx` dung `AppShell` va `Container` theo shell architecture | ✓ |
| CHECK-02 | `AppHeader.tsx` co app identity, API links, va dark mode toggle | ✓ |
| CHECK-03 | `PageSection`, `PageHeader`, `ActionBar`, `KeyValueRow` dung Mantine bases nhu architecture da khoa | ✓ |
| CHECK-04 | `StatusBadge.tsx` dung `getStatusColor()` va normalize status an toan | ✓ |
| CHECK-05 | `cd frontend && npm run build` thanh cong sau khi them shell/primitives | ✓ |
