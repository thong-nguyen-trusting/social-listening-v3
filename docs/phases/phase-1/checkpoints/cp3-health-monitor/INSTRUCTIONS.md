# CP3 — Health Monitor

**Muc tieu:** HealthMonitorService event-driven state machine + EventBus + safety stop.
**Requires:** CP2 PASS (BrowserAgent da co)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp3-health-monitor/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP3 — Health Monitor",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — EventBus

Tao `backend/app/infra/event_bus.py` theo architecture.md Section 7:

```python
import asyncio
from dataclasses import dataclass
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._subscribers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable):
        self._subscribers.setdefault(event_type, []).append(handler)

    async def emit(self, event: Any):
        for handler in self._subscribers.get(type(event), []):
            await handler(event)
```

Dinh nghia events:
```python
@dataclass
class HealthChangedEvent:
    new_status: str  # HEALTHY | CAUTION | BLOCKED
    signal_type: str
    cooldown_until: datetime | None

@dataclass
class HealthSignal:
    signal_type: str  # CAPTCHA | ACTION_BLOCKED | RATE_LIMIT | SESSION_EXPIRED
```

## Buoc 2 — HealthMonitorService

Tao `backend/app/services/health_monitor.py` theo architecture.md Section 6.1:

- State machine: HEALTHY → CAUTION (action-blocked, rate-limit) → BLOCKED (CAPTCHA)
- `_monitor_loop()` — asyncio background task, doc tu event_queue
- `_transition(signal)` — chuyen state, persist vao DB, emit HealthChangedEvent
- `is_write_allowed()` → True chi khi HEALTHY
- Cooldown logic: 24h cho CAPTCHA, 1h cho action-blocked

Persist moi transition vao `account_health_log`.

## Buoc 3 — BrowserAgent signal emission

Update `browser_agent.py` — them `_on_route()`:
- Intercept moi response qua `page.route("**/*", self._on_route)`
- Detect CAPTCHA: DOM selector hoac response pattern
- Detect action-blocked: specific error page/dialog
- Detect session-expired: redirect to login page
- Emit signal qua `self._event_queue.put()`

## Buoc 4 — Health API

Tao `backend/app/api/health.py`:
- `GET /api/health/status` — current status, cooldown_until, last_signal
- `POST /api/health/acknowledge` — acknowledge signal (ghi nhan)
- `POST /api/health/reset` — chi cho phep khi cooldown het → set HEALTHY

Register trong `main.py`. Start monitor background task on app startup.

## Buoc 5 — HealthBadge UI

Tao `frontend/src/components/HealthBadge.tsx`:
- Poll GET /api/health/status moi 5s (hoac dung SSE)
- HEALTHY = xanh la, CAUTION = vang, BLOCKED = do
- Hien thi cooldown countdown khi co

## Buoc 6 — Viet result.json va gui notification

```json
{
  "cp": "cp3-health-monitor",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Health monitor active. State machine HEALTHY→CAUTION→BLOCKED. Event-driven signal detection.",
  "artifacts": [
    {"file": "backend/app/services/health_monitor.py", "action": "created"},
    {"file": "backend/app/infra/event_bus.py", "action": "created"},
    {"file": "backend/app/api/health.py", "action": "created"},
    {"file": "backend/app/schemas/health.py", "action": "created"},
    {"file": "backend/app/infra/browser_agent.py", "action": "modified"},
    {"file": "frontend/src/components/HealthBadge.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": "Signal detection requires manual trigger for testing — mock CAPTCHA DOM."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp3-health-monitor \
    --role implementer \
    --status READY \
    --summary "Health monitor with event-driven state machine." \
    --result-file docs/phases/phase-1/checkpoints/cp3-health-monitor/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp3-health-monitor/result.json
```
