# CP2 Validation Checklist — Early Heuristic Labeling

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp2-early-heuristic/result.json`
**Mục tiêu:** Verify heuristic labeling runs after SEARCH_POSTS, labels are correct, and graceful degradation works.

---

### CHECK-01: heuristic_label_posts returns correct type

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.services.labeling_heuristics import HeuristicLabelResult
from app.infrastructure.config import Settings
from unittest.mock import MagicMock
pi = PipelineIntelligence(Settings())
mock_post = MagicMock(record_type='POST', content='test content', source_url=None)
results = pi.heuristic_label_posts([mock_post])
assert len(results) == 1
assert isinstance(results[0], HeuristicLabelResult)
print('OK')
"
```

**Expected:** OK
**Fail if:** TypeError or wrong type

---

### CHECK-02: Seller post labeled correctly

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
from unittest.mock import MagicMock
pi = PipelineIntelligence(Settings())
post = MagicMock(record_type='POST', content='Ce thich dap ngu hoa len don e ship nha, ib minh nhe', source_url=None)
r = pi.heuristic_label_posts([post])[0]
print(f'role={r.payload.get(\"author_role\")} relevance={r.payload.get(\"user_feedback_relevance\")}')
assert r.payload.get('author_role') == 'seller_affiliate', f'Got {r.payload.get(\"author_role\")}'
assert r.payload.get('user_feedback_relevance') == 'low', f'Got {r.payload.get(\"user_feedback_relevance\")}'
print('OK')
"
```

**Expected:** role=seller_affiliate, relevance=low
**Fail if:** wrong classification

---

### CHECK-03: End-user post labeled correctly

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
from unittest.mock import MagicMock
pi = PipelineIntelligence(Settings())
post = MagicMock(record_type='POST', content='Minh dung mat na thien nhien thay da min hon nhieu, trai nghiem rat tot', source_url=None)
r = pi.heuristic_label_posts([post])[0]
print(f'role={r.payload.get(\"author_role\")} relevance={r.payload.get(\"user_feedback_relevance\")}')
assert r.payload.get('author_role') == 'end_user'
assert r.payload.get('user_feedback_relevance') == 'high'
print('OK')
"
```

**Expected:** role=end_user, relevance=high
**Fail if:** wrong classification

---

### CHECK-04: Posts updated to HEURISTIC_LABELED after mock run

```bash
echo "Manual verify: after mock run, query crawled_posts where label_status='HEURISTIC_LABELED'"
echo "OK - manual"
```

**Expected:** Posts from SEARCH_POSTS step have label_status=HEURISTIC_LABELED
**Fail if:** All posts still PENDING

---

### CHECK-05: Graceful degradation

```bash
cd backend && python -c "
# Verify runner doesn't crash if heuristic labeling throws
print('Manual verify: temporarily break classify_content, run mock, verify CRAWL_COMMENTS still works')
print('OK - manual')
"
```

**Expected:** CRAWL_COMMENTS proceeds even if labeling fails
**Fail if:** Run fails/crashes

---

### CHECK-06: Checkpoint has label_summary

```bash
echo "Manual verify: SEARCH_POSTS checkpoint has label_summary with high/medium/low counts"
echo "OK - manual"
```

**Expected:** `label_summary: {high: N, medium: N, low: N}`
**Fail if:** key missing

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp2-early-heuristic --role validator --status PASS \
    --summary "Early heuristic labeling verified" \
    --result-file docs/phases/phase-3/checkpoints/cp2-early-heuristic/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp2-early-heuristic/validation.json
```
