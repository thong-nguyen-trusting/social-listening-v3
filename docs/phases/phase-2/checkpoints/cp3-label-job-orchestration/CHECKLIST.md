# CP3 Validation Checklist — Label Job Orchestration

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp3-label-job-orchestration/result.json`
**Muc tieu:** Verify lifecycle rieng cua label jobs.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp3-label-job-orchestration/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP3 — Label Job Orchestration",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Create label job

```bash
curl -s -X POST http://localhost:8000/api/runs/<run_id>/labels/jobs
```

**Expected:** Tra `label_job_id`
**Fail if:** Tao job khong duoc

### CHECK-02: Lifecycle state

```bash
curl -s http://localhost:8000/api/runs/<run_id>/labels/summary
```

**Expected:** Status nam trong `PENDING|RUNNING|DONE|PARTIAL|FAILED`
**Fail if:** State khong hop le

### CHECK-03: Progress counts

```bash
curl -s http://localhost:8000/api/runs/<run_id>/labels/summary | jq
```

**Expected:** Co `records_total`, `records_labeled`, `records_fallback`, `records_failed`
**Fail if:** Thieu field

### CHECK-04: Duplicate guard

```bash
curl -s -X POST http://localhost:8000/api/runs/<run_id>/labels/jobs
```

**Expected:** Bi chan hoac reuse job dang ton tai
**Fail if:** Tao duplicate khong kiem soat

### CHECK-05: Crawl run semantics

```bash
curl -s http://localhost:8000/api/runs/<run_id>
```

**Expected:** `plan_runs.status` khong bi mutate boi labeling
**Fail if:** Labeling lam sai meaning cua crawl run

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
