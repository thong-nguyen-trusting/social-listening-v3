# CP4 — Content Labeling Engine

**Muc tieu:** Gan labels cho records da crawl bang engine hybrid.
**Requires:** CP3 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp4-content-labeling-engine/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP4 — Content Labeling Engine",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Batch selection

- Lay records `label_status=PENDING`
- Gom batch 20-50 records
- Dua vao prompt voi metadata an toan

## Buoc 2 — Hybrid classification

- Heuristic pre-pass
- AI adjudication cho cases ambiguous
- Safe fallback khi parse/model fail

## Buoc 3 — Persist labels

- Ghi vao `content_labels`
- Cap nhat `current_label_id`, `label_status`
- Cap nhat counters tren `label_job`

## Buoc 4 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
