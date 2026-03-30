# CP1 — Group Relevance Scoring

**Mục tiêu:** Score discovered groups by topic relevance, filter irrelevant groups from JOIN_GROUP + SEARCH_IN_GROUP.
**Requires:** CP0 PASS — text_utils.py, PipelineIntelligence skeleton, settings

---

## Bước 1 — Implement `score_group_relevance()` và `score_groups()`

File: `backend/app/services/pipeline_intelligence.py`

Thêm dataclasses và methods:

```python
@dataclass
class GroupRelevanceResult:
    group_id: str
    name: str
    score: float
    relevant: bool
    matched_tokens: list[str]
    skip_reason: str | None

@dataclass
class GroupScoringReport:
    total_groups: int
    relevant_groups: int
    skipped_groups: int
    details: list[GroupRelevanceResult]
```

`score_group_relevance(group, topic, keywords)`:
1. `topic_tokens = tokenize_vn(topic) | {token for kw_list in keywords.values() for kw in kw_list for token in tokenize_vn(kw)}`
2. `group_tokens = tokenize_vn(group["name"])`
3. `matched = topic_tokens & group_tokens`
4. `score = len(matched) / max(len(topic_tokens), 1)`
5. Return result with `relevant = score >= self._group_relevance_threshold`

`score_groups(groups, topic, keywords)` → loops and returns `GroupScoringReport`.

## Bước 2 — Runner: inject PipelineIntelligence

Trong `RunnerService.__init__`, accept optional `pipeline_intel: PipelineIntelligence | None`.

Thêm helper `_load_topic_keywords(run_id)` → đọc ProductContext từ DB, trả (topic, keywords dict).

## Bước 3 — Runner: interceptor sau SEARCH_POSTS

Sau `_persist_posts()` trong SEARCH_POSTS handler, thêm:
- Call `score_groups()` trên `result["discovered_groups"]`
- Lưu `group_scoring` vào checkpoint
- Filter `discovered_groups` trong checkpoint — chỉ giữ relevant groups
- Giữ `discovered_groups_all` cho audit

## Bước 4 — Runner: filter trong JOIN_GROUP

Trước khi iterate `group_ids` trong JOIN_GROUP handler:
- Load cached group scoring từ SEARCH_POSTS checkpoint
- Filter out groups có `relevant=false`
- Log skipped groups trong checkpoint

## Bước 5 — Verify + result.json

```bash
python -c "import ast; ast.parse(open('backend/app/services/pipeline_intelligence.py').read()); print('OK')"
python -c "import ast; ast.parse(open('backend/app/services/runner.py').read()); print('OK')"
```

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp1-group-relevance --role implementer --status READY \
    --summary "Group relevance scoring + runner interceptors for JOIN_GROUP/SEARCH_IN_GROUP" \
    --result-file docs/phases/phase-3/checkpoints/cp1-group-relevance/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp1-group-relevance/result.json
```
