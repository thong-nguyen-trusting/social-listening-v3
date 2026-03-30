# CP6 — Monitor Labeling UI

**Muc tieu:** Hien lifecycle labeling trong Monitor mot cach tach biet va de hieu.
**Requires:** CP3 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp6-monitor-labeling-ui/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP6 — Monitor Labeling UI",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Label summary fetch

- Goi `/api/runs/{run_id}/labels/summary`
- Reuse state sharing giua Monitor va cac pages khac neu can

## Buoc 2 — UI section

- Hien status
- Hien counts
- Hien note khi labeling chua xong
- Co loading/error states

## Buoc 3 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
