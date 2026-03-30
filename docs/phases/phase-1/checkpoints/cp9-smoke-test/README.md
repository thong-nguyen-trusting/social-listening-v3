# CP9 — End-to-end Smoke Test

**Code:** cp9-smoke-test
**Order:** 9
**Depends On:** cp8-theme-analysis
**Estimated Effort:** 1 ngay

## Muc tieu

Chay full flow tu dau den cuoi voi real Facebook account: topic → keywords → plan → approve → crawl → themes. Chung minh Phase 1 deliver duoc gia tri thuc te. Khong crash, khong ban account.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/tests/e2e_smoke.py | created | End-to-end smoke test script |
| docs/phases/phase-1/checkpoints/cp9-smoke-test/DEMO_LOG.md | created | Log cua demo session (screenshots optional) |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Full flow chay duoc trong 1 session: topic → keywords → plan → approve → run → themes | yes |
| CHECK-02 | Account health van HEALTHY sau khi chay xong | yes |
| CHECK-03 | Theme results hien thi trong UI voi it nhat 1 theme co sentiment label | yes |
| CHECK-04 | Khong co error khong xu ly duoc (unhandled exception) trong server logs | yes |
| CHECK-05 | PII masking hoat dong — khong co raw phone/email trong DB hoac UI | yes |
| CHECK-06 | Total duration < 10 phut cho 1 group crawl (~20-50 posts) | no |
| CHECK-07 | DEMO_LOG.md ghi lai cac buoc va ket qua | no |
