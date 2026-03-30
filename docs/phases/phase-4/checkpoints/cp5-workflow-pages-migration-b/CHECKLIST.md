# CP5 Validation Checklist — Workflow Pages Migration B

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp5-workflow-pages-migration-b/result.json`
**Muc tieu:** Verify Monitor va Themes pages da migrate dung central status map va Mantine interaction patterns.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp5-workflow-pages-migration-b/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP5 — Workflow Pages Migration B",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: MonitorPage dung StatusBadge cho cac statuses

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/MonitorPage.tsx').read_text()
assert text.count('StatusBadge') >= 4
assert 'monitor-step-' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Con CSS state classes cu hoac thieu status badge

---

### CHECK-02: MonitorPage dung Mantine containers cho chips/log

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/MonitorPage.tsx').read_text()
assert 'Badge' in text and 'Paper' in text
assert 'label-chip' not in text and 'event-log' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Van phu thuoc `label-chip` / `event-log` classes cu

---

### CHECK-03: ThemesPage dung SegmentedControl va StatusBadge

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/ThemesPage.tsx').read_text()
assert 'SegmentedControl' in text and 'StatusBadge' in text
assert 'filter-chip' not in text and 'sentiment-' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Filters/sentiment van dung CSS classes cu

---

### CHECK-04: Build qua sau workflow migration B

```bash
cd frontend && npm run build
```

**Expected:** Build succeeds
**Fail if:** TypeScript/Vite build fail

---

## Ghi ket qua

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04
**Warning checks:** (none)

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp5-workflow-pages-migration-b \
    --role validator \
    --status PASS \
    --summary "Workflow pages migration B verified" \
    --result-file docs/phases/phase-4/checkpoints/cp5-workflow-pages-migration-b/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp5-workflow-pages-migration-b/validation.json
```
