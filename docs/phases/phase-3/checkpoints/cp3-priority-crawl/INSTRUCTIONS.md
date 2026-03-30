# CP3 — Priority-Based Comment Crawling

**Mục tiêu:** CRAWL_COMMENTS crawls high-relevance posts first, allocates budget per tier.
**Requires:** CP2 PASS — heuristic labels available on posts

---

## Bước 1 — Implement `prioritize_post_refs()`

File: `backend/app/services/pipeline_intelligence.py`

```python
@dataclass
class PrioritizedPostPlan:
    ordered_refs: list[dict]
    per_post_budget: dict[str, int]
    tier_counts: dict[str, int]
    tier_budgets: dict[str, int]

def prioritize_post_refs(
    self,
    post_refs: list[dict],
    label_map: dict[str, str],  # {post_id: user_feedback_relevance}
    total_budget: int,
) -> PrioritizedPostPlan:
```

Logic:
1. Partition by `label_map.get(ref["post_id"], "medium")` → tier_high, tier_medium, tier_low
2. ordered = tier_high + tier_medium + tier_low
3. Budget: high_budget = int(total * 0.6), medium = int(total * 0.3), low = total - high - medium
4. Per-post: tier_budget / max(len(tier), 1), minimum 1
5. Return PrioritizedPostPlan

## Bước 2 — Runner: add `_load_label_map()`

Helper reads ContentLabel records for run, returns `{post_id: user_feedback_relevance}`.

```python
def _load_label_map(self, run_id: str) -> dict[str, str]:
    with SessionLocal() as session:
        posts = session.scalars(
            select(CrawledPost).where(CrawledPost.run_id == run_id)
        ).all()
        labels = {}
        for post in posts:
            if post.current_label_id:
                label = session.get(ContentLabel, post.current_label_id)
                if label:
                    labels[post.post_id] = label.user_feedback_relevance
        return labels
```

## Bước 3 — Modify CRAWL_COMMENTS handler

Replace flat iteration with priority-based:

```python
post_refs = self._resolve_post_refs(run_id, step)

if self._pipeline_intel and self._pipeline_intel._enabled:
    label_map = self._load_label_map(run_id)
    priority = self._pipeline_intel.prioritize_post_refs(
        post_refs, label_map, step.estimated_count or 200
    )
    post_refs = priority.ordered_refs
    per_post_budget = priority.per_post_budget
else:
    per_post_budget = {}

for post_ref in post_refs:
    budget = per_post_budget.get(post_ref["post_id"], per_post_limit)
    comments = await self._browser_agent.crawl_comments(
        post_ref["post_url"], target_count=budget, ...
    )
```

## Bước 4 — Verify + result.json

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp3-priority-crawl --role implementer --status READY \
    --summary "Priority-based comment crawling: high→medium→low with 60/30/10 budget" \
    --result-file docs/phases/phase-3/checkpoints/cp3-priority-crawl/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp3-priority-crawl/result.json
```
