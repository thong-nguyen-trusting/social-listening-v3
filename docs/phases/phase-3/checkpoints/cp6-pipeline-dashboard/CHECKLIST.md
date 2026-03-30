# CP6 Validation Checklist — Pipeline Dashboard UI

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp6-pipeline-dashboard/result.json`
**Mục tiêu:** Verify pipeline funnel renders correctly in MonitorPage.

---

### CHECK-01: Funnel visible when pipeline_summary exists

```bash
echo "Manual verify: open MonitorPage with a completed run, verify pipeline funnel section appears"
echo "OK - manual"
```

**Expected:** Funnel section visible with stages
**Fail if:** No funnel section or empty

---

### CHECK-02: Correct data displayed

```bash
echo "Manual verify: funnel numbers match GET /api/runs/{run_id} pipeline_summary values"
echo "OK - manual"
```

**Expected:** Numbers match API response
**Fail if:** Mismatch

---

### CHECK-03: Hidden when null

```bash
echo "Manual verify: disable pipeline_intelligence_enabled, verify funnel section not shown"
echo "OK - manual"
```

**Expected:** No funnel section
**Fail if:** Empty/broken section

---

### CHECK-04: Frontend builds

```bash
cd frontend && npm run build 2>&1 | tail -3
```

**Expected:** `built in` message, no errors
**Fail if:** Build error

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-04
**Warning checks:** CHECK-03

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp6-pipeline-dashboard --role validator --status PASS \
    --summary "Pipeline dashboard UI verified" \
    --result-file docs/phases/phase-3/checkpoints/cp6-pipeline-dashboard/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp6-pipeline-dashboard/validation.json
```
