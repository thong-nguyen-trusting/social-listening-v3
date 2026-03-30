# CP6 — CSS Cleanup + Build Gate

**Code:** cp6-css-cleanup-build-gate
**Order:** 6
**Depends On:** cp5-workflow-pages-migration-b
**Estimated Effort:** 0.5 ngay

## Muc tieu

Dong Phase 4 bang quality gate cuoi: `styles.css` chi con global resets, frontend build xanh, va co smoke notes ngan de xac nhan shell/header/theme toggle/page layout deu hoat dong sau refactor.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `frontend/src/styles.css` | modified | Thu gon con reset styles duy nhat, khong con component class definitions |
| `docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/DEMO_LOG.md` | created | Ghi build output, smoke notes, va timestamp verification |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `frontend/src/styles.css` con duoi 10 dong va chi chua global resets | ✓ |
| CHECK-02 | `cd frontend && npm run build` thanh cong | ✓ |
| CHECK-03 | Smoke notes xac nhan hero/checkpoint cards da bien mat, header + theme toggle hoat dong | ✓ |
| CHECK-04 | Khong con class selectors cu (`.workflow-card`, `.setup-card`, `.health-panel`, `.theme-card`, `.monitor-step`) trong `styles.css` | ✓ |
