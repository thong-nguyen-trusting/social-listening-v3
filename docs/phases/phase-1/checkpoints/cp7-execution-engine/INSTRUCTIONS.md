# CP7 — Execution Engine

**Muc tieu:** RunnerService orchestrate step execution + BrowserAgent.crawl_feed() crawl Facebook that.
**Requires:** CP6 PASS (ApprovalGrant), CP2 PASS (BrowserAgent voi session)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp7-execution-engine/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP7 — Execution Engine (highest risk CP)",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — PII Masker

Tao `backend/app/infra/pii_masker.py`:
```python
import re

class PIIMasker:
    PATTERNS = [
        (re.compile(r'\b0\d{9,10}\b'), '[PHONE]'),          # VN phone
        (re.compile(r'\b\d{9,12}\b'), '[ID_NUMBER]'),        # CMND/CCCD
        (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), '[EMAIL]'), # Email
    ]

    def mask(self, text: str) -> str:
        for pattern, replacement in self.PATTERNS:
            text = pattern.sub(replacement, text)
        return text
```

## Buoc 2 — BrowserAgent.crawl_feed()

Update `backend/app/infra/browser_agent.py`:
```python
async def crawl_feed(self, group_id: str, target_count: int,
                     checkpoint: dict | None) -> List[RawPost]:
    await self.assert_session_valid()
    url = f"https://www.facebook.com/groups/{group_id}"
    await self._page.goto(url)

    posts = []
    start_index = checkpoint.get('collected_count', 0) if checkpoint else 0

    while len(posts) < target_count:
        # Scroll + extract posts from DOM
        # Rate limiting: await asyncio.sleep(random.uniform(2, 5))
        # CAPTCHA check moi iteration
        # PII mask truoc khi add vao list
        ...

    return posts
```

Luu y:
- Rate limiting: CRAWL_FEED max 10/hour, min delay 5s giua cac scroll
- Checkpoint: luu collected_count, last_cursor de resume
- humanize=True trong Camoufox da add random delays cho mouse/keyboard

## Buoc 3 — RunnerService

Tao `backend/app/services/runner.py` theo architecture.md Section 6.3:

```python
class RunnerService:
    async def start_run(self, plan_id: str, grant_id: str) -> PlanRun:
        # Validate grant
        # Create PlanRun + StepRuns (PENDING)
        # Start _execute_run as background task

    async def _execute_run(self, run_id: str):
        for step_run in step_runs_ordered:
            # Check health before write steps
            if step.read_or_write == 'WRITE' and not health_monitor.is_write_allowed():
                raise SafetyStopException()

            # Update checkpoint BEFORE starting
            # Execute step via BrowserAgent
            # Update StepRun status → DONE
            # Emit StepCompletedEvent

    async def pause_run(self, run_id: str): ...
    async def resume_run(self, run_id: str): ...
    async def stop_run(self, run_id: str): ...
```

## Buoc 4 — Run API + SSE

Tao `backend/app/api/runs.py`:
- `POST /api/runs` — body: {plan_id, grant_id} → start_run()
- `GET /api/runs/{run_id}` — full run status + steps
- `POST /api/runs/{run_id}/pause`
- `POST /api/runs/{run_id}/resume`
- `POST /api/runs/{run_id}/stop`
- `GET /api/runs/{run_id}/stream` — SSE voi events:
  - step_started, step_done, step_failed, run_paused, safety_stop, session_expired, run_done

## Buoc 5 — Frontend MonitorPage

Tao `frontend/src/pages/MonitorPage.tsx`:
- Subscribe SSE stream
- Hien thi steps voi status badges: Pending (xam), Running (xanh + spinner), Done (xanh la), Failed (do)
- Buttons: Pause, Resume, Stop
- Execution summary khi run xong

## Buoc 6 — Viet result.json va gui notification

```json
{
  "cp": "cp7-execution-engine",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Execution engine with crawl_feed, pause/resume, SSE streaming, PII masking.",
  "artifacts": [
    {"file": "backend/app/services/runner.py", "action": "created"},
    {"file": "backend/app/api/runs.py", "action": "created"},
    {"file": "backend/app/infra/browser_agent.py", "action": "modified"},
    {"file": "backend/app/infra/pii_masker.py", "action": "created"},
    {"file": "frontend/src/pages/MonitorPage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": "crawl_feed requires real FB session. Test with low target_count (5-10 posts)."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp7-execution-engine \
    --role implementer \
    --status READY \
    --summary "Execution engine with real Facebook crawl." \
    --result-file docs/phases/phase-1/checkpoints/cp7-execution-engine/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp7-execution-engine/result.json
```
