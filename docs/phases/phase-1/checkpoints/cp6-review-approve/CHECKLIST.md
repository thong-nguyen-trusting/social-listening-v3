# CP6 Validation Checklist — Review & Approve

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp6-review-approve/result.json`
**Muc tieu:** Verify approval flow: grant creation, health gate, invalidation on plan edit.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp6-review-approve/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP6 — Review & Approve",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Approve creates grant

```bash
curl -s -X POST "http://localhost:8000/api/plans/$PLAN_ID/approve" \
  -H "Content-Type: application/json" \
  -d '{"step_ids":["step-1","step-2"]}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert 'grant_id' in d, 'Missing grant_id'
assert d.get('plan_version') >= 1
assert len(d.get('approved_step_ids',[])) == 2
print(f'PASS — grant_id={d[\"grant_id\"]}')
"
```

**Expected:** PASS with grant_id
**Fail if:** Missing grant_id or wrong step count

---

### CHECK-02: Health gate blocks write actions

```bash
# Set health to CAUTION first
curl -s -X POST http://localhost:8000/api/health/_test/signal -d '{"signal":"ACTION_BLOCKED"}'
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/plans/$PLAN_ID/approve" \
  -H "Content-Type: application/json" \
  -d '{"step_ids":["write-step-id"]}')
echo "HTTP: $RESULT"
# Reset health
curl -s -X POST http://localhost:8000/api/health/reset -d '{"confirm":true}'
```

**Expected:** HTTP 400
**Fail if:** HTTP 200

---

### CHECK-03: Empty step_ids → 400

```bash
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/plans/$PLAN_ID/approve" \
  -H "Content-Type: application/json" \
  -d '{"step_ids":[]}')
echo "HTTP: $RESULT"
```

**Expected:** HTTP 400
**Fail if:** HTTP 200

---

### CHECK-04: Edit plan → grant invalidated

```bash
# Approve first
GRANT=$(curl -s -X POST "http://localhost:8000/api/plans/$PLAN_ID/approve" \
  -H "Content-Type: application/json" \
  -d '{"step_ids":["step-1"]}' | python3 -c "import json,sys; print(json.load(sys.stdin)['grant_id'])")

# Edit plan
curl -s -X PATCH "http://localhost:8000/api/plans/$PLAN_ID" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"bo step cuoi"}'

# Check grant status
cd backend && sqlite3 app.db "SELECT grant_id, invalidated FROM approval_grants WHERE grant_id='$GRANT';"
```

**Expected:** invalidated = 1 (or True)
**Fail if:** Grant still valid after plan edit

---

### CHECK-05: Grant in DB

```bash
cd backend && sqlite3 app.db "SELECT grant_id, plan_version, approver_id, approved_at FROM approval_grants LIMIT 3;"
```

**Expected:** Rows with all fields populated, approver_id='local_user'
**Fail if:** Missing fields

---

### CHECK-06: ApprovePage UI

```bash
grep -ri "approve\|checklist\|write.*action\|health" frontend/src/pages/ApprovePage.tsx | head -5
```

**Expected:** >= 1 match
**Fail if:** File missing or no relevant content

---

### CHECK-07: Dependency warning

```bash
# Test via UI or check code for dependency logic
grep -ri "dependency\|depend\|skip" frontend/src/pages/ApprovePage.tsx backend/app/services/approval.py | head -3
```

**Expected:** Evidence of dependency checking logic
**Fail if:** No dependency logic found

---

## Ghi ket qua

```json
{
  "cp": "cp6-review-approve",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp7-execution-engine"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp6-review-approve \
    --role validator \
    --status PASS \
    --summary "Approval flow verified." \
    --result-file docs/phases/phase-1/checkpoints/cp6-review-approve/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp6-review-approve/validation.json
```
