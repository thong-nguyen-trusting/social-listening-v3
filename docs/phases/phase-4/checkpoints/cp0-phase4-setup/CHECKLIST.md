# CP0 Validation Checklist — Phase 4 Setup

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp0-phase4-setup/result.json`
**Muc tieu:** Verify checkpoint workspace va phase metadata da san sang cho dashboard monitor.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp0-phase4-setup/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP0 — Phase 4 Setup",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Workspace files hien dien

```bash
test -f docs/phases/phase-4/checkpoints/README.md \
  && test -f docs/phases/phase-4/checkpoints/config.json \
  && test -f docs/phases/phase-4/checkpoints/config.example.json \
  && test -f docs/phases/phase-4/checkpoints/notify.py \
  && test -f docs/phases/phase-4/checkpoints/post-status.py \
  && echo OK
```

**Expected:** `OK`
**Fail if:** Bat ky file nao bi thieu

---

### CHECK-02: Du 7 checkpoint folders

```bash
find docs/phases/phase-4/checkpoints -maxdepth 1 -type d -name 'cp*' | wc -l | tr -d ' '
```

**Expected:** `7`
**Fail if:** Khac `7`

---

### CHECK-03: project_slug dung cho Phase 4

```bash
python3 - <<'PY'
import json
from pathlib import Path
config = json.loads(Path('docs/phases/phase-4/checkpoints/config.json').read_text())
assert config["project_slug"] == "ai-facebook-social-listening-engagement-v3-phase-4"
print("OK")
PY
```

**Expected:** `OK`
**Fail if:** `project_slug` sai hoac file JSON invalid

---

### CHECK-04: .phase.json da chuyen sang phase-4

```bash
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('.phase.json').read_text())
assert data["current"] == "phase-4"
assert data["phases"]["phase-4"]["status"] == "active"
assert data["phases"]["phase-4"]["checkpoints"] == 7
print("OK")
PY
```

**Expected:** `OK`
**Fail if:** current/status/checkpoint count sai

---

### CHECK-05: Bang checkpoint bao phu dung 7 CP

```bash
rg -n "cp0-phase4-setup|cp1-mantine-theme-foundation|cp2-shared-shell-primitives|cp3-entry-surfaces-migration|cp4-workflow-pages-migration-a|cp5-workflow-pages-migration-b|cp6-css-cleanup-build-gate" docs/phases/phase-4/checkpoints/README.md
```

**Expected:** Co du 7 entries
**Fail if:** Thieu CP code nao

---

## Ghi ket qua

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** (none)

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp0-phase4-setup \
    --role validator \
    --status PASS \
    --summary "Phase 4 checkpoint workspace va phase metadata verified" \
    --result-file docs/phases/phase-4/checkpoints/cp0-phase4-setup/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp0-phase4-setup/validation.json
```
