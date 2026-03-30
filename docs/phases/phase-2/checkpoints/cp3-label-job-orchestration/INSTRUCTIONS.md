# CP3 — Label Job Orchestration

**Muc tieu:** Tach lifecycle labeling ra khoi crawl run.
**Requires:** CP1 PASS, CP2 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp3-label-job-orchestration/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP3 — Label Job Orchestration",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Service layer

- Tao `LabelJobService`
- APIs: create/start/get summary/cancel neu can
- Block duplicate job cho cung `run_id + taxonomy_version` khi chua xong

## Buoc 2 — Read model va API

- Tao `/api/runs/{run_id}/labels/summary`
- Neu chua co job thi tra state de UI biet labeling chua bat dau

## Buoc 3 — Event strategy

- Khong doi `plan_runs.status`
- Cho UI doc labeling state tu `label_jobs`

## Buoc 4 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
