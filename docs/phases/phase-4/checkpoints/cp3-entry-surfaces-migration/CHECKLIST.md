# CP3 Validation Checklist — Entry Surfaces Migration

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp3-entry-surfaces-migration/result.json`
**Muc tieu:** Verify app root va entry surfaces da bo landing-page pattern va dung shell/primitives moi.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp3-entry-surfaces-migration/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP3 — Entry Surfaces Migration",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: App.tsx bo hero va checkpoint cards

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/App.tsx').read_text()
assert 'className="hero"' not in text
assert 'const checkpoints' not in text
assert 'AppLayout' in text and 'SimpleGrid' in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Hero/checkpoint placeholders van con hoac chua dung shell

---

### CHECK-02: HealthBadge dung StatusBadge

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/components/HealthBadge.tsx').read_text()
assert 'StatusBadge' in text
assert 'const colors' not in text
assert 'health-panel' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Con local status mapping/CSS classes cu

---

### CHECK-03: SetupPage dung StatusBadge cho session va health

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/SetupPage.tsx').read_text()
assert text.count('StatusBadge') >= 2
assert 'session_status' in text and 'health_status' in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Status van render plain text

---

### CHECK-04: Build qua sau entry migration

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
    --cp cp3-entry-surfaces-migration \
    --role validator \
    --status PASS \
    --summary "Entry surfaces migrated to shell/primitives successfully" \
    --result-file docs/phases/phase-4/checkpoints/cp3-entry-surfaces-migration/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp3-entry-surfaces-migration/validation.json
```
