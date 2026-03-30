# CP7 — E2E Smoke Test

**Mục tiêu:** Full end-to-end validation of Phase 3 smart crawl pipeline.
**Requires:** CP0-CP6 all PASS

---

## Bước 1 — Mock mode e2e

```bash
docker exec social-listening-v3 python -c "
import requests, json, time

# 1. Create session
r = requests.post('http://localhost:8000/api/sessions', json={'topic': 'sản phẩm làm đẹp thiên nhiên'})
session = r.json()
ctx = session['context_id']
print(f'Session: {ctx}')

# 2. Generate plan
r = requests.post('http://localhost:8000/api/plans', json={'context_id': ctx})
plan = r.json()
plan_id = plan['plan_id']
print(f'Plan: {plan_id} with {len(plan[\"steps\"])} steps')

# 3. Approve all steps
step_ids = [s['step_id'] for s in plan['steps']]
r = requests.post(f'http://localhost:8000/api/plans/{plan_id}/approve', json={'step_ids': step_ids})
grant = r.json()
print(f'Grant: {grant[\"grant_id\"]}')

# 4. Start run
r = requests.post('http://localhost:8000/api/runs', json={'plan_id': plan_id, 'grant_id': grant['grant_id']})
run = r.json()
run_id = run['run_id']
print(f'Run: {run_id}')

# 5. Wait for completion
for i in range(60):
    time.sleep(2)
    r = requests.get(f'http://localhost:8000/api/runs/{run_id}')
    run = r.json()
    if run['status'] in ('DONE', 'FAILED', 'CANCELLED'):
        break

print(f'Status: {run[\"status\"]}')
print(f'Total records: {run[\"total_records\"]}')
print(f'Pipeline summary: {json.dumps(run.get(\"pipeline_summary\"), indent=2, ensure_ascii=False)}')

# 6. Check steps
for step in run.get('steps', []):
    print(f'  {step[\"step_id\"]}: {step[\"action_type\"]} → {step[\"status\"]} (actual={step[\"actual_count\"]})')
"
```

## Bước 2 — Verify metrics

Compare with pre-Phase 3 run (run-802cb7073a):
- Before: 50 posts, 44% relevant, 19 groups (16 irrelevant)
- After: should see higher relevant %, fewer groups in JOIN_GROUP/SEARCH_IN_GROUP

Record results in `DEMO_LOG.md`.

## Bước 3 — Feature flag test

Set `PIPELINE_INTELLIGENCE_ENABLED=false` in container env, restart, run same test.
Verify: no pipeline_summary, all groups processed, no priority ordering.

## Bước 4 — Real browser test (optional)

If Facebook session active:
```bash
# Run with real browser on a different topic
# Verify group names resolve correctly
# Verify quality gate works with real data
```

## Bước 5 — Write DEMO_LOG.md + result.json

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp7-smoke-test --role implementer --status READY \
    --summary "E2E smoke test complete — Phase 3 verified" \
    --result-file docs/phases/phase-3/checkpoints/cp7-smoke-test/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp7-smoke-test/result.json
```
