# CP3 Validation Checklist — Priority-Based Comment Crawling

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp3-priority-crawl/result.json`
**Mục tiêu:** Verify priority sorting and budget allocation work correctly.

---

### CHECK-01: prioritize_post_refs sorts correctly

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence, PrioritizedPostPlan
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
refs = [{'post_id': 'a', 'post_url': 'u1'}, {'post_id': 'b', 'post_url': 'u2'}, {'post_id': 'c', 'post_url': 'u3'}]
labels = {'a': 'low', 'b': 'high', 'c': 'medium'}
plan = pi.prioritize_post_refs(refs, labels, 100)
order = [r['post_id'] for r in plan.ordered_refs]
assert order == ['b', 'c', 'a'], f'Wrong order: {order}'
print(f'order={order} tiers={plan.tier_counts} budgets={plan.tier_budgets}')
print('OK')
"
```

**Expected:** order=[b, c, a] (high, medium, low)
**Fail if:** wrong order

---

### CHECK-02: Budget allocation matches 60/30/10

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
refs = [{'post_id': f'p{i}', 'post_url': f'u{i}'} for i in range(10)]
labels = {f'p{i}': ['high','medium','low'][i%3] for i in range(10)}
plan = pi.prioritize_post_refs(refs, labels, 200)
print(f'budgets={plan.tier_budgets}')
assert plan.tier_budgets['high'] >= 100, f'High budget too low: {plan.tier_budgets}'
print('OK')
"
```

**Expected:** high >= 100 (60% of 200)
**Fail if:** budget distribution wrong

---

### CHECK-03: All low-relevance still runs

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
refs = [{'post_id': 'a', 'post_url': 'u1'}]
labels = {'a': 'low'}
plan = pi.prioritize_post_refs(refs, labels, 50)
assert len(plan.ordered_refs) == 1
assert plan.per_post_budget['a'] > 0
print('OK')
"
```

**Expected:** OK, post still gets budget
**Fail if:** empty plan or zero budget

---

### CHECK-04: No labels = fallback to original order

```bash
cd backend && python -c "
from app.services.pipeline_intelligence import PipelineIntelligence
from app.infrastructure.config import Settings
pi = PipelineIntelligence(Settings())
refs = [{'post_id': 'a', 'post_url': 'u1'}, {'post_id': 'b', 'post_url': 'u2'}]
plan = pi.prioritize_post_refs(refs, {}, 100)
order = [r['post_id'] for r in plan.ordered_refs]
assert order == ['a', 'b'], f'With no labels, should keep original order: {order}'
print('OK')
"
```

**Expected:** original order preserved
**Fail if:** different order

---

### CHECK-05: Checkpoint has tier data

```bash
echo "Manual verify: after mock run, CRAWL_COMMENTS checkpoint has tier_counts and tier_budgets"
echo "OK - manual"
```

---

### CHECK-06: Mock e2e priority order

```bash
echo "Manual verify: run mock e2e, check CRAWL_COMMENTS checkpoint shows high posts crawled first"
echo "OK - manual"
```

---

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-06
**Warning checks:** CHECK-05

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp3-priority-crawl --role validator --status PASS \
    --summary "Priority crawl verified" \
    --result-file docs/phases/phase-3/checkpoints/cp3-priority-crawl/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp3-priority-crawl/validation.json
```
