# CP7 Validation Checklist — Execution Engine

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp7-execution-engine/result.json`
**Muc tieu:** Verify full execution loop: start → steps execute → pause/resume → crawl real data → SSE updates.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp7-execution-engine/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP7 — Execution Engine",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Start run

```bash
curl -s -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d "{\"plan_id\":\"$PLAN_ID\",\"grant_id\":\"$GRANT_ID\"}" | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert 'run_id' in d
assert d.get('status') == 'RUNNING'
print(f'PASS — run_id={d[\"run_id\"]}')
"
```

**Expected:** PASS with run_id, status=RUNNING
**Fail if:** No run_id or status wrong

---

### CHECK-02: Step execution order

```bash
# Wait for run to progress, then check
sleep 10
curl -s "http://localhost:8000/api/runs/$RUN_ID" | python3 -c "
import json, sys; d=json.load(sys.stdin)
steps = d.get('steps', [])
done = [s for s in steps if s['status'] == 'DONE']
print(f'{len(done)}/{len(steps)} steps done')
assert len(done) >= 1, 'No steps completed'
print('PASS')
"
```

**Expected:** At least 1 step DONE
**Fail if:** 0 steps completed

---

### CHECK-03: Pause

```bash
curl -s -X POST "http://localhost:8000/api/runs/$RUN_ID/pause" | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d.get('status') == 'PAUSED'
print('PASS')
"
```

**Expected:** status=PAUSED
**Fail if:** Status not PAUSED

---

### CHECK-04: Resume

```bash
curl -s -X POST "http://localhost:8000/api/runs/$RUN_ID/resume" | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d.get('status') == 'RUNNING'
print('PASS')
"
```

**Expected:** status=RUNNING
**Fail if:** Status not RUNNING

---

### CHECK-05: Real Facebook crawl

```bash
cd backend && sqlite3 app.db "SELECT COUNT(*) as cnt FROM crawled_posts WHERE run_id='$RUN_ID';"
```

**Expected:** cnt >= 1 (real posts crawled)
**Fail if:** cnt = 0

---

### CHECK-06: PII masking

```bash
cd backend && sqlite3 app.db "SELECT content FROM crawled_posts WHERE run_id='$RUN_ID' LIMIT 5;" | grep -cE "0[0-9]{9}|[a-zA-Z0-9.+-]+@[a-zA-Z0-9-]"
```

**Expected:** 0 (no raw phone/email in stored content)
**Fail if:** > 0 (PII not masked)

---

### CHECK-07: SSE events

```bash
timeout 15 curl -s -N "http://localhost:8000/api/runs/$RUN_ID/stream" 2>/dev/null | head -20
```

**Expected:** Lines containing `event:` and `data:` (step_started, step_done, etc.)
**Fail if:** No SSE events received

---

### CHECK-08: Checkpoint persistence

```bash
cd backend && sqlite3 app.db "SELECT step_run_id, checkpoint IS NOT NULL as has_cp FROM step_runs WHERE run_id='$RUN_ID' AND status='DONE' LIMIT 3;"
```

**Expected:** has_cp = 1 for completed steps
**Fail if:** checkpoint is NULL for DONE steps

---

### CHECK-09: MonitorPage UI

```bash
grep -ri "EventSource\|SSE\|stream\|step.*status" frontend/src/pages/MonitorPage.tsx | head -3
```

**Expected:** >= 1 match (SSE connection logic)
**Fail if:** No SSE integration found

---

## Ghi ket qua

```json
{
  "cp": "cp7-execution-engine",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp8-theme-analysis"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05, CHECK-06, CHECK-07
**Warning checks:** CHECK-08, CHECK-09

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp7-execution-engine \
    --role validator \
    --status PASS \
    --summary "Execution engine verified with real Facebook crawl." \
    --result-file docs/phases/phase-1/checkpoints/cp7-execution-engine/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp7-execution-engine/validation.json
```
