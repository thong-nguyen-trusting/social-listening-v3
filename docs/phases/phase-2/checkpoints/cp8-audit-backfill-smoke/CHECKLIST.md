# CP8 Validation Checklist — Audit, Backfill & Smoke

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp8-audit-backfill-smoke/result.json`
**Muc tieu:** Verify Phase 2 co the demo tren run that va co trust layer day du.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp8-audit-backfill-smoke/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP8 — Audit, Backfill & Smoke",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: End-to-end flow

```bash
python3 backend/tests/labeling_smoke.py
```

**Expected:** Exit 0 va co labels + filtered themes
**Fail if:** Smoke fail

### CHECK-02: Backfill

```bash
sqlite3 backend/app.db "select count(*) from label_jobs;"
```

**Expected:** Co it nhat 1 label job cho run cu
**Fail if:** Khong backfill duoc

### CHECK-03: Audit sample

```bash
curl -s "http://localhost:8000/api/runs/<run_id>/records?label_filter=seller_affiliate&limit=1"
```

**Expected:** Tra sample co labels/reason hoac docs neu endpoint optional
**Fail if:** Khong co cach audit exclusion

### CHECK-04: Server stability

```bash
grep -iE "traceback|unhandled|500" /tmp/social-listening-server.log || true
```

**Expected:** Khong co unhandled exception moi
**Fail if:** Co crash nghiem trong

### CHECK-05: Demo log

```bash
head -20 docs/phases/phase-2/checkpoints/cp8-audit-backfill-smoke/DEMO_LOG.md
```

**Expected:** Log mo ta run, labels, filters, excluded summary
**Fail if:** Demo log trong hoac thieu ket qua

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
