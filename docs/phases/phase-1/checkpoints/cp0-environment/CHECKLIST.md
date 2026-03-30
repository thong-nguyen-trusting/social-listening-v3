# CP0 Validation Checklist — Environment Setup

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp0-environment/result.json`
**Muc tieu:** Verify toan bo dev environment chay duoc: backend, frontend, Camoufox, Alembic.

---

## Buoc 0 — Bao bat dau validate (bat buoc, chay truoc tien)

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp0-environment/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP0 — Environment Setup",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Danh sach kiem tra

### CHECK-01: Python version

```bash
python3 --version
```

**Expected:** Python 3.12.x hoac cao hon
**Fail if:** Version < 3.12

---

### CHECK-02: Backend dependencies

```bash
cd backend && source venv/bin/activate && pip freeze | grep -E "fastapi|uvicorn|sqlalchemy|anthropic|camoufox"
```

**Expected:** Tat ca 5 packages co trong output
**Fail if:** Bat ky package nao thieu

---

### CHECK-03: Camoufox binary

```bash
cd backend && source venv/bin/activate && python -c "from camoufox.async_api import AsyncCamoufox; print('OK')"
```

**Expected:** Output "OK" khong loi
**Fail if:** ImportError hoac binary not found

---

### CHECK-04: Backend server

```bash
cd backend && source venv/bin/activate && timeout 5 uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/health
kill %1 2>/dev/null
```

**Expected:** `{"status":"ok","version":"0.1.0"}`
**Fail if:** Server khong start hoac response sai format

---

### CHECK-05: Frontend dev server

```bash
cd frontend && timeout 10 npm run dev &
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
kill %1 2>/dev/null
```

**Expected:** HTTP 200
**Fail if:** npm run dev fail hoac HTTP status khac 200

---

### CHECK-06: Alembic config

```bash
cd backend && source venv/bin/activate && alembic current
```

**Expected:** Chay khong loi (output co the la empty vi chua co migration)
**Fail if:** Error message

---

### CHECK-07: .gitignore

```bash
cat .gitignore | grep -c -E "venv|node_modules|\.env|browser_profile|\.db"
```

**Expected:** >= 4 matches
**Fail if:** < 4 (thieu entries quan trong)

---

## Ghi ket qua

Tao `docs/phases/phase-1/checkpoints/cp0-environment/validation.json`:

```json
{
  "cp": "cp0-environment",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [
    {
      "name": "CHECK-01: Python version",
      "command": "python3 --version",
      "expected": "Python 3.12+",
      "actual": "<actual output>",
      "passed": true
    }
  ],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp1-schema-lock"
}
```

**Status rules:**
- `PASS`: Tat ca checks pass
- `PARTIAL`: Chi warning checks fail (CHECK-07) — co the proceed
- `FAIL`: Bat ky blocker check nao fail — khong the proceed

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05, CHECK-06
**Warning checks:** CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp0-environment \
    --role validator \
    --status PASS \
    --summary "All 7 checks passed. Environment ready." \
    --result-file docs/phases/phase-1/checkpoints/cp0-environment/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp0-environment/validation.json
```
