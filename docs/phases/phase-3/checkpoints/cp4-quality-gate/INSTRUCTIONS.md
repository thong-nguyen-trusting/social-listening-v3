# CP4 — Group Quality Gate

**Mục tiêu:** Filter SEARCH_IN_GROUP to skip groups with mostly low-quality posts.
**Requires:** CP1 PASS (group scoring), CP2 PASS (heuristic labels)

---

## Bước 1 — Implement `quality_gate_groups()`

File: `backend/app/services/pipeline_intelligence.py`

```python
@dataclass
class GroupQualityDetail:
    group_id: str
    post_count: int
    high_count: int
    medium_count: int
    low_count: int
    quality_ratio: float
    passed: bool
    skip_reason: str | None

@dataclass
class GroupQualityReport:
    passed_group_ids: list[str]
    skipped_group_ids: list[str]
    details: dict[str, GroupQualityDetail]
```

Logic:
1. For each group_id, find posts in run where `group_id_hash = hash(group_id)`
2. Count by `user_feedback_relevance` from `label_map`
3. `quality_ratio = (high + medium) / max(total, 1)`
4. If `total == 1` → always pass (benefit of doubt)
5. If `quality_ratio < (1 - self._group_quality_threshold)` → skip
6. Return GroupQualityReport

## Bước 2 — Runner: interceptor trong SEARCH_IN_GROUP

Before iterating group_ids:
1. Load label_map
2. Call `quality_gate_groups(group_ids, posts, label_map, group_id_resolver)`
3. Replace group_ids with passed_group_ids
4. Add quality report to checkpoint

## Bước 3 — Verify + result.json

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp4-quality-gate --role implementer --status READY \
    --summary "Group quality gate for SEARCH_IN_GROUP" \
    --result-file docs/phases/phase-3/checkpoints/cp4-quality-gate/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp4-quality-gate/result.json
```
