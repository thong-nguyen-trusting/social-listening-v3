# User Stories — Phase 2: Trustworthy Feedback Labeling
## AI Facebook Social Listening & Engagement v3

**Product:** AI-powered Facebook research and engagement assistant
**Primary users:** Researcher, Marketer, Sales/BD
**Language:** Vietnamese first, English supported
**Phase:** 2 — Trustworthy Feedback Labeling
**Updated:** 2026-03-29

---

## Phase 2 Scope

Phase 1 đã prove được core loop crawl -> theme analysis.
Phase 2 tập trung vào **chất lượng của insight**:

- Label từng `POST` và `COMMENT` bằng AI service
- Phân biệt tương đối giữa `end_user`, `seller_affiliate`, `brand_official`, `community_admin`, `unknown`
- Tính `user_feedback_relevance` để biết record nào nên vào theme analysis mặc định
- Cho phép user đổi filter trên UI Themes/Monitor
- Hiển thị minh bạch số record bị loại bởi label thay vì chỉ `spam_or_seller_noise`

---

## Cross-Cutting Rules

**R-20 — Label first, filter second**
Không hard-delete hoặc bỏ record ngay ở crawl layer chỉ vì nghi là seller hoặc brand.
Mọi record phải được persist trước, rồi mới label và filter ở analysis layer.

**R-21 — Post/comment independence**
`COMMENT` không được inherit cứng `author_role` từ `POST` cha.
Comment dưới post bán hàng vẫn có thể là feedback end user thật.

**R-22 — Explainability**
Mỗi label phải có:
- `label_confidence`
- `label_reason`
- `label_source` (`heuristic` | `ai` | `hybrid`)

**R-23 — Safe fallback**
Nếu AI labeling fail hoặc timeout:
- record được gán `author_role=unknown`
- `user_feedback_relevance=medium`
- hệ thống không được drop record âm thầm

**R-24 — Filter transparency**
Khi record không được đưa vào theme analysis theo filter hiện tại, UI phải hiển thị:
- tổng số excluded
- breakdown theo label
- policy đang áp dụng

**R-25 — Vietnamese-first labeling**
Prompt labeling phải hiểu:
- tiếng Việt có dấu và không dấu
- seller slang VN: `ib`, `inbox`, `pass lại`, `chốt đơn`, `deal`, `kéo thẻ`, `mở thẻ`, `ref`
- end-user phrasing: `mình dùng`, `em bị`, `có ai giống em`, `cho em hỏi`, `trải nghiệm`

---

## Story Map

```
CRAWL DATA              LABEL DATA                  ANALYZE + REVIEW
────────────────────────────────────────────────────────────────────────────
US-20 Persist raw       US-21 AI label records      US-23 Theme filter policy
                        US-22 Labeling progress      US-24 Themes UI filters
                                                    US-25 Excluded by label audit
```

---

## User Stories

### US-20: Persist Raw Crawled Posts and Comments Without Early Deletion

**As a** researcher
**I want** every crawled post and comment to be stored before audience filtering happens
**So that** the system can decide later which records are genuine end-user feedback without losing raw evidence

**Acceptance Criteria:**

- Given a run crawls posts and comments successfully
  When the crawler persists records
  Then every record is stored even if it looks commercial or brand-owned

- Given a crawled comment belongs to a seller or brand post
  When the record is persisted
  Then the comment is still stored as an independent record with its own `record_type='COMMENT'`

- Given a record has not been labeled yet
  When it is first stored
  Then it is marked as `label_status='PENDING'` or equivalent and remains available for downstream labeling

- Given a record contains masked PII
  When it is persisted
  Then the masked content is the version used for labeling and analysis

**Out of scope:**
- Manual reviewer override
- Real-time inline labeling during crawl

**Dependencies:** Phase 1 crawl persistence

**Notes:**
- Story này khóa nguyên tắc kiến trúc: crawl layer không tự quyết định “seller nên bỏ”.

---

### US-21: AI Labels Each Post and Comment With Audience-Relevance Metadata

**As a** researcher
**I want** the system to classify each post/comment by author role, content intent, and end-user relevance
**So that** theme analysis can focus on genuine customer feedback instead of noisy promotional content

**Acceptance Criteria:**

- Given a run has crawled records with `label_status='PENDING'`
  When the labeling job starts
  Then the system classifies each record with at least:
  `author_role`, `content_intent`, `commerciality_level`, `user_feedback_relevance`, `label_confidence`, `label_reason`

- Given a record is a comment under a commercial or official post
  When the labeling job evaluates it
  Then the comment is classified from its own text and context, not forced to inherit the parent post label

- Given the AI model returns a low-confidence result or malformed output
  When the system persists the label
  Then it falls back to a safe label such as `author_role='unknown'` and records the fallback reason

- Given the labeling job completes
  When the user inspects the run
  Then the run exposes counts by label category and counts of unlabeled/failed labels

- Given the same run is analyzed later with a newer taxonomy version
  When re-labeling is triggered intentionally
  Then the system preserves label versioning or explicit replacement history rather than mutating silently

**Out of scope:**
- Detecting the real identity of the author
- Cross-platform identity resolution

**Dependencies:** US-20

**Notes:**
- `author_role` target set for Phase 2:
  `end_user | seller_affiliate | brand_official | community_admin | unknown`

---

### US-22: Show Labeling Progress and Failures in Monitor

**As a** researcher
**I want** to see whether labeling is still running, completed, or partially failed
**So that** I know whether the themes I am viewing already reflect the audience filter I selected

**Acceptance Criteria:**

- Given a run finishes crawling and starts labeling
  When I open Monitor
  Then I see labeling as a distinct section backed by a label job summary
  And the summary includes counts such as `pending`, `labeled`, `fallback`, `failed`

- Given labeling is still in progress
  When I view the run status
  Then the UI shows that themes may still change until labeling completes

- Given some records fail labeling
  When the run summary is shown
  Then the UI displays how many records failed and whether fallback labels were applied

**Out of scope:**
- Per-record manual retry from the UI

**Dependencies:** US-21

**Notes:**
- Story này giúp user không nhầm crawl done = insight done.
- Labeling progress should come from a dedicated labeling lifecycle, not by mutating crawl run semantics.

---

### US-23: Theme Analysis Respects Audience Filter Policies

**As a** researcher
**I want** theme analysis to apply a clear audience filter policy
**So that** the themes I see match the voice I am trying to understand

**Acceptance Criteria:**

- Given a run has labeled records
  When I request themes with the default policy
  Then only records classified as sufficiently relevant end-user feedback are included
  And the response identifies which taxonomy version and audience filter were used

- Given I select `End-user only`
  When theme analysis runs
  Then records labeled `seller_affiliate` and `brand_official` are excluded by default
  And end-user comments under seller/brand posts may still be included if their own labels qualify

- Given I select `Include seller`
  When theme analysis runs
  Then records labeled `seller_affiliate` can participate in the analysis while brand-owned records remain excluded unless explicitly included

- Given I select `Include brand`
  When theme analysis runs
  Then brand-owned records can participate in the analysis alongside end-user and seller content

- Given records are excluded under the active policy
  When the theme response is returned
  Then the payload includes `excluded_by_label_count` and a breakdown by reason or label

**Out of scope:**
- Weighted theme ranking by role segment
- Separate theme taxonomies per audience segment

**Dependencies:** US-21

**Notes:**
- Đây là policy layer, không phải crawl rule.
- Story này assume theme filtering happens at read-time, not by permanently marking records excluded for every future view.

---

### US-24: Themes UI Lets Me Switch Between End-user, Seller, and Brand Views

**As a** researcher
**I want** a simple filter control in Themes
**So that** I can compare genuine customer sentiment with seller or brand narratives without re-running the crawl

**Acceptance Criteria:**

- Given I open Themes for a run that has completed labeling
  When the filter control is displayed
  Then I can choose:
  `End-user only`, `Include seller`, `Include brand`

- Given `End-user only` is selected
  When themes load
  Then the UI makes it explicit that seller and brand content are excluded by policy

- Given I switch from `End-user only` to `Include seller`
  When the request completes
  Then the theme list and counts refresh to reflect the newly included records

- Given the system is fetching filtered themes
  When the request is in flight
  Then the filter CTA shows loading and prevents duplicate requests

- Given the theme response contains excluded breakdowns
  When the UI renders results
  Then I see a clear summary such as `Excluded by label: 24 (seller_affiliate: 18, brand_official: 6)`

**Out of scope:**
- Advanced multi-select audience builder
- Per-theme diff visualization

**Dependencies:** US-23

**Notes:**
- Default selected filter should be `End-user only`.

---

### US-25: Review Excluded Records and Reasons

**As a** researcher
**I want** to understand which records were excluded and why
**So that** I can trust the analysis and decide whether the current filter policy is too strict

**Acceptance Criteria:**

- Given a theme response excludes records by label
  When I expand the excluded summary
  Then I can see counts grouped by:
  `seller_affiliate`, `brand_official`, `community_admin`, `low_relevance`, `unknown`

- Given I inspect a sample excluded record
  When the detail view is shown
  Then the UI displays the record text, its labels, confidence, and exclusion reason

- Given a record was included even though the parent post was commercial
  When I inspect that record
  Then the UI shows that inclusion was based on the comment’s own label, not on the parent post

**Out of scope:**
- Editing labels from UI
- Bulk export of excluded records

**Dependencies:** US-21, US-23

**Notes:**
- Story này là trust layer cho người dùng nghiên cứu.

---

## Recommended Sprint Breakdown

| Sprint | Stories | Focus |
|--------|---------|-------|
| Sprint 2A | US-20, US-21 | Labeling pipeline + taxonomy contract |
| Sprint 2B | US-22, US-23 | Monitor status + filtered theme analysis |
| Sprint 2C | US-24, US-25 | UI controls + trust/audit visibility |

---

## Open Questions

1. Labeling nên chạy tự động ngay sau crawl hay chạy lazy khi user mở Themes lần đầu?
2. Phase 2 có cần lưu full label history hay chỉ current label + taxonomy version?
3. Có cần cho phép filter `seller only` hoặc `brand only` ở cuối Phase 2, hay tạm thời chỉ 3 preset như trên?
4. Nếu label confidence thấp nhưng record có chứa complaint rõ ràng, policy nên include hay exclude mặc định?
