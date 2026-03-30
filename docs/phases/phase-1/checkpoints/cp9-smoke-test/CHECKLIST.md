# CP9 Validation Checklist — End-to-end Smoke Test

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp9-smoke-test/result.json`
**Muc tieu:** Verify full Phase 1 flow chay duoc end-to-end, khong crash, khong ban account.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp9-smoke-test/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP9 — End-to-end Smoke Test",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Full flow completed

```bash
# Verify a completed run exists with themes
cd backend && sqlite3 app.db "
SELECT r.run_id, r.status, COUNT(t.theme_id) as theme_count
FROM plan_runs r
LEFT JOIN theme_results t ON r.run_id = t.run_id
WHERE r.status = 'DONE'
GROUP BY r.run_id
LIMIT 1;
"
```

**Expected:** 1 row with status=DONE and theme_count > 0
**Fail if:** No completed run or 0 themes

---

### CHECK-02: Account still HEALTHY

```bash
curl -s http://localhost:8000/api/health/status | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d['status'] == 'HEALTHY', f'Account is {d[\"status\"]}!'
print('PASS — account HEALTHY')
"
```

**Expected:** PASS
**Fail if:** Account not HEALTHY (may indicate ban risk)

---

### CHECK-03: Themes in UI

```bash
# Get latest completed run
RUN_ID=$(cd backend && sqlite3 app.db "SELECT run_id FROM plan_runs WHERE status='DONE' ORDER BY ended_at DESC LIMIT 1;")
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys; d=json.load(sys.stdin)
themes = d.get('themes', [])
assert len(themes) >= 1, 'No themes'
has_sentiment = all(t.get('dominant_sentiment') for t in themes)
assert has_sentiment, 'Missing sentiment labels'
print(f'PASS — {len(themes)} themes with sentiment labels')
"
```

**Expected:** PASS
**Fail if:** No themes or missing sentiment

---

### CHECK-04: No unhandled errors

```bash
# Check server logs for unhandled exceptions
grep -ci "traceback\|unhandled\|500 internal" /tmp/social-listening-server.log 2>/dev/null || echo "0"
```

**Expected:** 0
**Fail if:** > 0 unhandled exceptions

---

### CHECK-05: PII check across DB

```bash
cd backend && python3 -c "
import sqlite3, re
conn = sqlite3.connect('app.db')
posts = conn.execute('SELECT content FROM crawled_posts').fetchall()
quotes = conn.execute('SELECT sample_quotes FROM theme_results').fetchall()
pii_found = 0
for row in posts + quotes:
    text = row[0] or ''
    if re.search(r'0\d{9,10}', text) or re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text):
        pii_found += 1
print(f'PII found in {pii_found} rows')
assert pii_found == 0, 'PII not fully masked!'
print('PASS')
"
```

**Expected:** PASS — 0 PII rows
**Fail if:** PII found

---

### CHECK-06: Duration < 10 minutes

```bash
cd backend && sqlite3 app.db "
SELECT
  run_id,
  ROUND((julianday(ended_at) - julianday(started_at)) * 24 * 60, 1) as minutes
FROM plan_runs
WHERE status = 'DONE'
ORDER BY ended_at DESC
LIMIT 1;
"
```

**Expected:** < 10 minutes
**Fail if:** > 10 minutes (performance concern, but not blocker)

---

### CHECK-07: DEMO_LOG.md exists

```bash
cat docs/phases/phase-1/checkpoints/cp9-smoke-test/DEMO_LOG.md | head -10
```

**Expected:** File exists with structured demo log
**Fail if:** File missing

---

## Ghi ket qua

```json
{
  "cp": "cp9-smoke-test",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": false,
  "next_cp": null
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp9-smoke-test \
    --role validator \
    --status PASS \
    --summary "Phase 1 COMPLETE. Full flow verified, account healthy, first visible value delivered." \
    --result-file docs/phases/phase-1/checkpoints/cp9-smoke-test/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp9-smoke-test/validation.json
```
