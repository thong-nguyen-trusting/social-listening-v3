# Architecture — Phase 3: Smart Crawl Pipeline

**Updated:** 2026-03-29

---

## 1. Problem Statement

Current pipeline executes steps blindly: SEARCH_POSTS → CRAWL_COMMENTS → JOIN_GROUP → SEARCH_IN_GROUP. Every discovered post gets equal crawl budget, every discovered group gets joined and searched. Production run `run-802cb7073a` showed:

- 30% posts = seller spam, 26% = off-topic, only 44% relevant
- 16/19 discovered groups irrelevant
- ~10 minutes wasted crawling comments on spam posts

Phase 3 adds **inline intelligence** between existing steps — no new action types, no schema changes, just smarter orchestration inside `RunnerService`.

---

## 2. Architecture Principle: Interceptors, Not New Steps

Phase 3 does **not** add new `action_type` values or new plan steps. Instead it adds **interceptors** — logic that runs inside the runner between persist and the next step's execution.

```
SEARCH_POSTS
     │
     ├── persist posts (existing)
     ├── ► INTERCEPTOR: heuristic_label_posts()     ← US-31
     ├── ► INTERCEPTOR: score_groups()               ← US-30
     │
CRAWL_COMMENTS
     │
     ├── ► INTERCEPTOR: prioritize_post_refs()       ← US-32
     ├── crawl in priority order (modified existing)
     │
JOIN_GROUP
     │
     ├── ► INTERCEPTOR: filter_irrelevant_groups()   ← US-30
     │
SEARCH_IN_GROUP
     │
     ├── ► INTERCEPTOR: quality_gate_groups()         ← US-34
     │
ALL STEPS
     │
     └── ► checkpoint enrichment: pipeline_summary    ← US-33
```

**Why interceptors, not new steps:**
- No migration needed (no new action types in DB constraint)
- No plan generation prompt changes needed
- Backward compatible — interceptors are no-ops when disabled
- No extra AI calls (R-31)

---

## 3. New Module: `pipeline_intelligence.py`

All Phase 3 logic lives in one new file. Runner delegates to it. Clean separation.

### File: `backend/app/services/pipeline_intelligence.py`

```python
class PipelineIntelligence:
    """Inline intelligence for the crawl pipeline.

    Stateless service — receives data, returns decisions.
    No DB access, no AI calls, no side effects.
    """

    def __init__(self, settings: Settings) -> None:
        self._group_relevance_threshold: float = settings.group_relevance_threshold
        self._group_quality_threshold: float = settings.group_quality_threshold
        self._priority_budget_ratio: tuple[float, float, float] = (0.6, 0.3, 0.1)
```

### 3A. Group Relevance Scoring (US-30)

```python
def score_group_relevance(
    self,
    group: dict,           # {group_id, name, privacy, ...}
    topic: str,            # from ProductContext
    keywords: dict,        # flattened keyword map
) -> GroupRelevanceResult:
    """Score a group by token overlap between group name and topic+keywords."""
```

**Algorithm:**
1. Normalize both sides: strip diacritics, lowercase, tokenize
2. Build `topic_tokens` = tokens from topic + all keyword values (flattened, deduped)
3. Build `group_tokens` = tokens from `group.name`
4. `score = len(topic_tokens & group_tokens) / max(len(topic_tokens), 1)`
5. Return `GroupRelevanceResult(group_id, score, relevant=score >= threshold)`

**Data structures:**

```python
@dataclass
class GroupRelevanceResult:
    group_id: str
    name: str
    score: float           # 0.0 – 1.0
    relevant: bool         # score >= threshold
    matched_tokens: list[str]
    skip_reason: str | None  # "low_group_relevance" or None

@dataclass
class GroupScoringReport:
    total_groups: int
    relevant_groups: int
    skipped_groups: int
    details: list[GroupRelevanceResult]
```

**Vietnamese diacritics handling:** Reuse `_strip_diacritics()` from `AIClient` or extract to a shared `text_utils.py`:
```python
def strip_diacritics(text: str) -> str: ...
def tokenize_vn(text: str) -> set[str]: ...
```

### 3B. Early Heuristic Labeling (US-31)

```python
def heuristic_label_posts(
    self,
    posts: list[CrawledPost],
) -> list[HeuristicLabelResult]:
    """Run labeling_heuristics.classify_content() on each post."""
```

This is a thin wrapper around existing `classify_content()`. No new logic — just calls it at a different time.

**Integration point:** After `_persist_posts()` in SEARCH_POSTS handler, before returning the checkpoint.

### 3C. Post Priority Sorting (US-32)

```python
def prioritize_post_refs(
    self,
    post_refs: list[dict],    # [{post_id, post_url, source_group_id}]
    label_map: dict[str, str], # {post_id: user_feedback_relevance}
    total_budget: int,
) -> PrioritizedPostPlan:
    """Sort post_refs by relevance tier, allocate comment budget per tier."""
```

**Algorithm:**
1. Partition `post_refs` into 3 tiers by `user_feedback_relevance`:
   - tier_high = relevance "high"
   - tier_medium = relevance "medium" or missing
   - tier_low = relevance "low"
2. Concatenate: `ordered = tier_high + tier_medium + tier_low`
3. Allocate budget: high gets 60%, medium gets 30%, low gets 10%
4. Per-post budget = tier_budget / len(tier) (minimum 1)

```python
@dataclass
class PrioritizedPostPlan:
    ordered_refs: list[dict]       # post_refs sorted by priority
    per_post_budget: dict[str, int] # {post_id: comment_limit}
    tier_counts: dict[str, int]    # {"high": 20, "medium": 15, "low": 15}
    tier_budgets: dict[str, int]   # {"high": 120, "medium": 60, "low": 20}
```

### 3D. Group Quality Gate (US-34)

```python
def quality_gate_groups(
    self,
    group_ids: list[str],
    posts: list[CrawledPost],      # posts from this run
    label_map: dict[str, str],     # {post_id: user_feedback_relevance}
    group_id_resolver: Callable,   # maps post.group_id_hash → group_id
) -> GroupQualityReport:
    """Filter groups where >70% of posts are low relevance."""
```

**Algorithm:**
1. For each group_id, count posts by relevance tier
2. If `low_count / total > quality_threshold` → mark as `low_quality_source`
3. Groups with only 1 post → always include (benefit of doubt)

```python
@dataclass
class GroupQualityReport:
    passed_group_ids: list[str]
    skipped_group_ids: list[str]
    details: dict[str, GroupQualityDetail]

@dataclass
class GroupQualityDetail:
    group_id: str
    post_count: int
    high_count: int
    medium_count: int
    low_count: int
    quality_ratio: float   # (high + medium) / total
    passed: bool
    skip_reason: str | None
```

### 3E. Pipeline Summary Builder (US-33)

```python
def build_pipeline_summary(
    self,
    group_scoring: GroupScoringReport | None,
    label_summary: dict[str, int],          # {relevance: count}
    priority_plan: PrioritizedPostPlan | None,
    group_quality: GroupQualityReport | None,
    comment_result: dict | None,
) -> dict:
    """Assemble the funnel summary for the run response."""
```

Returns:
```json
{
  "search_posts": {"total": 50},
  "heuristic_labeling": {"high": 22, "medium": 13, "low": 15},
  "group_scoring": {"total": 19, "relevant": 3, "skipped": 16},
  "comment_crawl": {"from_high": 120, "from_medium": 40, "from_low": 5, "skipped_budget": 35},
  "group_quality_gate": {"passed": 2, "skipped": 1},
  "search_in_group": {"groups_searched": 2, "posts_found": 18}
}
```

---

## 4. Runner Integration Points

### 4A. SEARCH_POSTS handler (runner.py ~line 469)

**After** `_persist_posts()`, **before** returning checkpoint:

```python
# --- Phase 3: Early heuristic labeling (US-31) ---
if self._pipeline_intel:
    with SessionLocal() as session:
        db_posts = session.scalars(
            select(CrawledPost).where(
                CrawledPost.run_id == run_id,
                CrawledPost.step_run_id == step_run.step_run_id,
            )
        ).all()
        label_results = self._pipeline_intel.heuristic_label_posts(db_posts)
        for post, label_result in zip(db_posts, label_results):
            self._apply_heuristic_label(session, post, label_result)
        session.commit()

# --- Phase 3: Group relevance scoring (US-30) ---
if self._pipeline_intel:
    topic, keywords = self._load_topic_keywords(run_id)
    group_scoring = self._pipeline_intel.score_groups(
        result["discovered_groups"], topic, keywords
    )
    # Enrich checkpoint with scoring
    checkpoint["group_scoring"] = asdict(group_scoring)
    # Filter discovered_groups in checkpoint to only relevant ones
    checkpoint["discovered_groups_all"] = checkpoint["discovered_groups"]
    checkpoint["discovered_groups"] = [
        g for g, r in zip(result["discovered_groups"], group_scoring.details)
        if r.relevant
    ]
```

### 4B. CRAWL_COMMENTS handler (runner.py ~line 519)

**Replace** `_resolve_post_refs()` flat iteration with priority-sorted iteration:

```python
post_refs = self._resolve_post_refs(run_id, step)

# --- Phase 3: Priority-based crawling (US-32) ---
if self._pipeline_intel:
    label_map = self._load_label_map(run_id)
    priority_plan = self._pipeline_intel.prioritize_post_refs(
        post_refs, label_map, step.estimated_count or 200
    )
    post_refs = priority_plan.ordered_refs
    per_post_budget = priority_plan.per_post_budget
else:
    per_post_budget = None

for post_ref in post_refs:
    budget = (per_post_budget or {}).get(post_ref["post_id"], per_post_limit)
    comments = await self._browser_agent.crawl_comments(
        post_ref["post_url"],
        target_count=budget,
        ...
    )
```

### 4C. JOIN_GROUP handler (runner.py ~line 406)

**Before** iterating group_ids:

```python
group_ids = self._resolve_private_group_ids(run_id, step)

# --- Phase 3: Skip irrelevant groups (US-30) ---
if self._pipeline_intel:
    scoring = self._get_cached_group_scoring(run_id)
    if scoring:
        relevant_ids = {r.group_id for r in scoring.details if r.relevant}
        skipped = [g for g in group_ids if g not in relevant_ids]
        group_ids = [g for g in group_ids if g in relevant_ids]
        # Log skipped groups in checkpoint
```

### 4D. SEARCH_IN_GROUP handler (runner.py ~line 549)

**Before** iterating group_ids:

```python
group_ids = self._resolve_discovered_group_ids(run_id, step)

# --- Phase 3: Group quality gate (US-34) ---
if self._pipeline_intel:
    label_map = self._load_label_map(run_id)
    quality_report = self._pipeline_intel.quality_gate_groups(
        group_ids, posts, label_map, ...
    )
    skipped = quality_report.skipped_group_ids
    group_ids = quality_report.passed_group_ids
```

---

## 5. Settings & Configuration

### File: `backend/app/infrastructure/config.py`

Add to `Settings`:

```python
# Phase 3: Smart Pipeline
group_relevance_threshold: float = 0.15      # US-30: min token overlap score
group_quality_threshold: float = 0.70        # US-34: max % low-relevance posts
priority_budget_high: float = 0.60           # US-32: % budget for high tier
priority_budget_medium: float = 0.30         # US-32: % budget for medium tier
priority_budget_low: float = 0.10            # US-32: % budget for low tier
pipeline_intelligence_enabled: bool = True   # Feature flag to disable Phase 3
```

**Feature flag** `pipeline_intelligence_enabled` allows instant rollback without code change.

---

## 6. Database Changes

### No new tables needed.

Phase 3 stores all intelligence data in **existing structures**:

| Data | Storage | Location |
|------|---------|----------|
| Heuristic labels | `content_labels` table | Via existing `_persist_label()` in ContentLabelingService |
| Group relevance scores | Step checkpoint JSON | `checkpoint.group_scoring` |
| Priority plan | Step checkpoint JSON | `checkpoint.priority_plan` |
| Group quality report | Step checkpoint JSON | `checkpoint.group_quality` |
| Pipeline summary | Run-level aggregation | Computed from step checkpoints at read time |

### Label status extension

Add `HEURISTIC_LABELED` to `label_status` check constraint on `crawled_posts`:

```python
# Migration 007_add_heuristic_labeled_status.py
OLD = "label_status IN ('PENDING','LABELED','FALLBACK','FAILED')"
NEW = "label_status IN ('PENDING','HEURISTIC_LABELED','LABELED','FALLBACK','FAILED')"
```

Also add to `label_taxonomy.py`:
```python
LABEL_RECORD_STATUSES = ("PENDING", "HEURISTIC_LABELED", "LABELED", "FALLBACK", "FAILED")
```

When Phase 2 full labeling runs later, `HEURISTIC_LABELED` → `LABELED` (AI overwrites heuristic).

---

## 7. Shared Utility: `text_utils.py`

### File: `backend/app/infra/text_utils.py`

Extract Vietnamese text processing used by multiple modules:

```python
def strip_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics: ắ→a, đ→d, etc."""

def tokenize_vn(text: str) -> set[str]:
    """Lowercase, strip diacritics, split on non-alphanumeric, dedupe."""

def token_overlap_score(text_a: str, text_b: str) -> float:
    """Jaccard-like overlap: |A ∩ B| / max(|A|, 1)."""
```

Currently `_strip_diacritics()` exists in `AIClient` (line 300+). Extract to shared utility.

---

## 8. API Changes

### `GET /api/runs/{run_id}` response enrichment

Add `pipeline_summary` to run response (computed at read time from checkpoints):

```python
# In RunnerService.get_run()
pipeline_summary = self._build_pipeline_summary_from_checkpoints(step_checkpoints)
```

```json
{
  "run_id": "run-802cb7073a",
  "status": "DONE",
  "pipeline_summary": {
    "search_posts": {"total": 50},
    "heuristic_labeling": {"high": 22, "medium": 13, "low": 15},
    "group_scoring": {"total": 19, "relevant": 3, "skipped": 16},
    "comment_crawl": {"from_high": 120, "from_medium": 40, "from_low": 5},
    "group_quality_gate": {"passed": 2, "skipped": 1}
  },
  "steps": [...]
}
```

No schema change for `PlanResponse` — `pipeline_summary` is on the **run** response, not plan response.

### Run response schema addition

```python
# In schemas/runs.py or equivalent
class RunResponse(BaseModel):
    ...
    pipeline_summary: dict | None = None
```

---

## 9. Request Flow — Complete Run Lifecycle

```
User clicks "Approve & Run"
        │
        ▼
┌─ RunnerService._execute_run() ──────────────────────────────────────────┐
│                                                                         │
│  STEP-1: SEARCH_POSTS "VIB Max Card"                                    │
│    ├── browser_agent.search_posts() → 50 posts, 19 groups              │
│    ├── _persist_posts() → save to crawled_posts                        │
│    ├── ► heuristic_label_posts() → label 50 posts (US-31)              │
│    │     22 high, 13 medium, 15 low                                    │
│    ├── ► score_groups() → score 19 groups (US-30)                      │
│    │     3 relevant (score≥0.15), 16 skipped                           │
│    └── checkpoint: {posts, discovered_groups: [3 relevant only],        │
│                     group_scoring: {...}, label_summary: {...}}         │
│                                                                         │
│  STEP-2: CRAWL_COMMENTS                                                 │
│    ├── _resolve_post_refs() → 50 post URLs                             │
│    ├── ► prioritize_post_refs() → sort by tier (US-32)                 │
│    │     tier_high: 22 posts × 5 comments = 110 budget                 │
│    │     tier_medium: 13 posts × 4 comments = 52 budget                │
│    │     tier_low: 15 posts × 2 comments = 30 budget                   │
│    ├── crawl in priority order (high first)                            │
│    └── checkpoint: {collected, per_tier_stats}                         │
│                                                                         │
│  STEP-3: JOIN_GROUP                                                     │
│    ├── _resolve_private_group_ids() → private groups                   │
│    ├── ► filter by group_scoring (US-30) → skip irrelevant             │
│    └── join only relevant private groups                               │
│                                                                         │
│  STEP-4: CHECK_JOIN_STATUS                                              │
│    └── (unchanged)                                                     │
│                                                                         │
│  STEP-5: SEARCH_IN_GROUP                                                │
│    ├── _resolve_discovered_group_ids() → accessible groups             │
│    ├── ► quality_gate_groups() → filter by post quality (US-34)        │
│    └── search only in quality groups                                   │
│                                                                         │
│  RUN COMPLETE → pipeline_summary aggregated from checkpoints (US-33)   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Trade-Off Analysis

| Decision | Alternative | Why chosen |
|----------|-------------|------------|
| Heuristic-only labeling between steps (R-31) | AI call for better accuracy | Latency: heuristic <10ms vs AI 2-3s. Pipeline must not block. AI runs later in Phase 2 flow. |
| Token overlap for group scoring | AI-based group classification | Sufficient for name-based filtering. "Review Khách Sạn" vs "sản phẩm làm đẹp" has zero overlap — simple and effective. |
| Soft priority (deprioritize) vs hard filter (skip) for posts | Hard skip saves more time | R-33 recoverable decisions. Seller post may have valuable comments. Low-priority posts still get 10% budget. |
| Hard skip for groups below threshold | Soft deprioritize | Groups are coarser — joining an irrelevant group wastes a WRITE action and increases account risk. Hard skip justified. |
| Checkpoint-based storage for pipeline data | New DB tables | No migration needed. Pipeline data is ephemeral per-run. Checkpoint JSON is extensible. |
| Single module `pipeline_intelligence.py` | Spread across existing files | Clean separation. Runner stays as orchestrator, intelligence is pluggable and testable in isolation. |
| Feature flag `pipeline_intelligence_enabled` | Always on | Allows instant rollback. New logic might have edge cases with different topic types. |

---

## 11. Implementation Slices

### Slice 1 — Foundation (Sprint 3A, ~2 days)

| File | Change |
|------|--------|
| `backend/app/infra/text_utils.py` | **New** — `strip_diacritics`, `tokenize_vn`, `token_overlap_score` |
| `backend/app/services/pipeline_intelligence.py` | **New** — `PipelineIntelligence` class with `score_group_relevance`, `heuristic_label_posts` |
| `backend/app/infrastructure/config.py` | Add 6 settings (thresholds, feature flag) |
| `backend/app/domain/label_taxonomy.py` | Add `HEURISTIC_LABELED` to `LABEL_RECORD_STATUSES` |
| `backend/alembic/versions/007_add_heuristic_labeled_status.py` | **New** — migration for label_status constraint |

### Slice 2 — Runner Integration (Sprint 3A, ~2 days)

| File | Change |
|------|--------|
| `backend/app/services/runner.py` | Inject `PipelineIntelligence`, add interceptors in SEARCH_POSTS/JOIN_GROUP handlers |
| `backend/app/services/runner.py` | Add `_apply_heuristic_label()`, `_load_topic_keywords()`, `_load_label_map()`, `_get_cached_group_scoring()` helper methods |

### Slice 3 — Priority Crawl + Quality Gate (Sprint 3B, ~2 days)

| File | Change |
|------|--------|
| `backend/app/services/pipeline_intelligence.py` | Add `prioritize_post_refs`, `quality_gate_groups` |
| `backend/app/services/runner.py` | Modify CRAWL_COMMENTS handler to use priority order + per-post budget |
| `backend/app/services/runner.py` | Add quality gate interceptor in SEARCH_IN_GROUP handler |

### Slice 4 — Pipeline Dashboard (Sprint 3C, ~2 days)

| File | Change |
|------|--------|
| `backend/app/services/pipeline_intelligence.py` | Add `build_pipeline_summary` |
| `backend/app/services/runner.py` | Enrich `get_run()` with `pipeline_summary` |
| `backend/app/schemas/runs.py` | Add `pipeline_summary: dict | None` to RunResponse |
| `frontend/src/pages/MonitorPage.tsx` | Add pipeline funnel section |
| `frontend/src/styles.css` | Funnel styling |

### Slice 5 — Verification

| Test | Validates |
|------|-----------|
| Mock mode e2e: topic "sản phẩm làm đẹp thiên nhiên" | Group "Ăn Vặt BMT" skipped, "REVIEW MỸ PHẨM" passes |
| Mock mode e2e: all posts are seller | CRAWL_COMMENTS still runs (graceful degradation), warns user |
| Mock mode e2e: pipeline disabled via feature flag | Identical behavior to pre-Phase 3 |
| Compare funnel: % relevant in CRAWL_COMMENTS before/after | Target: 44% → >70% |
| Real browser run on 3 different topics | Verify group names resolve, quality gate works end-to-end |
