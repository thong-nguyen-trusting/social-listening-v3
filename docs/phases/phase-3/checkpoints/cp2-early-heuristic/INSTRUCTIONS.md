# CP2 — Early Heuristic Labeling

**Mục tiêu:** Run heuristic labeling immediately after SEARCH_POSTS persist, before CRAWL_COMMENTS.
**Requires:** CP0 PASS — PipelineIntelligence skeleton, HEURISTIC_LABELED status

---

## Bước 1 — Implement `heuristic_label_posts()`

File: `backend/app/services/pipeline_intelligence.py`

```python
from app.services.labeling_heuristics import classify_content, HeuristicLabelResult

def heuristic_label_posts(self, posts: list) -> list[HeuristicLabelResult]:
    results = []
    for post in posts:
        result = classify_content(
            record_type=getattr(post, 'record_type', 'POST'),
            content=getattr(post, 'content', ''),
            parent_summary=None,
            source_url=getattr(post, 'source_url', None),
        )
        results.append(result)
    return results
```

## Bước 2 — Runner: interceptor sau SEARCH_POSTS

After `_persist_posts()` in SEARCH_POSTS handler:

1. Load persisted posts from DB (by run_id + step_run_id)
2. Call `self._pipeline_intel.heuristic_label_posts(posts)`
3. For each post + label result:
   - Create `ContentLabel` record with `label_source="heuristic"`
   - Update `post.current_label_id` và `post.label_status = "HEURISTIC_LABELED"`
4. Commit
5. Build `label_summary = {"high": N, "medium": N, "low": N}` from results
6. Add `label_summary` to checkpoint

Add helper method `_apply_heuristic_label(session, post, label_result)` to runner.

## Bước 3 — Graceful degradation

Wrap the entire heuristic block in try/except. On failure:
- Log warning
- Posts remain `label_status=PENDING`
- CRAWL_COMMENTS proceeds without priority info

## Bước 4 — Verify + result.json

```bash
python -c "import ast; ast.parse(open('backend/app/services/pipeline_intelligence.py').read()); print('OK')"
python -c "import ast; ast.parse(open('backend/app/services/runner.py').read()); print('OK')"
```

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp2-early-heuristic --role implementer --status READY \
    --summary "Early heuristic labeling after SEARCH_POSTS with graceful degradation" \
    --result-file docs/phases/phase-3/checkpoints/cp2-early-heuristic/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp2-early-heuristic/result.json
```
