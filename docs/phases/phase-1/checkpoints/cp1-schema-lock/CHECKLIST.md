# CP1 Validation Checklist — Schema Lock + DB Migration

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp1-schema-lock/result.json`
**Muc tieu:** Verify 9 tables duoc tao dung, constraints chinh xac, migration roundtrip sach.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp1-schema-lock/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP1 — Schema Lock",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Danh sach kiem tra

### CHECK-01: Alembic upgrade head

```bash
cd backend && source venv/bin/activate && alembic upgrade head 2>&1; echo "EXIT: $?"
```

**Expected:** EXIT: 0
**Fail if:** Any error

---

### CHECK-02: 9 tables exist

```bash
cd backend && sqlite3 app.db ".tables" | tr ' ' '\n' | sort | grep -v '^$'
```

**Expected:** product_contexts, plans, plan_steps, approval_grants, plan_runs, step_runs, crawled_posts, theme_results, account_health_state, account_health_log (10 tables including alembic_version)
**Fail if:** Any core table missing

---

### CHECK-03: theme_results.dominant_sentiment

```bash
cd backend && sqlite3 app.db ".schema theme_results" | grep -i dominant_sentiment
```

**Expected:** Output contains `dominant_sentiment` with CHECK constraint containing 'positive','negative','neutral'
**Fail if:** Column missing or constraint wrong

---

### CHECK-04: account_health_state session fields

```bash
cd backend && sqlite3 app.db ".schema account_health_state" | grep -E "session_status|account_id_hash"
```

**Expected:** Both `session_status` and `account_id_hash` present
**Fail if:** Either column missing

---

### CHECK-05: plan_steps.action_type constraint

```bash
cd backend && sqlite3 app.db ".schema plan_steps" | grep -i action_type
```

**Expected:** CHECK constraint with CRAWL_FEED, JOIN_GROUP, CRAWL_COMMENTS, CRAWL_GROUP_META, SEARCH_GROUPS
**Fail if:** Any value missing from constraint

---

### CHECK-06: Migration roundtrip

```bash
cd backend && source venv/bin/activate && alembic downgrade base && alembic upgrade head 2>&1; echo "EXIT: $?"
```

**Expected:** EXIT: 0, no errors
**Fail if:** Any error during downgrade or upgrade

---

### CHECK-07: Models importable

```bash
cd backend && source venv/bin/activate && python -c "
from app.models.base import Base
from app.models.product_context import ProductContext
from app.models.plan import Plan, PlanStep
from app.models.approval import ApprovalGrant
from app.models.run import PlanRun, StepRun
from app.models.crawled_post import CrawledPost
from app.models.theme_result import ThemeResult
from app.models.health import AccountHealthState, AccountHealthLog
print(f'OK: {len(Base.metadata.tables)} tables')
"
```

**Expected:** "OK: N tables" (N >= 9)
**Fail if:** ImportError or count < 9

---

## Ghi ket qua

Tao `docs/phases/phase-1/checkpoints/cp1-schema-lock/validation.json`:

```json
{
  "cp": "cp1-schema-lock",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [
    {"name": "CHECK-01: Alembic upgrade head", "command": "...", "expected": "...", "actual": "...", "passed": true}
  ],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp2-browser-session"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05, CHECK-06, CHECK-07
**Warning checks:** (none)

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp1-schema-lock \
    --role validator \
    --status PASS \
    --summary "All 7 checks passed. Schema locked." \
    --result-file docs/phases/phase-1/checkpoints/cp1-schema-lock/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp1-schema-lock/validation.json
```
