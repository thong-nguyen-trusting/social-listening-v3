# CP2 Validation Checklist — Browser Session Setup

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp2-browser-session/result.json`
**Muc tieu:** Verify BrowserAgent persistent session hoat dong: login 1 lan, session survive restart.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp2-browser-session/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP2 — Browser Session",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Status NOT_SETUP khi chua login

```bash
curl -s http://localhost:8000/api/browser/status | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['session_status'])"
```

**Expected:** `NOT_SETUP`
**Fail if:** Bat ky status khac

---

### CHECK-02: POST /api/browser/setup mo browser

```bash
curl -s -X POST http://localhost:8000/api/browser/setup | python3 -c "import json,sys; d=json.load(sys.stdin); print(d)"
```

**Expected:** Browser Camoufox visible xuat hien, response {"ok": true}
**Fail if:** Browser khong mo hoac error

---

### CHECK-03: Sau login → VALID + account_id_hash

```bash
# Sau khi user da login Facebook trong browser window:
curl -s http://localhost:8000/api/browser/status | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'session: {d[\"session_status\"]}')
print(f'hash: {d[\"account_id_hash\"]}')
assert d['session_status'] == 'VALID'
assert d['account_id_hash'] is not None and len(d['account_id_hash']) > 10
print('PASS')
"
```

**Expected:** session: VALID, hash: (non-null hex string)
**Fail if:** session khac VALID hoac hash la null

---

### CHECK-04: Session persist qua restart

```bash
# Restart backend server, roi:
curl -s http://localhost:8000/api/browser/status | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['session_status'] == 'VALID', f'Expected VALID, got {d[\"session_status\"]}'
print('PASS — session survived restart')
"
```

**Expected:** PASS — session survived restart
**Fail if:** session_status khong phai VALID

---

### CHECK-05: Browser profile directory

```bash
ls -la ~/.social-listening/browser_profile/ 2>/dev/null | head -5
```

**Expected:** Directory ton tai va chua Firefox profile files
**Fail if:** Directory khong ton tai

---

### CHECK-06: account_id_hash la HMAC

```bash
curl -s http://localhost:8000/api/browser/status | python3 -c "
import json, sys, re
d = json.load(sys.stdin)
h = d.get('account_id_hash', '')
assert re.match(r'^[a-f0-9]{16,64}$', h), f'Not hex hash: {h}'
print(f'PASS — hash: {h[:8]}...')
"
```

**Expected:** PASS — hash looks like hex HMAC
**Fail if:** Hash contains plaintext or non-hex characters

---

### CHECK-07: SetupPage UI

```bash
curl -s http://localhost:5173 | grep -c "SetupPage\|setup\|ket-noi\|connect"
```

**Expected:** >= 1 match (page renders)
**Fail if:** 0 matches (page khong ton tai)

---

## Ghi ket qua

```json
{
  "cp": "cp2-browser-session",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp3-health-monitor"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp2-browser-session \
    --role validator \
    --status PASS \
    --summary "Browser session persists across restarts." \
    --result-file docs/phases/phase-1/checkpoints/cp2-browser-session/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp2-browser-session/validation.json
```
