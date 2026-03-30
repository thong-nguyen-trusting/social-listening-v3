# CP7 Validation Checklist — E2E Smoke Test

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp7-smoke-test/result.json`
**Mục tiêu:** Verify full Phase 3 pipeline works end-to-end.

---

### CHECK-01: Mock e2e run completes DONE

```bash
docker exec social-listening-v3 python -c "
import requests
# Check most recent run status
print('Manual: verify latest mock run has status=DONE')
print('OK - manual')
"
```

**Expected:** Run status = DONE
**Fail if:** FAILED or CANCELLED

---

### CHECK-02: pipeline_summary present with data

```bash
echo "Manual: GET /api/runs/{run_id} has pipeline_summary with non-null values"
echo "OK - manual"
```

**Expected:** pipeline_summary is not null, has heuristic_labeling + group_scoring
**Fail if:** null or empty

---

### CHECK-03: Groups were filtered

```bash
echo "Manual: pipeline_summary.group_scoring.skipped > 0"
echo "OK - manual"
```

**Expected:** At least 1 group skipped
**Fail if:** skipped = 0 (all groups passed)

---

### CHECK-04: Priority tiers in CRAWL_COMMENTS

```bash
echo "Manual: CRAWL_COMMENTS checkpoint has tier_counts with high > 0"
echo "OK - manual"
```

**Expected:** tier_counts present, high > 0
**Fail if:** No tier data

---

### CHECK-05: Dashboard funnel visible

```bash
echo "Manual: open MonitorPage at http://localhost:8000, connect to run, verify funnel displays"
echo "OK - manual"
```

**Expected:** Pipeline Intelligence section visible with bars
**Fail if:** Section missing or broken

---

### CHECK-06: Feature flag rollback

```bash
echo "Manual: set PIPELINE_INTELLIGENCE_ENABLED=false, restart, verify run works without pipeline_summary"
echo "OK - manual"
```

**Expected:** Run completes, pipeline_summary = null
**Fail if:** Run fails

---

### CHECK-07: Real browser test

```bash
echo "Optional: run with real Facebook session, verify group names and quality gate"
echo "OK - optional"
```

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp7-smoke-test --role validator --status PASS \
    --summary "Phase 3 E2E smoke test passed" \
    --result-file docs/phases/phase-3/checkpoints/cp7-smoke-test/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp7-smoke-test/validation.json
```
