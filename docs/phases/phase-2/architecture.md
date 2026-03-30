# Solution Architecture — Phase 2: Trustworthy Feedback Labeling
## AI Facebook Social Listening & Engagement v3

**Phase:** 2 — Trustworthy Feedback Labeling
**Stories covered:** US-20, US-21, US-22, US-23, US-24, US-25
**Updated:** 2026-03-29
**Status:** Implemented in local Phase 2 delivery slice with taxonomy version `v1`

---

## 1. Executive Summary

Phase 2 giải bài toán chất lượng insight sau crawl:

> Làm sao để themes phản ánh tiếng nói của end user, thay vì bị lẫn seller, brand-owned content, hoặc admin announcements?

**Decision của solution architecture:**

1. `POST` và `COMMENT` vẫn được crawl/persist đầy đủ như Phase 1.
2. Một pipeline **labeling bất đồng bộ** chạy sau crawl để gắn audience labels cho từng record.
3. Theme analysis không dùng regex exclude thô nữa; thay vào đó áp dụng **filter policy ở read-time**.
4. UI Themes/Monitor hiển thị filter preset và số liệu `excluded by label` minh bạch.

Điểm quan trọng nhất: **không nhét labeling vào crawler và không overload run status hiện tại**.
Thay vào đó, dùng `label_jobs` tách riêng khỏi `plan_runs`.

---

## 2. Problem and Constraints

### 2.1 Problem

Phase 1 đã crawl được dữ liệu và tạo themes, nhưng logic lọc hiện tại ở [insight.py](/Users/nguyenquocthong/project/social-listening-v3/backend/app/services/insight.py) mới chỉ là regex-based noise filtering. Cách này không đủ để phân biệt:

- feedback end user thật
- seller/affiliate promotion
- brand-owned or official messaging
- community admin posts
- mixed threads nơi post là commercial nhưng comment lại là user feedback thật

### 2.2 Hard constraints

| Constraint | Why it matters |
|-----------|----------------|
| Facebook data được lấy bằng browser automation, không có structured API | Metadata author/source bị hạn chế, labeling phải dựa nhiều vào text + context |
| Dữ liệu đã persist là masked/opaque-first | Prompt labeling phải dùng masked text và metadata an toàn |
| Phase 1 run engine đang ổn định | Không nên phá `plan_runs` / `step_runs` state machine chỉ để thêm labeling |
| UI hiện dùng `GET /api/runs/{run_id}/themes` | Nên evolve API có kiểm soát, tránh redesign quá rộng |
| Cần khả năng re-label khi taxonomy/prompt đổi | Không nên coi label là immutable field cứng trên `crawled_posts` |

### 2.3 Non-functional requirements

| NFR | Target |
|-----|--------|
| Correctness bias | Ưu tiên explainability và safe fallback hơn là aggressive filtering |
| Auditability | Phải biết record nào bị loại và vì sao |
| Backfill-friendly | Có thể label lại run cũ khi taxonomy đổi |
| Incremental delivery | Có thể ship backend labeling trước, UI filter sau |
| Cost control | Labeling phải batch được, không gọi model 1 request/record |

---

## 3. Architecture Decisions

### D-20 — Persist first, label later

```
Crawl -> Persist raw records -> Create label job -> Persist labels -> Analyze with policy
```

Lý do:
- không mất raw evidence
- cho phép taxonomy evolve
- giữ crawler đơn giản

### D-21 — Labeling is a separate background concern

**Chosen design:** `label_jobs` tách riêng khỏi `plan_runs`.

Không chọn “add extra steps vào plan run” vì:
- crawl run và enrichment run là hai lifecycle khác nhau
- re-label không nên tạo plan run mới
- UI cần progress labeling nhưng không nên mutate `RUNNING/DONE/FAILED` semantics của crawl run

### D-22 — Theme filter is a read-time policy

Không pre-delete hay hard-mark `excluded` duy nhất một lần.
Một record có thể:
- bị exclude ở `End-user only`
- nhưng lại được include ở `Include seller`

Vì vậy filter phải là policy động khi đọc dữ liệu.

### D-23 — Post and comment are labeled independently

Comment dưới post seller không tự động bị exclude.
Đây là requirement cốt lõi để không bỏ mất tiếng nói user thật.

### D-24 — Hybrid classification

**Chosen design:** `heuristic -> AI adjudication -> fallback`

Không chọn heuristic-only vì độ chính xác thấp.
Không chọn AI-only vì:
- tốn chi phí
- khó explain
- fail mode cao hơn khi output malformed

---

## 4. Proposed System Design

### 4.1 Module map

```
┌─────────────────────────────────────────────────────────────────┐
│                         React UI                                │
│  MonitorPage                ThemesPage                          │
│  - labeling progress        - audience filter                   │
│  - label job status         - excluded by label                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / SSE
┌──────────────────────────────▼──────────────────────────────────┐
│                         FastAPI App                              │
│  ┌─────────────────────┐    ┌────────────────────────────────┐  │
│  │ Labeling Router     │    │ Insights Router                │  │
│  │ /labels/summary     │    │ /runs/{id}/themes             │  │
│  └──────────┬──────────┘    └───────────────┬────────────────┘  │
│             │                                │                   │
│  ┌──────────▼──────────┐          ┌──────────▼──────────────┐    │
│  │ ContentLabelingSvc  │          │ InsightService          │    │
│  │ - batch records     │          │ - load labels           │    │
│  │ - heuristic pass    │          │ - apply policy          │    │
│  │ - AI adjudication   │          │ - build themes          │    │
│  └──────────┬──────────┘          └──────────┬──────────────┘    │
│             │                                │                   │
│  ┌──────────▼──────────┐          ┌──────────▼──────────────┐    │
│  │ LabelRepository     │          │ AudienceFilterPolicy    │    │
│  └──────────┬──────────┘          └─────────────────────────┘    │
└─────────────┼────────────────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────────┐
│                           SQLite                                 │
│ crawled_posts | content_labels | label_jobs | theme_results      │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 New bounded responsibilities

**`ContentLabelingService`**
- owns batch selection of unlabeled records
- computes heuristic signals
- calls AI in batches
- persists labels and job progress

**`AudienceFilterPolicy`**
- maps UI preset -> inclusion logic
- is pure policy, no DB side effects

**`InsightService`**
- consumes the latest labels
- applies filter policy
- computes excluded breakdowns
- triggers theme classification on filtered subset

**`LabelingReadModel`**
- optimized queries for Monitor/Themes
- avoids overloading `crawled_posts` joins in UI paths

---

## 5. Data Model

### 5.1 Existing tables reused

- `crawled_posts`
- `plan_runs`
- `theme_results`

### 5.2 New tables

#### `label_jobs`

Tracks one labeling execution for one run and one taxonomy version.

```sql
CREATE TABLE label_jobs (
  label_job_id           TEXT PRIMARY KEY,
  run_id                 TEXT NOT NULL REFERENCES plan_runs(run_id),
  taxonomy_version       TEXT NOT NULL,
  model_name             TEXT,
  status                 TEXT NOT NULL CHECK(status IN (
                           'PENDING','RUNNING','DONE','FAILED','CANCELLED','PARTIAL'
                         )),
  records_total          INTEGER NOT NULL DEFAULT 0,
  records_labeled        INTEGER NOT NULL DEFAULT 0,
  records_fallback       INTEGER NOT NULL DEFAULT 0,
  records_failed         INTEGER NOT NULL DEFAULT 0,
  started_at             TEXT,
  ended_at               TEXT,
  error_message          TEXT,
  created_at             TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### `content_labels`

Stores classification outputs. One record may have many labels historically, but only one current label per taxonomy version.

```sql
CREATE TABLE content_labels (
  label_id                TEXT PRIMARY KEY,
  post_id                 TEXT NOT NULL REFERENCES crawled_posts(post_id),
  run_id                  TEXT NOT NULL REFERENCES plan_runs(run_id),
  label_job_id            TEXT NOT NULL REFERENCES label_jobs(label_job_id),
  taxonomy_version        TEXT NOT NULL,
  author_role             TEXT NOT NULL CHECK(author_role IN (
                            'end_user','seller_affiliate','brand_official','community_admin','unknown'
                          )),
  content_intent          TEXT NOT NULL CHECK(content_intent IN (
                            'experience','question','promotion','support_answer','comparison','other'
                          )),
  commerciality_level     TEXT NOT NULL CHECK(commerciality_level IN ('low','medium','high')),
  user_feedback_relevance TEXT NOT NULL CHECK(user_feedback_relevance IN ('high','medium','low')),
  label_confidence        REAL NOT NULL,
  label_reason            TEXT NOT NULL,
  label_source            TEXT NOT NULL CHECK(label_source IN (
                            'heuristic','ai','hybrid','fallback'
                          )),
  model_name              TEXT,
  model_version           TEXT,
  is_current              BOOLEAN NOT NULL DEFAULT TRUE,
  created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 Changes to `crawled_posts`

Add lightweight summary pointers:

```sql
ALTER TABLE crawled_posts ADD COLUMN label_status TEXT NOT NULL DEFAULT 'PENDING';
ALTER TABLE crawled_posts ADD COLUMN current_label_id TEXT REFERENCES content_labels(label_id);
```

`label_status`:
- `PENDING`
- `LABELED`
- `FALLBACK`
- `FAILED`

### 5.4 Why separate `label_jobs` is better

Trade-off:

| Option | Pros | Cons |
|--------|------|------|
| Add labeling into `plan_runs` | Ít bảng mới | Re-label awkward, progress semantics lẫn với crawl |
| Separate `label_jobs` | Clean lifecycle, retry/backfill dễ, monitor rõ | Thêm một layer orchestration |

**Chosen:** separate `label_jobs`.

---

## 6. Label Taxonomy and Policy

### 6.1 Record taxonomy

```json
{
  "author_role": "end_user | seller_affiliate | brand_official | community_admin | unknown",
  "content_intent": "experience | question | promotion | support_answer | comparison | other",
  "commerciality_level": "low | medium | high",
  "user_feedback_relevance": "high | medium | low",
  "label_confidence": 0.0,
  "label_reason": "short explanation",
  "label_source": "heuristic | ai | hybrid | fallback",
  "taxonomy_version": "v1"
}
```

### 6.2 Policy presets

**`end_user_only`**
- include:
  - `author_role=end_user`
  - `user_feedback_relevance in ('high','medium')`
- exclude:
  - `seller_affiliate`
  - `brand_official`
  - `community_admin`
  - `unknown` with low confidence or low relevance

**`include_seller`**
- include:
  - everything from `end_user_only`
  - `seller_affiliate`
- still exclude:
  - `brand_official`
  - low relevance records

**`include_brand`**
- include:
  - end user
  - seller
  - brand
- still exclude:
  - very low relevance noise if policy says so

### 6.3 Important nuance

Commercial source != low user value.

Examples:
- post = seller, comment = end user complaint -> should be includable
- post = official brand announcement, comment = genuine pain point -> should be includable under end-user view if comment qualifies

---

## 7. Execution Flow

### 7.1 End-to-end flow

```
1. Crawl run finishes and persists records
2. System creates label_job(run_id, taxonomy_version)
3. ContentLabelingService selects unlabeled records in batches
4. Heuristic pass scores easy cases
5. Ambiguous records go to AI labeling prompt
6. Labels are persisted and `current_label_id` updated
7. Monitor reads label_job progress
8. Themes page calls theme analysis with audience_filter
9. InsightService loads current labels, applies policy, returns themes + excluded breakdown
```

### 7.2 Label job state machine

```
PENDING -> RUNNING -> DONE
                └-> PARTIAL
                └-> FAILED
```

`PARTIAL` means:
- some records labeled
- some records fallback/failed
- still safe to use with transparency in UI

### 7.3 Batch strategy

Recommended initial batch size:
- 20-50 records per AI request depending on token size

Rules:
- comments and posts may be mixed in a batch
- include `record_type`, masked content, parent context summary
- cap maximum content length per record before prompt assembly

---

## 8. API Contract

### 8.1 Themes API

Current:

```http
GET /api/runs/{run_id}/themes
```

Proposed:

```http
GET /api/runs/{run_id}/themes?audience_filter=end_user_only
GET /api/runs/{run_id}/themes?audience_filter=include_seller
GET /api/runs/{run_id}/themes?audience_filter=include_brand
```

Response:

```json
{
  "run_id": "run-123",
  "audience_filter": "end_user_only",
  "taxonomy_version": "v1",
  "posts_crawled": 120,
  "posts_included": 72,
  "posts_excluded": 48,
  "excluded_by_label_count": 48,
  "excluded_breakdown": {
    "seller_affiliate": 31,
    "brand_official": 9,
    "community_admin": 4,
    "low_relevance": 4
  },
  "themes": [],
  "warning": null
}
```

### 8.2 Label summary API

```http
GET /api/runs/{run_id}/labels/summary
```

Response:

```json
{
  "run_id": "run-123",
  "label_job_id": "label-job-001",
  "status": "RUNNING",
  "taxonomy_version": "v1",
  "records_total": 320,
  "records_labeled": 180,
  "records_fallback": 8,
  "records_failed": 2,
  "counts_by_author_role": {
    "end_user": 96,
    "seller_affiliate": 41,
    "brand_official": 12,
    "community_admin": 5,
    "unknown": 26
  }
}
```

### 8.3 Optional audit API

```http
GET /api/runs/{run_id}/records?label_filter=seller_affiliate&limit=20
```

Use cases:
- trust panel in Themes
- sampling excluded records

---

## 9. UI Solution

### 9.1 Monitor Page

Do not overload crawl step list.
Instead add a separate section:

- `Labeling status`
- `Records labeled / total`
- `Fallback count`
- `Failed count`
- `Taxonomy version`

If label job is still running:
- show a soft warning that filtered themes may still shift

### 9.2 Themes Page

Required controls:
- `End-user only`
- `Include seller`
- `Include brand`

Required summaries:
- included count
- excluded by label count
- label breakdown
- optional “view excluded sample” panel

### 9.3 UX defaults

- default filter = `End-user only`
- disable re-fetch CTA while request is in flight
- show distinct states for:
  - crawl exists but labeling pending
  - labeling partial
  - themes ready

---

## 10. AI Service Design

### 10.1 Prompt artifact

Add:
- [content_labeling.md](/Users/nguyenquocthong/project/social-listening-v3/backend/app/skills/content_labeling.md)

Prompt constraints:
- Vietnamese-first
- JSON-only output
- per-record classification
- short `label_reason`
- no chain-of-thought

### 10.2 Inputs to model

Per record:
- `post_id`
- `record_type`
- masked `content`
- optional `parent_post_id`
- optional `parent_post_summary`
- optional source hints from URL or known role markers

### 10.3 Heuristic pre-pass

Examples:

- seller markers:
  - `ib`, `inbox`, `zalo`, `liên hệ`, `đăng ký`, `ref`, `mở thẻ ib mình`
- end-user markers:
  - `mình dùng`, `em bị`, `cho em hỏi`, `có ai giống`, `trải nghiệm`
- official markers:
  - `fanpage chính thức`, `official`, `CSKH`, `thông báo từ admin`

Heuristics should not directly exclude.
They should only:
- pre-fill weak priors
- skip AI for trivially obvious records if confidence is high enough

### 10.4 Failure strategy

If model fails:
- persist fallback label
- mark `label_source='fallback'`
- increment `records_fallback`
- do not block theme analysis forever

---

## 11. Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Separate `label_jobs` | Re-label and monitor cleanly | More tables and orchestration |
| Read-time filter policy | Flexible UI and auditability | Slightly more expensive reads |
| Hybrid labeling | Better precision/cost balance | More implementation complexity |
| Keep raw records | Preserves evidence and reuse | More storage |

---

## 12. Implementation Slices

### Slice A — Schema and contracts

- add `label_jobs`
- add `content_labels`
- add `label_status` + `current_label_id` to `crawled_posts`
- extend theme response schema

### Slice B — Labeling backend

- `ContentLabelingService`
- heuristic pass
- AI prompt + parser
- background job orchestration

### Slice C — Policy-aware themes

- `AudienceFilterPolicy`
- update `InsightService`
- `/api/runs/{id}/themes?audience_filter=...`
- `/api/runs/{id}/labels/summary`

### Slice D — UI integration

- Monitor labeling panel
- Themes filter selector
- excluded-by-label summary
- loading and partial-state UX

### Slice E — Backfill and observability

- label existing Phase 1 runs
- metrics:
  - job duration
  - AI failure rate
  - fallback rate
  - included/excluded ratios

---

## 13. Recommendation

Proceed với kiến trúc sau:

1. Keep crawl pipeline unchanged as much as possible
2. Add `label_jobs` and `content_labels` as a decoupled enrichment layer
3. Make theme filtering policy-driven at read time
4. Surface trust and exclusion details in UI

Đây là hướng có chi phí triển khai hợp lý nhất mà vẫn giữ được:
- correctness
- auditability
- khả năng re-label
- không phá vỡ core loop Phase 1
