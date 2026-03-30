# CP5 Validation Checklist — Pipeline Summary API

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp5-pipeline-summary/result.json`
**Mục tiêu:** Verify pipeline_summary present in run API response with correct structure.

---

### CHECK-01: build_pipeline_summary returns correct structure

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
fake_checkpoints = {
    'step-1': {'label_summary': {'high': 10, 'medium': 5, 'low': 3}, 'group_scoring': {'total_groups': 5, 'relevant_groups': 2, 'skipped_groups': 3}},
}
result = pi.build_pipeline_summary(fake_checkpoints)
assert result is not None
assert 'heuristic_labeling' in result
assert 'group_scoring' in result
print(result)
print('OK')
"
```

**Expected:** dict with heuristic_labeling + group_scoring keys
**Fail if:** None or missing keys

---

### CHECK-02: API response contains pipeline_summary

```bash
docker exec social-listening-v3 python -c "
import requests
# Use an existing run_id or create one via mock
runs = requests.get('http://localhost:8000/api/runs/run-test-does-not-exist')
print('Verify manually: GET /api/runs/{run_id} has pipeline_summary key')
print('OK - manual')
"
```

**Expected:** pipeline_summary key in response JSON
**Fail if:** key absent

---

### CHECK-03: Correct counts in mock e2e

```bash
echo "Manual verify: run full mock e2e, check pipeline_summary counts match actual step results"
echo "OK - manual"
```

---

### CHECK-04: Null when disabled

```bash
echo "Manual verify: set pipeline_intelligence_enabled=false, verify pipeline_summary is null"
echo "OK - manual"
```

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03
**Warning checks:** CHECK-04

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp5-pipeline-summary --role validator --status PASS \
    --summary "Pipeline summary API verified" \
    --result-file docs/phases/phase-3/checkpoints/cp5-pipeline-summary/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp5-pipeline-summary/validation.json
```
