# CP3 Validation Checklist — Health Monitor

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp3-health-monitor/result.json`
**Muc tieu:** Verify state machine transitions, signal detection, audit log, va safety stop.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp3-health-monitor/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP3 — Health Monitor",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Default HEALTHY status

```bash
curl -s http://localhost:8000/api/health/status | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d['status'] == 'HEALTHY', f'Expected HEALTHY, got {d[\"status\"]}'
print('PASS')
"
```

**Expected:** PASS
**Fail if:** Status khac HEALTHY

---

### CHECK-02: CAPTCHA signal → BLOCKED

```bash
# Trigger mock CAPTCHA signal (implementation-specific test endpoint or direct event):
curl -s -X POST http://localhost:8000/api/health/_test/signal -d '{"signal":"CAPTCHA"}' | python3 -c "
import json, sys; d=json.load(sys.stdin); print(d)
"
curl -s http://localhost:8000/api/health/status | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d['status'] == 'BLOCKED', f'Expected BLOCKED, got {d[\"status\"]}'
assert d['cooldown_until'] is not None
print('PASS')
"
```

**Expected:** Status BLOCKED, cooldown_until non-null
**Fail if:** Status khong phai BLOCKED

---

### CHECK-03: Action-blocked signal → CAUTION

```bash
# Reset first, then trigger action-blocked
curl -s -X POST http://localhost:8000/api/health/reset -d '{"confirm":true}'
curl -s -X POST http://localhost:8000/api/health/_test/signal -d '{"signal":"ACTION_BLOCKED"}'
curl -s http://localhost:8000/api/health/status | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d['status'] == 'CAUTION', f'Expected CAUTION, got {d[\"status\"]}'
print('PASS')
"
```

**Expected:** PASS
**Fail if:** Status khong phai CAUTION

---

### CHECK-04: Audit log

```bash
cd backend && sqlite3 app.db "SELECT signal_type, status_before, status_after FROM account_health_log ORDER BY detected_at DESC LIMIT 3;"
```

**Expected:** Co it nhat 2 rows (CAPTCHA va ACTION_BLOCKED transitions)
**Fail if:** Table rong hoac thieu transitions

---

### CHECK-05: Reset chi khi cooldown het

```bash
# Trigger CAPTCHA (sets 24h cooldown), then try reset immediately
curl -s -X POST http://localhost:8000/api/health/_test/signal -d '{"signal":"CAPTCHA"}'
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/health/reset -d '{"confirm":true}')
echo "HTTP status: $RESULT"
```

**Expected:** HTTP 400 (cooldown chua het)
**Fail if:** HTTP 200 (cho phep reset khi con cooldown)

---

### CHECK-06: HealthBadge UI

```bash
curl -s http://localhost:5173 | grep -ci "health\|badge\|status"
```

**Expected:** >= 1
**Fail if:** 0

---

### CHECK-07: EventBus dispatch

```bash
cd backend && source venv/bin/activate && python -c "
import asyncio
from app.infra.event_bus import EventBus, HealthChangedEvent

received = []
bus = EventBus()
bus.subscribe(HealthChangedEvent, lambda e: received.append(e))
asyncio.run(bus.emit(HealthChangedEvent('BLOCKED', 'CAPTCHA', None)))
assert len(received) == 1, f'Expected 1 event, got {len(received)}'
print('PASS')
"
```

**Expected:** PASS
**Fail if:** Event khong duoc nhan

---

## Ghi ket qua

```json
{
  "cp": "cp3-health-monitor",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp4-keyword-analysis"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05, CHECK-07
**Warning checks:** CHECK-06

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp3-health-monitor \
    --role validator \
    --status PASS \
    --summary "Health monitor state machine verified." \
    --result-file docs/phases/phase-1/checkpoints/cp3-health-monitor/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp3-health-monitor/validation.json
```
