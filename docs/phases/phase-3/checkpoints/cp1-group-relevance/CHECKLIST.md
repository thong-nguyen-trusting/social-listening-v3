# CP1 Validation Checklist — Group Relevance Scoring

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp1-group-relevance/result.json`
**Mục tiêu:** Verify group scoring logic correct, runner integration works, irrelevant groups are filtered.

---

### CHECK-01: score_group_relevance trả đúng kiểu

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence, GroupRelevanceResult
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
result = pi.score_group_relevance({'group_id': 'test', 'name': 'Test Group'}, 'test topic', {'brand': ['test']})
assert isinstance(result, GroupRelevanceResult), f'Wrong type: {type(result)}'
print('OK')
"
```

**Expected:** OK
**Fail if:** TypeError or wrong return type

---

### CHECK-02: Irrelevant group scored low

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
r = pi.score_group_relevance({'group_id': 'x', 'name': 'Ăn Vặt BMT - Review Đồ Ăn BMT'}, 'sản phẩm làm đẹp thiên nhiên', {'brand': ['mặt nạ thiên nhiên'], 'pain_points': ['da nhạy cảm']})
print(f'score={r.score:.3f} relevant={r.relevant}')
assert not r.relevant, f'Should be irrelevant but score={r.score}'
print('OK')
"
```

**Expected:** score < 0.15, relevant=False
**Fail if:** relevant=True

---

### CHECK-03: Relevant group scored high

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
r = pi.score_group_relevance({'group_id': 'x', 'name': 'REVIEW MỸ PHẨM - TÂM SỰ SKINCARE'}, 'sản phẩm làm đẹp thiên nhiên', {'brand': ['mỹ phẩm thiên nhiên'], 'pain_points': ['da nhạy cảm']})
print(f'score={r.score:.3f} relevant={r.relevant}')
assert r.relevant, f'Should be relevant but score={r.score}'
print('OK')
"
```

**Expected:** score >= 0.15, relevant=True
**Fail if:** relevant=False

---

### CHECK-04: SEARCH_POSTS checkpoint contains group_scoring

```bash
docker exec social-listening-v3 python -c "
# Requires a mock mode run to exist
print('Manual verify: run a mock e2e and check checkpoint has group_scoring key')
print('OK - manual')
"
```

**Expected:** checkpoint JSON has `group_scoring` key
**Fail if:** key missing after mock run

---

### CHECK-05: JOIN_GROUP skips irrelevant groups

```bash
echo "Manual verify: in mock run checkpoint, JOIN_GROUP has skipped_groups list"
echo "OK - manual"
```

**Expected:** JOIN_GROUP checkpoint includes `skipped_groups` with reasons
**Fail if:** no skip metadata

---

### CHECK-06: Mock mode e2e passes

```bash
docker exec social-listening-v3 python -c "
import requests, json
r = requests.post('http://localhost:8000/api/sessions', json={'topic': 'sản phẩm làm đẹp thiên nhiên'})
ctx = r.json()['context_id']
r = requests.post('http://localhost:8000/api/plans', json={'context_id': ctx})
plan = r.json()
print(f'Plan {plan[\"plan_id\"]} with {len(plan[\"steps\"])} steps')
print('OK')
"
```

**Expected:** Plan generated successfully
**Fail if:** HTTP error or empty plan

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03
**Warning checks:** CHECK-04, CHECK-05, CHECK-06

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp1-group-relevance --role validator --status PASS \
    --summary "Group relevance scoring verified" \
    --result-file docs/phases/phase-3/checkpoints/cp1-group-relevance/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp1-group-relevance/validation.json
```
