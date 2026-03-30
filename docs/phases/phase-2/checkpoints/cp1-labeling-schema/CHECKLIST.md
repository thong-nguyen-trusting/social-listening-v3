# CP1 Validation Checklist — Labeling Schema + Migration

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp1-labeling-schema/result.json`
**Muc tieu:** Verify schema Phase 2 da lock dung.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp1-labeling-schema/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP1 — Labeling Schema + Migration",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Alembic upgrade

```bash
cd backend && source venv/bin/activate && alembic upgrade head
```

**Expected:** Exit 0
**Fail if:** Migration fail

### CHECK-02: Tables moi ton tai

```bash
cd backend && sqlite3 app.db ".tables"
```

**Expected:** Co `label_jobs` va `content_labels`
**Fail if:** Thieu table

### CHECK-03: Columns tren crawled_posts

```bash
cd backend && sqlite3 app.db ".schema crawled_posts" | grep -E "label_status|current_label_id"
```

**Expected:** Co 2 column moi
**Fail if:** Khong thay column

### CHECK-04: Constraints taxonomy

```bash
cd backend && sqlite3 app.db ".schema content_labels"
```

**Expected:** Co CHECK constraints cho enums
**Fail if:** Constraint thieu

### CHECK-05: Migration roundtrip

```bash
cd backend && source venv/bin/activate && alembic downgrade -1 && alembic upgrade head
```

**Expected:** Exit 0
**Fail if:** Roundtrip fail

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
