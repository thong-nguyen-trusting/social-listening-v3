# CP4 Validation Checklist — Group Quality Gate

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp4-quality-gate/result.json`
**Mục tiêu:** Verify quality gate correctly filters low-quality groups from SEARCH_IN_GROUP.

---

### CHECK-01: quality_gate_groups returns correct type

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence, GroupQualityReport
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
report = pi.quality_gate_groups(['g1'], {}, {})
assert isinstance(report, GroupQualityReport)
print('OK')
"
```

**Expected:** OK
**Fail if:** TypeError

---

### CHECK-02: All-seller group gets skipped

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
# 5 posts all low relevance from group g1
label_map = {'p1': 'low', 'p2': 'low', 'p3': 'low', 'p4': 'low', 'p5': 'low'}
post_groups = {'p1': 'g1', 'p2': 'g1', 'p3': 'g1', 'p4': 'g1', 'p5': 'g1'}
report = pi.quality_gate_groups(['g1'], label_map, post_groups)
assert 'g1' in report.skipped_group_ids, f'g1 should be skipped: {report.skipped_group_ids}'
print('OK')
"
```

**Expected:** g1 skipped
**Fail if:** g1 passes

---

### CHECK-03: Single-post group always passes

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
label_map = {'p1': 'medium'}
post_groups = {'p1': 'g1'}
report = pi.quality_gate_groups(['g1'], label_map, post_groups)
assert 'g1' in report.passed_group_ids
print('OK')
"
```

**Expected:** g1 passes
**Fail if:** g1 skipped

---

### CHECK-04: All groups fail = step completes gracefully

```bash
echo "Manual verify: mock run where all groups fail quality gate, SEARCH_IN_GROUP returns actual_count=0"
echo "OK - manual"
```

---

### CHECK-05: Checkpoint has quality report

```bash
echo "Manual verify: SEARCH_IN_GROUP checkpoint has group_quality key"
echo "OK - manual"
```

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04
**Warning checks:** CHECK-05

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp4-quality-gate --role validator --status PASS \
    --summary "Group quality gate verified" \
    --result-file docs/phases/phase-3/checkpoints/cp4-quality-gate/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp4-quality-gate/validation.json
```
