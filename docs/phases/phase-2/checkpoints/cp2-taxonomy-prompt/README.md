# CP2 — Taxonomy + Prompt Contract

**Code:** cp2-taxonomy-prompt
**Order:** 2
**Depends On:** cp0-phase2-setup
**Estimated Effort:** 1 ngay

## Muc tieu

Chot taxonomy va prompt contract cho AI labeling, bao gom JSON schema output, heuristic signals, va fallback rules. Sau CP nay, backend co mot contract ro rang de bat dau implement labeling engine.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/skills/content_labeling.md | created | Prompt chinh cho labeling |
| backend/app/domain/label_taxonomy.py | created | Constants cho taxonomy va presets |
| backend/app/services/labeling_heuristics.py | created | Heuristic signals va score helper |
| docs/phases/phase-2/architecture.md | modified | Taxonomy version lock |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | Prompt file ton tai va bat model tra JSON-only | ✓ |
| CHECK-02 | Taxonomy constants khop docs phase-2 | ✓ |
| CHECK-03 | Heuristic signals co seller/end-user/official markers | ✓ |
| CHECK-04 | Fallback rules duoc document hoa ro rang | ✓ |
| CHECK-05 | Prompt sample parse duoc thanh JSON schema mong muon | ✓ |
