# CP0 — Phase 4 Setup

**Code:** cp0-phase4-setup
**Order:** 0
**Depends On:** —
**Estimated Effort:** 0.5 ngay

## Muc tieu

Khoi tao workspace checkpoint cho Phase 4 de dashboard monitor co the track implementation frontend refactor nhu mot phase doc lap: scripts notification, config project slug, bang checkpoint tong, va phase metadata.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| `docs/phases/phase-4/checkpoints/README.md` | created | Bang checkpoint va sprint mapping Phase 4 |
| `docs/phases/phase-4/checkpoints/config.example.json` | created | Mau config dashboard/ntfy cho Phase 4 |
| `docs/phases/phase-4/checkpoints/config.json` | created | Config local cho dashboard monitor Phase 4 |
| `docs/phases/phase-4/checkpoints/notify.py` | created | Script notification dung lai tu phase truoc |
| `docs/phases/phase-4/checkpoints/post-status.py` | created | Script post checkpoint status len dashboard |
| `.phase.json` | modified | Them phase-4, checkpoint count = 7, current phase chuyen sang phase-4 |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `docs/phases/phase-4/checkpoints/` ton tai day du README, config, notify.py, post-status.py | ✓ |
| CHECK-02 | Co du 7 CP folders tu `cp0-phase4-setup` den `cp6-css-cleanup-build-gate` | ✓ |
| CHECK-03 | `config.json` tro toi `project_slug=ai-facebook-social-listening-engagement-v3-phase-4` | ✓ |
| CHECK-04 | `.phase.json` co `current=phase-4` va `checkpoints=7` | ✓ |
| CHECK-05 | Phase 4 checkpoint table khop architecture breakdown (setup, foundation, shell, migrations, cleanup) | ✓ |
