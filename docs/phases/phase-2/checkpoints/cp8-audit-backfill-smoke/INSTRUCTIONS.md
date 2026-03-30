# CP8 — Audit, Backfill & Smoke

**Muc tieu:** Xac nhan end-to-end cho Phase 2 va co demo log.
**Requires:** CP7 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp8-audit-backfill-smoke/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP8 — Audit, Backfill & Smoke",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Backfill

- Chon it nhat 1 run Phase 1 co data
- Tao label job/backfill va verify labels persist

## Buoc 2 — Audit sample

- Neu implement endpoint sample, expose 1 sample excluded record
- Dam bao UI co the hien labels, confidence, reason

## Buoc 3 — Smoke

- Chay flow end-to-end cho 1 run
- Verify Themes UI co filter va summary excluded

## Buoc 4 — DEMO_LOG va result

- Tao `DEMO_LOG.md`
- Viet `result.json`
- Gui `notify.py` va `post-status.py`
