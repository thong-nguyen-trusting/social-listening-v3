# CP2 — Browser Session Setup

**Muc tieu:** BrowserAgent voi Camoufox persistent profile. User dang nhap Facebook 1 lan, session ton tai qua cac lan restart.
**Requires:** CP1 PASS + Camoufox binary da fetch (CP0)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp2-browser-session/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP2 — Browser Session Setup",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — BrowserAgent core

Tao `backend/app/infra/browser_agent.py` theo architecture.md Section 6.4:

```python
from camoufox.async_api import AsyncCamoufox
from pathlib import Path
import hmac, hashlib, asyncio

BROWSER_PROFILE_DIR = Path.home() / ".social-listening" / "browser_profile"
```

Implement:
- `__init__(self, event_queue)` — nhan asyncio.Queue de emit health signals
- `start()` — tao Camoufox voi `user_data_dir=BROWSER_PROFILE_DIR`, headless=False, geoip=True, humanize=True
- `is_logged_in()` — navigate facebook.com, check login button absent
- `wait_for_login()` — poll is_logged_in() moi 2s, tra ve account_id_hash (HMAC-SHA256 cua c_user cookie)
- `assert_session_valid()` — goi is_logged_in(), neu False → emit SESSION_EXPIRED signal + raise
- `stop()` — clean shutdown

Luu y: `_load_local_secret()` doc tu `.env` file (OPAQUE_ID_SECRET).

## Buoc 2 — Browser API

Tao `backend/app/api/browser.py`:
- `GET /api/browser/status` — doc account_health_state.session_status tu DB
- `POST /api/browser/setup` — trigger wait_for_login(), update DB khi xong
- `GET /api/browser/setup/stream` — SSE stream: browser_opened, login_detected, setup_complete

Tao `backend/app/schemas/browser.py`:
```python
from pydantic import BaseModel

class BrowserStatus(BaseModel):
    session_status: str  # NOT_SETUP | VALID | EXPIRED
    account_id_hash: str | None
    health_status: str   # HEALTHY | CAUTION | BLOCKED
    cooldown_until: str | None
```

Register router trong `main.py`.

## Buoc 3 — Update AccountHealthState on login

Khi `wait_for_login()` thanh cong:
- Update `account_health_state.session_status = 'VALID'`
- Update `account_health_state.account_id_hash = <hash>`
- Update `account_health_state.status = 'HEALTHY'` (neu chua co row → INSERT)

## Buoc 4 — Frontend SetupPage

Tao `frontend/src/pages/SetupPage.tsx`:
- Goi GET /api/browser/status khi mount
- Neu NOT_SETUP: hien button "Ket noi Facebook" → goi POST /api/browser/setup
- Subscribe GET /api/browser/setup/stream de cap nhat realtime
- Khi VALID: hien "Da ket noi — San sang" va redirect toi trang chinh

## Buoc 5 — Viet result.json va gui notification

```json
{
  "cp": "cp2-browser-session",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "BrowserAgent with persistent Camoufox profile. Login once, session persists across restarts.",
  "artifacts": [
    {"file": "backend/app/infra/browser_agent.py", "action": "created"},
    {"file": "backend/app/api/browser.py", "action": "created"},
    {"file": "backend/app/schemas/browser.py", "action": "created"},
    {"file": "backend/app/main.py", "action": "modified"},
    {"file": "frontend/src/pages/SetupPage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": "Requires real Facebook account for full test."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp2-browser-session \
    --role implementer \
    --status READY \
    --summary "Browser session setup complete." \
    --result-file docs/phases/phase-1/checkpoints/cp2-browser-session/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp2-browser-session/result.json
```
