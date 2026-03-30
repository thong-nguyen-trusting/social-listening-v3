# CP1 — Schema Lock + DB Migration

**Muc tieu:** Tao 9 tables trong SQLite qua Alembic migration, voi SQLAlchemy models map dung.
**Requires:** CP0 PASS + backend venv activated

---

## Buoc 0 — Bao bat dau (bat buoc, chay truoc tien)

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp1-schema-lock/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP1 — Schema Lock + DB Migration",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — SQLAlchemy models

Tao `backend/app/models/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Tao models cho 9 tables theo schema trong `docs/phases/phase-1/architecture.md` Section 4.1:

- `product_context.py` — ProductContext
- `plan.py` — Plan, PlanStep
- `approval.py` — ApprovalGrant
- `run.py` — PlanRun, StepRun
- `crawled_post.py` — CrawledPost
- `theme_result.py` — ThemeResult (bao gom `dominant_sentiment` column)
- `health.py` — AccountHealthState (bao gom `session_status`, `account_id_hash`), AccountHealthLog

Luu y:
- ThemeResult.dominant_sentiment: CHECK constraint IN ('positive','negative','neutral')
- AccountHealthState.session_status: CHECK constraint IN ('NOT_SETUP','VALID','EXPIRED')
- PlanStep.action_type: CHECK constraint 5 values
- JSON fields (keyword_json, approved_step_ids, etc.) luu dang TEXT

## Buoc 2 — Alembic migration

Update `alembic/env.py` de import Base:
```python
from app.models.base import Base
target_metadata = Base.metadata
```

Auto-generate migration:
```bash
cd backend
alembic revision --autogenerate -m "initial schema — 9 tables"
```

Review file migration duoc tao → verify du 9 tables.

Apply:
```bash
alembic upgrade head
```

## Buoc 3 — Verify roundtrip

```bash
alembic downgrade base
alembic upgrade head
```

Phai chay sach khong loi.

## Buoc 4 — Verify models importable

```bash
python -c "
from app.models.base import Base
from app.models.product_context import ProductContext
from app.models.plan import Plan, PlanStep
from app.models.approval import ApprovalGrant
from app.models.run import PlanRun, StepRun
from app.models.crawled_post import CrawledPost
from app.models.theme_result import ThemeResult
from app.models.health import AccountHealthState, AccountHealthLog
print(f'Models loaded: {len(Base.metadata.tables)} tables')
"
```

Expected: "Models loaded: 9 tables" (hoac 10 neu account_health_state va account_health_log dem rieng).

## Buoc 5 — Viet result.json va gui notification

```json
{
  "cp": "cp1-schema-lock",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "9 tables created via Alembic migration. All models importable. Schema locked.",
  "artifacts": [
    {"file": "backend/app/models/base.py", "action": "created"},
    {"file": "backend/app/models/product_context.py", "action": "created"},
    {"file": "backend/app/models/plan.py", "action": "created"},
    {"file": "backend/app/models/approval.py", "action": "created"},
    {"file": "backend/app/models/run.py", "action": "created"},
    {"file": "backend/app/models/crawled_post.py", "action": "created"},
    {"file": "backend/app/models/theme_result.py", "action": "created"},
    {"file": "backend/app/models/health.py", "action": "created"},
    {"file": "backend/alembic/versions/001_initial_schema.py", "action": "created"}
  ],
  "issues": [],
  "notes": "Schema matches architecture.md Section 4.1 exactly."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp1-schema-lock \
    --role implementer \
    --status READY \
    --summary "Schema locked. 9 tables, all models importable." \
    --result-file docs/phases/phase-1/checkpoints/cp1-schema-lock/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp1-schema-lock/result.json
```
