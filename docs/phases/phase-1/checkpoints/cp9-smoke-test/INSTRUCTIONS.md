# CP9 — End-to-end Smoke Test

**Muc tieu:** Chay full flow voi real account, chung minh Phase 1 hoat dong.
**Requires:** CP8 PASS + real Facebook account da login (CP2)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp9-smoke-test/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP9 — End-to-end Smoke Test voi real account",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — Pre-flight checks

```bash
# 1. Backend running
curl -s http://localhost:8000/health

# 2. Session valid
curl -s http://localhost:8000/api/browser/status | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d['session_status'] == 'VALID', 'Login truoc!'
assert d['health_status'] == 'HEALTHY', 'Health khong OK!'
print('Pre-flight OK')
"

# 3. Frontend running
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
```

## Buoc 2 — Chay full flow

Chon 1 trong 2 cach:

### Cach A — Qua UI (recommended cho demo)

1. Mo http://localhost:5173
2. Nhap topic: "Phan hoi khach hang ve TPBank EVO"
3. Review keywords → confirm
4. Review plan (chi CRAWL_FEED, khong JOIN_GROUP)
5. Approve
6. Xem monitor — doi steps chay xong
7. Xem ThemesPage — verify themes + sentiment

### Cach B — Qua API script

Tao `backend/tests/e2e_smoke.py`:
```python
import httpx, asyncio, json

BASE = "http://localhost:8000"

async def smoke():
    async with httpx.AsyncClient(base_url=BASE, timeout=120) as c:
        # 1. Create session
        r = await c.post("/api/sessions", json={"topic": "Phan hoi ve TPBank EVO"})
        ctx = r.json()
        print(f"1. Session: {ctx['context_id']} — {ctx['status']}")

        # 2. Confirm keywords (neu keywords_ready)
        if ctx['status'] == 'keywords_ready':
            context_id = ctx['context_id']
        else:
            # Answer clarification...
            pass

        # 3. Generate plan
        r = await c.post("/api/plans", json={"context_id": context_id})
        plan = r.json()
        print(f"2. Plan: {plan['plan_id']} — {len(plan['steps'])} steps")

        # 4. Approve (read-only steps only for smoke test)
        read_steps = [s['step_id'] for s in plan['steps'] if s['read_or_write'] == 'READ']
        r = await c.post(f"/api/plans/{plan['plan_id']}/approve", json={"step_ids": read_steps})
        grant = r.json()
        print(f"3. Approved: {grant['grant_id']}")

        # 5. Start run
        r = await c.post("/api/runs", json={"plan_id": plan['plan_id'], "grant_id": grant['grant_id']})
        run = r.json()
        print(f"4. Run started: {run['run_id']}")

        # 6. Wait for completion
        while True:
            await asyncio.sleep(5)
            r = await c.get(f"/api/runs/{run['run_id']}")
            status = r.json()['status']
            print(f"   ... status: {status}")
            if status in ('DONE', 'FAILED', 'CANCELLED'):
                break

        # 7. Get themes
        r = await c.get(f"/api/runs/{run['run_id']}/themes")
        themes = r.json()
        print(f"5. Themes: {len(themes['themes'])} themes, {themes['posts_crawled']} posts")
        for t in themes['themes']:
            print(f"   - {t['label']} ({t['dominant_sentiment']}): {t['post_count']} posts")

        # 8. Health check
        r = await c.get("/api/health/status")
        print(f"6. Health: {r.json()['status']}")

asyncio.run(smoke())
```

## Buoc 3 — Ghi DEMO_LOG.md

Tao `docs/phases/phase-1/checkpoints/cp9-smoke-test/DEMO_LOG.md`:
```markdown
# Demo Log — Phase 1 Smoke Test

**Date:** 2026-XX-XX
**Account:** [account_id_hash first 8 chars]
**Topic:** "Phan hoi khach hang ve TPBank EVO"

## Results

- Keywords generated: X across 5 categories
- Plan: X steps (Y read, Z write)
- Approved: read-only steps
- Crawled: X posts from Y groups
- Excluded: X spam posts
- Themes found: X
  1. [label] — [sentiment] — X posts
  2. ...
- Health after run: HEALTHY
- Total duration: X minutes
- Errors: none / [describe]
```

## Buoc 4 — Viet result.json va gui notification

```json
{
  "cp": "cp9-smoke-test",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Full flow smoke test passed. Topic → keywords → plan → approve → crawl → themes. No account ban.",
  "artifacts": [
    {"file": "backend/tests/e2e_smoke.py", "action": "created"},
    {"file": "docs/phases/phase-1/checkpoints/cp9-smoke-test/DEMO_LOG.md", "action": "created"}
  ],
  "issues": [],
  "notes": "Phase 1 delivers first visible value."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp9-smoke-test \
    --role implementer \
    --status READY \
    --summary "Phase 1 smoke test PASSED." \
    --result-file docs/phases/phase-1/checkpoints/cp9-smoke-test/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp9-smoke-test/result.json
```
