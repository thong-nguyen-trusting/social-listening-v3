# CP8 — Audit, Backfill & Smoke

**Code:** cp8-audit-backfill-smoke
**Order:** 8
**Depends On:** cp7-themes-audience-ui
**Estimated Effort:** 1 ngay

## Muc tieu

Chot Phase 2 bang audit/sample records, backfill cho run cu, va smoke test end-to-end. Sau CP nay, project Phase 2 co the demo tren dashboard va tren app voi flow labeling + filters hoan chinh.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/tests/labeling_smoke.py | created | Smoke test cho labeling pipeline |
| docs/phases/phase-2/checkpoints/cp8-audit-backfill-smoke/DEMO_LOG.md | created | Log ket qua demo Phase 2 |
| backend/app/api/labels.py | modified | Optional sample/audit endpoint neu duoc chon |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Chay duoc flow crawl run co labels va themes filter | ✓ |
| CHECK-02 | Backfill toi thieu 1 run cu thanh cong | ✓ |
| CHECK-03 | Audit sample excluded record hien thi du labels/reason | ✓ |
| CHECK-04 | Khong co crash/unhandled exception | ✓ |
| CHECK-05 | DEMO_LOG ghi lai ket qua ro rang | ✓ |
