# User Stories — Phase 3: Smart Crawl Pipeline
## AI Facebook Social Listening & Engagement v3

**Product:** AI-powered Facebook research and engagement assistant
**Primary users:** Researcher, Marketer, Sales/BD
**Language:** Vietnamese first, English supported
**Phase:** 3 — Smart Crawl Pipeline
**Updated:** 2026-03-29

---

## Tại sao cần Phase 3

Phase 1 prove core loop: search → plan → crawl → theme analysis.
Phase 2 thêm AI labeling chất lượng: label post/comment → audience filter → transparent exclusion.

**Vấn đề phát hiện từ production runs:**

Run `run-802cb7073a` (topic: "sản phẩm làm đẹp thiên nhiên") cho thấy:
- **30% posts là seller spam** (15/50 — group "Ngũ hoa hạt", toàn quảng cáo "Ce thích đắp ngũ hoa lên đơn e ship nha")
- **26% posts không liên quan** (13/50 — review khách sạn, ăn vặt, tai nghe)
- **Chỉ 44% posts thực sự liên quan** đến topic
- **16/19 discovered groups không liên quan** (Review Khách Sạn, Ăn Vặt BMT, Cuồng Tai nghe...)
- Hệ thống crawl comments của **toàn bộ 50 posts** bao gồm cả spam — lãng phí 5-10 phút crawl time

Content Labeling pipeline (Phase 2) đã tồn tại nhưng chỉ chạy **sau khi crawl xong**, khi user request theme analysis. Kết quả: hệ thống lãng phí thời gian crawl comments và search trong groups không liên quan.

**Phase 3 giải quyết:** Đưa intelligence vào giữa crawl pipeline — lọc groups, ưu tiên posts, và chỉ crawl sâu vào nội dung có giá trị.

---

## Phase 3 Scope

```
FILTER GROUPS           PRIORITIZE POSTS         SMART COMMENTS         TRANSPARENCY
─────────────────────  ────────────────────────  ────────────────────  ──────────────
US-30 Group relevance   US-31 Early heuristic    US-32 Priority-based  US-33 Pipeline
      scoring                 labeling                 comment crawl         dashboard
                                                US-34 Group quality
                                                      gate
```

---

## Cross-Cutting Rules

**R-30 — No hard delete at crawl time**
Phase 2 rule R-20 vẫn áp dụng: mọi record từ SEARCH_POSTS phải được persist trước.
Phase 3 thêm **soft priority** và **skip logic** — không xóa data, chỉ thay đổi thứ tự xử lý.

**R-31 — Heuristic only, no extra AI call between steps**
Giữa SEARCH_POSTS và CRAWL_COMMENTS, chỉ dùng heuristic (pattern matching cục bộ, không gọi AI model). Mục đích: không thêm latency hoặc failure point vào pipeline.

**R-32 — Transparency over automation**
Mọi quyết định skip/deprioritize phải logged và hiển thị cho user. User phải biết "X posts bị đánh low-priority vì seller pattern" thay vì thấy kết quả ít hơn mà không hiểu tại sao.

**R-33 — Recoverable decisions**
Posts bị deprioritize hoặc groups bị score thấp vẫn có thể được crawl nếu user muốn. Không có irreversible filtering trong pipeline.

---

## User Stories

---

### US-30: Score Discovered Groups by Topic Relevance

**As a** researcher
**I want** the system to evaluate whether discovered groups are actually relevant to my research topic
**So that** JOIN_GROUP and SEARCH_IN_GROUP only target groups that are likely to contain useful content, instead of wasting time on "Review Khách Sạn" when I'm researching skincare

**Acceptance Criteria:**

- Given SEARCH_POSTS has completed and discovered groups are in the checkpoint
  When the runner prepares for JOIN_GROUP or SEARCH_IN_GROUP
  Then each discovered group is scored for relevance against the original topic and keywords

- Given a group has a name like "Ăn Vặt BMT - Review Đồ Ăn BMT"
  When the topic is "sản phẩm làm đẹp thiên nhiên"
  Then the group receives a low relevance score because the name contains no overlap with topic keywords

- Given a group has a name like "REVIEW MỸ PHẨM - TÂM SỰ SKINCARE"
  When the topic is "sản phẩm làm đẹp thiên nhiên"
  Then the group receives a high relevance score because it matches the topic domain

- Given a group has relevance score below threshold
  When JOIN_GROUP step runs
  Then the group is skipped and the step checkpoint records `skipped_groups` with reason `"low_group_relevance"`

- Given a group has relevance score below threshold
  When SEARCH_IN_GROUP step runs
  Then the group is skipped and the step checkpoint records the skip reason

- Given all discovered groups are below threshold
  When JOIN_GROUP or SEARCH_IN_GROUP runs
  Then the step completes with `actual_count=0` and a note `"no relevant groups found"` — it does not fail

- Given the runner skips groups
  When the run summary is shown to the user
  Then the user sees: "X/Y groups skipped (low relevance)" with the ability to see which groups were skipped and why

**Out of scope:**
- AI-based group classification (Phase 3 uses heuristic only, per R-31)
- Manual group whitelist/blacklist management
- Group content sampling before scoring

**Dependencies:** Phase 1 SEARCH_POSTS pipeline, Phase 2 labeling taxonomy (for keyword overlap logic)

**Notes:**
- Scoring mechanism: token overlap between `group.name` (cleaned, lowercased, diacritics-removed) and `ProductContext.topic` + `ProductContext.keywords` (flattened). Score = matched tokens / total topic tokens. Threshold suggested: 0.2 (at least 1 in 5 topic words must appear in group name).
- This scoring runs synchronously in the runner between SEARCH_POSTS checkpoint processing and JOIN_GROUP/SEARCH_IN_GROUP execution — no separate step needed.
- Must handle Vietnamese diacritics: "mỹ phẩm" should match "my pham" in group name.

---

### US-31: Early Heuristic Labeling After SEARCH_POSTS

**As a** researcher
**I want** the system to quickly classify posts right after SEARCH_POSTS using pattern-based heuristics
**So that** the system knows which posts are likely seller spam, brand content, or genuine user feedback before spending time crawling their comments

**Acceptance Criteria:**

- Given SEARCH_POSTS has collected N posts
  When the posts are persisted to the database
  Then the runner immediately runs heuristic labeling (from `labeling_heuristics.py`) on all N posts before starting CRAWL_COMMENTS

- Given a post matches 2+ seller patterns (e.g., "ib", "ship", "lên đơn")
  When heuristic labeling runs
  Then the post is labeled `author_role=seller_affiliate`, `user_feedback_relevance=low`, `label_source=heuristic`

- Given a post matches experience patterns (e.g., "mình dùng", "trải nghiệm")
  When heuristic labeling runs
  Then the post is labeled `author_role=end_user`, `user_feedback_relevance=high`, `label_source=heuristic`

- Given a post does not match any heuristic pattern strongly
  When heuristic labeling runs
  Then the post receives `author_role=unknown`, `user_feedback_relevance=medium`, `label_source=heuristic`

- Given heuristic labeling completes
  When the results are stored
  Then each post's `label_status` is updated from `PENDING` to `HEURISTIC_LABELED` (not `LABELED` — full AI labeling still happens later in Phase 2 pipeline)

- Given the heuristic labeling step fails or times out
  When the error is caught
  Then all posts retain `label_status=PENDING` and CRAWL_COMMENTS proceeds without priority ordering — graceful degradation

**Out of scope:**
- AI model call at this stage (per R-31)
- Overriding Phase 2 full labeling results
- User-facing label editing at this stage

**Dependencies:** Phase 2 `labeling_heuristics.py` (reuse existing patterns), US-20 (persist first)

**Notes:**
- This reuses `classify_content()` from `labeling_heuristics.py` — no new labeling logic needed, just calling it earlier in the pipeline.
- Heuristic labels are preliminary: when Phase 2 full labeling runs later, it overwrites with higher-quality AI + heuristic hybrid labels.
- The `label_status=HEURISTIC_LABELED` state is a new enum value that distinguishes "quick-labeled by pattern" from "fully-labeled by AI pipeline".

---

### US-32: Priority-Based Comment Crawling

**As a** researcher
**I want** CRAWL_COMMENTS to crawl high-relevance posts first and low-relevance posts last
**So that** if the crawl is stopped or times out, the most valuable comments have already been collected

**Acceptance Criteria:**

- Given SEARCH_POSTS returned 50 posts and US-31 heuristic labeling is complete
  When CRAWL_COMMENTS starts
  Then posts are sorted by priority: `high` relevance first, `medium` second, `low` last

- Given the comment crawl budget is 200 comments across 50 posts
  When the runner allocates per-post budget
  Then `high` relevance posts receive more budget (e.g., 8 comments each) than `low` relevance posts (e.g., 2 comments each)

- Given the run is cancelled or paused mid-CRAWL_COMMENTS
  When the user reviews what was collected
  Then the majority of collected comments come from high-relevance posts — not from seller spam

- Given all posts have `user_feedback_relevance=low` (e.g., all seller content)
  When CRAWL_COMMENTS runs
  Then the step still proceeds (no hard block) but logs a warning: "All posts scored low relevance — comments may not reflect end-user feedback"

- Given heuristic labeling failed (US-31 graceful degradation)
  When CRAWL_COMMENTS starts
  Then it falls back to the original order (no prioritization) — same behavior as before Phase 3

- Given the run completes
  When the user views run summary
  Then they see: "Crawled comments from X high-relevance posts, Y medium, Z low (W skipped due to budget)"

**Out of scope:**
- Completely skipping low-relevance posts (they are deprioritized, not deleted)
- Re-ordering posts based on engagement metrics (reaction_count, comment_count)
- Real-time re-prioritization during crawl

**Dependencies:** US-31

**Notes:**
- Priority tiers map directly to `user_feedback_relevance`: high → tier 1, medium → tier 2, low → tier 3.
- Budget allocation formula suggestion: tier 1 gets 60% of budget, tier 2 gets 30%, tier 3 gets 10%. Exact split is configurable.
- If a post has 0 comments on Facebook, the budget allocated to it is returned to the pool.

---

### US-33: Pipeline Transparency Dashboard

**As a** researcher
**I want** to see how the smart pipeline filtered and prioritized content at each stage
**So that** I trust the system's decisions and can adjust my approach if too much content was filtered

**Acceptance Criteria:**

- Given a run has completed with Phase 3 smart pipeline active
  When I open the run summary
  Then I see a pipeline funnel view showing:
  - SEARCH_POSTS: X posts found
  - Heuristic labeling: Y high / Z medium / W low relevance
  - Group scoring: A relevant / B skipped groups
  - CRAWL_COMMENTS: C comments from high-relevance posts, D from medium, E from low
  - SEARCH_IN_GROUP: F posts from G relevant groups

- Given some groups were skipped by US-30
  When I expand the group scoring section
  Then I see each skipped group's name, relevance score, and skip reason

- Given some posts were deprioritized by US-31/US-32
  When I expand the post prioritization section
  Then I see counts by relevance tier and sample post IDs per tier

- Given I disagree with the pipeline's decisions
  When I want to override
  Then I see guidance: "Adjust topic keywords for better group matching" or "Lower the group relevance threshold in settings"

- Given the pipeline data is available
  When the run is viewed via API (`GET /api/runs/{run_id}`)
  Then the response includes a `pipeline_summary` object with all funnel metrics

**Out of scope:**
- Real-time pipeline visualization during crawl (shows after completion)
- Per-record drill-down with label editing
- A/B comparison between runs with different pipeline settings

**Dependencies:** US-30, US-31, US-32

**Notes:**
- Pipeline summary is computed from existing step checkpoint data — no new storage needed.
- This is primarily a read-only transparency feature. Settings adjustment (threshold tuning) is Phase 4.

---

### US-34: Group Quality Gate for SEARCH_IN_GROUP

**As a** researcher
**I want** SEARCH_IN_GROUP to only search within groups where SEARCH_POSTS found at least 1 relevant post
**So that** the system doesn't waste time searching inside groups that produced only spam or irrelevant content

**Acceptance Criteria:**

- Given SEARCH_POSTS found 50 posts across 19 groups
  When heuristic labeling (US-31) marks 15 posts from group "Ngũ hoa hạt" as `seller_affiliate`
  Then the group "Ngũ hoa hạt" is flagged as `low_quality_source` because 100% of its posts are seller content

- Given a group has more than 50% of its posts labeled as `high` or `medium` relevance
  When SEARCH_IN_GROUP runs
  Then that group is included in the in-group search

- Given a group has more than 70% of its posts labeled as `low` relevance (seller/brand/irrelevant)
  When SEARCH_IN_GROUP runs
  Then that group is skipped with reason `"low_quality_source"` in the step checkpoint

- Given a group had only 1 post discovered and it was `medium` relevance
  When SEARCH_IN_GROUP runs
  Then that group is included (benefit of the doubt for small sample)

- Given all discovered groups fail the quality gate
  When SEARCH_IN_GROUP runs
  Then the step completes with `actual_count=0` and note `"no quality groups to search"` — does not fail the run

- Given groups are skipped
  When the pipeline dashboard (US-33) shows results
  Then skipped groups appear with their quality score and the count of posts per relevance tier

**Out of scope:**
- Re-crawling the group to get a better sample
- User override to force search in a specific group
- Group quality score persistence across runs

**Dependencies:** US-30, US-31

**Notes:**
- Quality gate logic: for each group, count posts by `user_feedback_relevance`. If `low / total > 0.7`, skip the group. This is a simple ratio, not an AI call.
- Group quality is ephemeral — computed per-run from the posts discovered in that run. Not persisted as a permanent group attribute.

---

## Story Map

```
SEARCH_POSTS ──────────────────────────────────────────────────────────────────────
     │
     ├── US-30: Score groups ──► Filter for JOIN_GROUP / SEARCH_IN_GROUP
     │
     ├── US-31: Heuristic label posts ──► Priority tags
     │                                       │
     │                                       ▼
     │                               US-32: Priority-based
     │                                       CRAWL_COMMENTS
     │
     ├── US-34: Group quality gate ──► Filter for SEARCH_IN_GROUP
     │
     └── US-33: Pipeline dashboard ──► Show funnel to user
```

---

## Recommended Sprint Breakdown

| Sprint | Stories | Focus |
|--------|---------|-------|
| Sprint 3A | US-30, US-31 | Group scoring + early heuristic labeling (foundation) |
| Sprint 3B | US-32, US-34 | Priority crawl + group quality gate (optimization) |
| Sprint 3C | US-33 | Pipeline transparency (trust & visibility) |

**Sprint 3A gate:** US-31 must reuse existing `labeling_heuristics.py` patterns. If new patterns are needed, add them in Sprint 3A before Sprint 3B depends on label quality.

**Sprint 3B gate:** Test with at least 3 real runs on different topics. Compare funnel metrics before/after Phase 3: % relevant posts in CRAWL_COMMENTS should increase from ~44% to >70%.

---

## INVEST Check

| Story | I | N | V | E | S | T | Flag |
|-------|---|---|---|---|---|---|------|
| US-30 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| US-31 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Reuses existing heuristics — low new-code risk |
| US-32 | ~ | ✓ | ✓ | ✓ | ✓ | ✓ | Depends on US-31 for priority data. If US-31 is not done, falls back gracefully. |
| US-33 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Read-only — low risk, high trust value |
| US-34 | ~ | ✓ | ✓ | ✓ | ✓ | ✓ | Depends on US-30 + US-31. Small scope — could merge with US-30 if too thin. |

---

## Open Questions

| # | Question | Impact | Owner |
|---|----------|--------|-------|
| OQ-1 | Group relevance threshold: 0.2 token overlap là đủ hay quá strict? Cần test trên 5+ topics. | US-30 scoring accuracy | Tech |
| OQ-2 | Budget allocation ratio (60/30/10) cho comment crawl tiers — cần tune dựa trên real data không? | US-32 comment quality | Product/Tech |
| OQ-3 | `HEURISTIC_LABELED` có cần là status riêng hay reuse `PENDING` + `label_source=heuristic`? | US-31 schema impact | Tech |
| OQ-4 | Pipeline dashboard nên là tab riêng hay section trong Monitor page? | US-33 UX | Product |
| OQ-5 | Nếu user muốn force crawl một group bị skip, UX flow nào? Rerun vs manual override? | US-30 recoverability | Product |
