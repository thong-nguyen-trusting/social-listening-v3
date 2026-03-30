# CP4 Validation Checklist — Workflow Pages Migration A

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp4-workflow-pages-migration-a/result.json`
**Muc tieu:** Verify ba workflow pages dau da chuan hoa JSX theo shell/primitives ma khong lech logic.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp4-workflow-pages-migration-a/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP4 — Workflow Pages Migration A",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: KeywordPage da doi sang Mantine inputs va PageSection

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/KeywordPage.tsx').read_text()
assert 'PageSection' in text and 'PageHeader' in text
assert 'TextInput' in text and 'Textarea' in text
assert 'className="text-input"' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Con class-based input/card cu

---

### CHECK-02: PlanPage dung StatusBadge va Paper cho steps

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/PlanPage.tsx').read_text()
assert 'StatusBadge' in text and 'Paper' in text
assert 'plan-step' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Step rendering van phu thuoc CSS classes cu

---

### CHECK-03: ApprovePage dung Checkbox va ActionBar

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('frontend/src/pages/ApprovePage.tsx').read_text()
assert 'Checkbox' in text and 'ActionBar' in text and 'Paper' in text
assert 'approve-item' not in text
print('OK')
PY
```

**Expected:** `OK`
**Fail if:** Van dung label/input CSS pattern cu

---

### CHECK-04: Build qua sau workflow migration A

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
    --cp cp4-workflow-pages-migration-a \
    --role validator \
    --status PASS \
    --summary "Workflow pages migration A verified" \
    --result-file docs/phases/phase-4/checkpoints/cp4-workflow-pages-migration-a/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp4-workflow-pages-migration-a/validation.json
```
