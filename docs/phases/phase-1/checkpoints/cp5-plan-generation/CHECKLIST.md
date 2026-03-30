# CP5 Validation Checklist — Plan Generation

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp5-plan-generation/result.json`
**Muc tieu:** Verify plan generation: ordered steps, write action classification, versioning, NL refinement.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp5-plan-generation/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP5 — Plan Generation",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Plan with ordered steps

```bash
# Tao session truoc
CID=$(curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic":"Phan hoi khach hang ve TPBank EVO"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['context_id'])")

# Generate plan
curl -s -X POST http://localhost:8000/api/plans \
  -H "Content-Type: application/json" \
  -d "{\"context_id\":\"$CID\"}" | python3 -c "
import json, sys; d=json.load(sys.stdin)
steps = d.get('steps', [])
assert len(steps) >= 2, f'Expected >=2 steps, got {len(steps)}'
for s in steps:
    for field in ['action_type','read_or_write','target','estimated_count','risk_level']:
        assert field in s, f'Missing field: {field}'
print(f'PASS — {len(steps)} steps')
"
```

**Expected:** PASS with step count
**Fail if:** Missing fields or < 2 steps

---

### CHECK-02: Write action classification

```bash
curl -s http://localhost:8000/api/plans/$PLAN_ID | python3 -c "
import json, sys; d=json.load(sys.stdin)
write_steps = [s for s in d['steps'] if s['read_or_write'] == 'WRITE']
for s in write_steps:
    assert s['risk_level'] in ('MEDIUM','HIGH'), f'{s[\"action_type\"]} should be MEDIUM/HIGH risk'
print(f'PASS — {len(write_steps)} write steps correctly classified')
"
```

**Expected:** PASS
**Fail if:** Write steps with LOW risk

---

### CHECK-03: NL refinement + versioning

```bash
curl -s -X PATCH "http://localhost:8000/api/plans/$PLAN_ID" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"chi crawl 2 groups thoi"}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d.get('version', 0) > 1, f'Version should be > 1, got {d.get(\"version\")}'
print(f'PASS — version {d[\"version\"]}')
"
```

**Expected:** PASS with version > 1
**Fail if:** Version still 1

---

### CHECK-04: Plan in DB

```bash
cd backend && sqlite3 app.db "SELECT plan_id, version, status FROM plans LIMIT 3;"
```

**Expected:** At least 1 row
**Fail if:** Empty

---

### CHECK-05: GET plan

```bash
curl -s http://localhost:8000/api/plans/$PLAN_ID | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert 'plan_id' in d and 'steps' in d
print(f'PASS — plan_id={d[\"plan_id\"]}, {len(d[\"steps\"])} steps')
"
```

**Expected:** PASS
**Fail if:** Missing plan_id or steps

---

### CHECK-06: PlanPage UI write action highlight

```bash
grep -ri "write.*action\|WRITE\|risk.*high\|warning\|canh-bao" frontend/src/pages/PlanPage.tsx | head -3
```

**Expected:** >= 1 match showing write action highlighting
**Fail if:** No evidence of write action visual distinction

---

### CHECK-07: Step dependencies

```bash
curl -s http://localhost:8000/api/plans/$PLAN_ID | python3 -c "
import json, sys; d=json.load(sys.stdin)
for s in d['steps']:
    print(f'{s[\"step_order\"]}: {s[\"action_type\"]} depends={s.get(\"dependency_step_ids\",[])}')
"
```

**Expected:** Dependencies make logical sense (crawl before analysis)
**Fail if:** Obviously wrong dependencies

---

## Ghi ket qua

```json
{
  "cp": "cp5-plan-generation",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp6-review-approve"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp5-plan-generation \
    --role validator \
    --status PASS \
    --summary "Plan generation verified." \
    --result-file docs/phases/phase-1/checkpoints/cp5-plan-generation/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp5-plan-generation/validation.json
```
