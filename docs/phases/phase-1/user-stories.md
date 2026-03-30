# User Stories — Phase 1: Safe Core Loop
## AI Facebook Social Listening & Engagement v3

**Product:** AI-powered Facebook research and engagement assistant
**Account type:** Personal Facebook account (non-business)
**Primary users:** Researcher, Marketer, Sales/BD
**Language:** Vietnamese first, English supported
**Phase:** 1 — Safe Core Loop
**Updated:** 2026-03-28

---

## Tại sao Phase 1 được re-scope từ v2

Phase 1 trong v2 kết thúc ở US-03b — toàn bộ là planning infrastructure, không có visible output cho user.
Phân tích critical thinking xác định 2 rủi ro lớn:

1. **Không có first value** — sau Sprint 1, user chạy plan nhưng không nhận insight hay lead nào.
2. **Account health không được build sớm** — nếu account bị ban trong tuần đầu, toàn bộ progress mất.

Phase 1 v3 được re-frame thành: **"Prove the core loop works safely and delivers first visible value."**

---

## Phase 1 Scope

```
PLAN                    SAFETY               FIRST VALUE
─────────────────────────────────────────────────────────────
US-01 Keyword analysis  US-00 Account health  US-04L Feed crawl
US-02 Generate plan                            + theme list
US-03a Approve plan
US-03b Monitor run
```

**Sprint phân bổ:**

| Sprint | Stories | Focus |
|--------|---------|-------|
| Sprint 1A | US-00, US-01, US-02 | Safety infra + planning foundation |
| Sprint 1B | US-03a, US-03b | Approval gate + execution loop |
| Sprint 1C | US-04L | First visible output — crawl + themes |

---

## Cross-Cutting Implementation Rules

Áp dụng cho tất cả stories trong Phase 1, không có exception.

**R-01 — Write action definition**
Bất kỳ action nào thay đổi state trên Facebook là write action.
Write actions Phase 1 bao gồm ít nhất: `JOIN_GROUP`.
Mọi write action đều phải có explicit human approval trước khi execute.

**R-02 — Approval contract**
Approval không được biểu diễn chỉ bằng client boolean.
Mọi approval phải là backend-issued `ApprovalGrant` ghi lại: `approver_id`, `approved_at`, `plan_version`, `approved_step_ids`, `content_hash` (nếu có).

**R-03 — Safety stop**
Khi phát hiện CAPTCHA, action-blocked response, hoặc account-risk signal:
Dừng toàn bộ pending write actions ngay lập tức.
Không có exception. Không có "retry sau 1 giây".

**R-04 — Plan/run separation**
Plan definition và plan execution là hai records riêng biệt.
Chỉnh sửa plan không được mutate execution history.

**R-05 — Vietnamese NLP**
Mọi AI output liên quan đến keyword, intent, theme phải hỗ trợ:
- Tiếng Việt có và không dấu
- Slang thông dụng của seller VN
- Buying-intent patterns: "ship không", "ib mình nhé", "còn hàng không", "cho mình xin sdt"

**R-06 — PII masking**
Crawled content được coi là sensitive data.
Phone numbers, email, CMND/CCCD patterns phải được mask trước khi persist hoặc hiển thị.
Phase 1 policy: chỉ lưu `opaque_id`, không lưu display name.

---

## Schema Contracts — Phải lock trước khi code US-02

Đây là deliverable của Sprint 1A, không phải implementation note.
Nếu schema chưa được sign off, không bắt đầu code US-02 trở đi.

```
PlanStep {
  step_id: string         -- stable, never changes after creation
  action_type: enum       -- CRAWL_FEED | JOIN_GROUP | CRAWL_COMMENTS | ...
  read_or_write: enum     -- READ | WRITE
  target: string          -- group_id hoặc search_query
  estimated_count: int
  estimated_duration_sec: int
  risk_level: enum        -- LOW | MEDIUM | HIGH
  dependency_step_ids: string[]
}

PlanRun {
  run_id: string
  plan_id: string
  plan_version: int
  approval_grant_id: string
  started_at: timestamp
  ended_at: timestamp | null
  status: enum            -- RUNNING | PAUSED | DONE | FAILED | CANCELLED
}

StepRun {
  step_run_id: string
  run_id: string
  step_id: string
  status: enum            -- PENDING | RUNNING | DONE | FAILED | SKIPPED
  started_at: timestamp | null
  ended_at: timestamp | null
  actual_count: int | null
  error_message: string | null
  checkpoint: json | null  -- state đủ để resume
}

ApprovalGrant {
  grant_id: string
  plan_id: string
  plan_version: int
  approved_step_ids: string[]
  approver_id: string
  approved_at: timestamp
  expires_at: timestamp | null
}
```

---

## User Stories

---

### US-00: Account Session & Health Monitor (Safety Infrastructure)

**As a** researcher
**I want** to connect my own Facebook account once and have the app monitor it for risk signals automatically
**So that** my account is never put at risk by the tool — and I don't have to log in again every time I open the app

> **Note:** Đây là safety infrastructure, không phải optional feature.
> US-00 phải hoàn thành trước khi bất kỳ story nào khác có thể chạy write actions.

**Acceptance Criteria:**

**Session Setup (first run)**

- Given the app is launched for the first time (no saved session)
  When the setup screen is displayed
  Then the app opens a visible Firefox browser window và hướng dẫn user: "Vui lòng đăng nhập Facebook trong cửa sổ này. App sẽ tự động tiếp tục sau khi đăng nhập thành công."

- Given the user has completed Facebook login in the browser window
  When the app detects a valid session (home feed accessible)
  Then the app saves an opaque fingerprint of the account (`account_id_hash`), shows "Đã kết nối — sẵn sàng để dùng", và không bao giờ lưu credentials hoặc tên tài khoản

- Given a session has been saved previously
  When the app is launched again
  Then the app reuses the saved browser profile — user không cần đăng nhập lại

**Session Recovery (expiry mid-run)**

- Given a plan run is in progress
  When the browser detects a login redirect (session expired)
  Then the run is paused immediately, user sees: "Phiên đăng nhập Facebook đã hết hạn — vui lòng đăng nhập lại để tiếp tục"
  And after the user re-logs in the browser, they can resume the run từ checkpoint cuối cùng

- Given the app starts and the saved session is no longer valid
  When `is_logged_in()` returns false
  Then the app shows the setup screen lại — không tự động proceed với session không hợp lệ

**Health Monitoring**

- Given the app is running and a Facebook session is active
  When no risk signals are present
  Then the account status indicator shows `Healthy` và không có interruption nào xảy ra

- Given the app is running
  When a CAPTCHA challenge appears in the session
  Then all pending write actions stop immediately, the user sees an alert: "CAPTCHA detected — all write actions paused", và app không tự động retry

- Given the app is running
  When an "action blocked" response is received from Facebook
  Then write actions stop, user sees the specific block message, và app đề xuất cooling period (ví dụ: "Chờ 24h trước khi thử lại")

- Given the app is idle (no plan running)
  When a passive health check detects reduced reach or rate-limit headers
  Then the status indicator changes to `Caution` và user receives a non-intrusive notification

- Given the account status is `Caution` or `Blocked`
  When the user tries to approve a write action step
  Then the system blocks the action and shows: "Account health status must be Healthy before write actions can proceed"

- Given the account health status changes
  When any status transition occurs
  Then the event is logged with: signal_type, detected_at, action_taken, và cooldown_until (nếu có)

**Out of scope:**
- Auto-fill credentials hoặc bất kỳ form của login automation (tool không được chạm vào credentials)
- Automatic account recovery
- Multi-account switching (Phase 2+)
- Email/Slack notifications (Phase 3+)

**Dependencies:** None (foundation layer)

**Notes:**
- Session được persist qua Firefox profile directory (`~/.social-listening/browser_profile/`). App không bao giờ đọc hoặc lưu username/password — chỉ reuse cookies do browser tự lưu.
- `account_id_hash` = HMAC-SHA256 của Facebook user ID (lấy từ DOM sau login), dùng để detect nếu account khác đăng nhập vào cùng profile.
- Health check chạy passive — detect từ response headers và DOM signals, không phải polling API.
- Cooldown period mặc định: 24h cho CAPTCHA, 1h cho action-blocked.
- Status phải persist qua app restart — nếu đóng app lúc account đang `Blocked`, mở lại vẫn còn `Blocked` cho đến khi cooldown hết.

---

### US-01: Enter a Topic and Get Keyword Analysis

**As a** researcher
**I want to** enter a natural-language research topic
**So that** AI suggests relevant keywords before any crawling starts, và tôi không bắt đầu crawl với keywords sai

**Acceptance Criteria:**

- Given I open the app and no research session is active
  When I enter a topic such as "Khách hàng nghĩ gì về TPBank EVO?"
  Then the system returns at least 10 suggested keywords grouped into categories: brand, pain points, sentiment, behavior, comparison

- Given AI returns a keyword set
  When I want to adjust it
  Then I can add, remove, or edit individual keywords before confirming — changes persist in session

- Given I enter a topic in Vietnamese
  When AI generates suggestions
  Then the result includes cả dạng có dấu lẫn không dấu (ví dụ: "dịch vụ" và "dich vu"), slang phổ biến, và informal buying-intent phrases nếu relevant

- Given the topic is too broad or ambiguous (ví dụ: "bán hàng")
  When AI processes it
  Then AI returns clarifying questions thay vì generate keywords ngay — ví dụ: "Bạn đang nghiên cứu sản phẩm cụ thể nào? Đối tượng khách hàng là ai?"

- Given I confirm the keyword set
  When I proceed
  Then the system initializes a `ProductContext` với topic và confirmed keywords, và trạng thái chuyển sang `keywords_ready`

- Given AI cannot generate meaningful keywords for a topic
  When processing fails
  Then user sees a clear error — không phải empty list im lặng

**Out of scope:**
- Automatically starting crawling after topic submission
- Saving topics for reuse across sessions (Phase 2+)

**Dependencies:** US-00 (session phải healthy trước khi initialize ProductContext)

**Notes:**
- Output contract hai trạng thái: `clarification_required` | `keywords_ready`
- Keyword output phải structured và exportable (JSON minimum)
- ProductContext từ US-01 là shared context cho tất cả downstream stories trong session

---

### US-02: Generate a Research Plan

**As a** researcher
**I want to** receive a detailed research plan after confirming keywords
**So that** I know exactly what the system will do, where it will look, và how much risk it carries — before anything runs

**Acceptance Criteria:**

- Given I have confirmed keywords from US-01
  When AI generates a research plan
  Then the plan lists ordered steps với: action_type, read_or_write classification, target group/query, estimated_count, estimated_duration, risk_level, dependency_step_ids

- Given the plan is generated
  When I review it
  Then write action steps (như `JOIN_GROUP`) được visually highlighted và labeled "⚠ Write Action — requires approval"

- Given I want to narrow or expand the scope
  When I describe the change in natural language (ví dụ: "chỉ crawl 2 groups thôi")
  Then AI returns an updated plan version mà không mất prior context, và version number tăng

- Given AI cannot find relevant groups for the topic
  When it tries to build the plan
  Then it returns warnings và alternative approach — không trả về empty plan

- Given the plan is finalized
  When I click "Proceed to Review"
  Then the plan is saved với a stable plan_id và version number, sẵn sàng cho US-03a

**Out of scope:**
- Executing the plan automatically after generation
- Scheduling recurring plan runs (Phase 3+)

**Dependencies:** US-01

**Notes:**
- Plan phải dùng schema `PlanStep` đã được lock (xem Schema Contracts section)
- Plan phải versioned — mỗi edit tạo plan version mới, không overwrite
- Estimated scope giúp user judge risk: "~50 posts from 3 groups" rõ ràng hơn "crawl groups"

---

### US-03a: Review and Approve a Plan

**As a** researcher
**I want to** review the generated plan and explicitly approve which steps will run
**So that** I understand and authorize exactly what the assistant will do with my Facebook account

> **Note:** Đây là safety gate quan trọng nhất trong sản phẩm. Approval screen phải feel như **confirmation**, không phải bureaucracy. Target: user có thể review và approve trong dưới 30 giây.

**Acceptance Criteria:**

- Given a plan has been generated from US-02
  When I open the review screen
  Then I see a checklist của plan steps với: action name, one-line description, read/write classification, estimated scope, risk level

- Given I want to skip some steps
  When I uncheck them
  Then only checked steps are eligible for execution, và system warns nếu dependencies would break (ví dụ: "Step 3 phụ thuộc Step 2 — nếu bỏ Step 2, Step 3 sẽ bị skip tự động")

- Given the plan contains write actions (JOIN_GROUP hoặc tương tự)
  When those steps are displayed
  Then they are visually distinguished — icon, color, hoặc label rõ ràng

- Given I click "Approve and Run" với ít nhất một step được chọn
  When I confirm
  Then the system creates an `ApprovalGrant` record với: approver_id, approved_at, plan_id, plan_version, approved_step_ids — và chuyển sang execution monitoring

- Given I click "Approve and Run" nhưng không có step nào được chọn
  When the action is triggered
  Then button is disabled hoặc system shows: "Chọn ít nhất một bước để tiếp tục"

- Given I want to edit the plan before running
  When I click "Edit Plan"
  Then I return to plan editing mà không mất current draft

- Given account health status is not `Healthy` (US-00)
  When I try to approve a plan containing write actions
  Then write action steps are disabled và system shows: "Không thể approve write actions khi account đang bị hạn chế"

**Out of scope:**
- Reusable saved approval templates
- Recurring scheduled approvals
- Approval by multiple users (single-user tool, Phase 1)

**Dependencies:** US-01, US-02, US-00

**Notes:**
- Approval phải produce backend-issued `ApprovalGrant` — không phải chỉ flip một boolean
- Không có "approve all without review" shortcut
- Plan version phải khớp giữa `ApprovalGrant` và `PlanRun` — nếu plan bị edit sau khi approve, approval grant bị invalidated

---

### US-03b: Monitor Plan Execution

**As a** researcher
**I want to** monitor a running plan in real time and intervene when needed
**So that** I always know what the system is doing and can stop or recover safely

**Acceptance Criteria:**

- Given a plan has been approved and started
  When I open the monitor screen
  Then I see all steps với statuses: `Pending` | `Running` | `Done` | `Failed` | `Skipped`, updated in near real time

- Given a step completes successfully
  When the status changes to `Done`
  Then I see actual output — ví dụ: "Crawled 47 posts from Group X"

- Given the run is in progress
  When I click `Pause`
  Then the system finishes the current atomic action safely và pauses before starting the next step

- Given the run is paused
  When I click `Resume`
  Then execution continues from the last incomplete step — không replay completed steps

- Given a step fails (rate limit, session expiry, Facebook error)
  When the failure is detected
  Then step is marked `Failed`, user sees specific error message, và available actions are: `Retry` | `Skip` | `Stop All`

- Given the run completes
  When all selected steps finish
  Then user sees execution summary: total steps, done count, failed count, skipped count, records processed, total duration

- Given the app closes or disconnects while a plan is running
  When the user returns
  Then the app restores last durable run state từ `StepRun.checkpoint` và hỏi: "Resume từ bước X?" hoặc "Cancel run này?"

- Given account health monitor (US-00) detects a risk signal while a run is active
  When the signal is confirmed
  Then all pending write actions stop immediately — không cần user action, không hỏi confirm

**Out of scope:**
- Unlimited automatic retries (max 1 manual retry per step)
- Parallel runs on the same Facebook account
- Email/Slack notifications (Phase 3+)

**Dependencies:** US-03a, US-00

**Notes:**
- `PlanRun` và `StepRun` phải dùng schema đã lock (xem Schema Contracts)
- Mỗi `StepRun` phải có `checkpoint` đủ để resume mà không cần re-crawl từ đầu
- Mọi step transition phải được logged với timestamp — không có state mất đi silently

---

### US-04L: Minimal Feed Crawl and Theme List (Phase 1 Lite)

**As a** researcher
**I want to** see a short list of themes — each with a sentiment label — from a Facebook group's recent posts
**So that** I have a first real output from the tool — and can quickly tell whether the conversation in a group is mostly positive, negative, or neutral before investing in deeper research

> **Note:** "L" = Lite. Đây là stripped-down version của US-04 (full insight analysis). Mục tiêu duy nhất: Phase 1 không kết thúc với empty result. Full US-04 với filtering, export, sentiment distribution thuộc Phase 2.

**Acceptance Criteria:**

- Given a plan run has completed at least one CRAWL_FEED step (from US-03b)
  When I open the results screen
  Then I see: number of posts crawled, top 5 themes found, và 1-2 representative quote per theme

- Given theme analysis is complete
  When I view the theme list
  Then each theme shows a dominant sentiment label: **Positive**, **Negative**, or **Neutral**
  And the label reflects the majority sentiment of posts classified under that theme

- Given crawled posts include spam or obvious seller noise
  When AI classifies them
  Then spam posts are excluded from theme list — và user sees "X posts excluded as seller noise"

- Given theme analysis is complete
  When I view a theme
  Then I can see the theme label và 2-3 raw post excerpts supporting it (PII-masked per R-06)

- Given the crawl returned fewer than 10 posts
  When theme analysis runs
  Then system shows a warning: "Ít hơn 10 posts — kết quả có thể chưa đại diện. Thử crawl thêm group." — nhưng vẫn hiển thị kết quả có được

- Given I want to see more detail on any theme
  When I click on it
  Then I see a note: "Full comment analysis available in Phase 2" — không bị broken UI

**Out of scope:**
- Sentiment distribution chart / breakdown percentages (Phase 2)
- Per-post sentiment classification (Phase 2)
- Per-post relevance scoring (Phase 2)
- Comment-level analysis (Phase 2 US-05)
- Export CSV (Phase 2)
- Real-time streaming analysis while crawling is in progress
- Filtering by theme or sentiment (Phase 2)

**Dependencies:** US-03b (phải có completed CRAWL_FEED step run)

**Notes:**
- Theme taxonomy: 5 default categories đủ cho Lite — pain_point, positive_feedback, question, comparison, other
- Sentiment per theme: một Haiku call phân loại cả theme label lẫn dominant_sentiment trong cùng 1 prompt — không cần call riêng
- `dominant_sentiment` = majority sentiment của posts trong theme đó (positive / negative / neutral)
- Quote output phải respect R-06 (PII masking) — không hiển thị phone number, email trong excerpts
- Đây là proof-of-value milestone, không phải production-ready feature

---

## Story Map

```
FOUNDATION           PLAN                 APPROVE & RUN        FIRST VALUE
────────────────     ────────────────     ────────────────     ────────────────
US-00               US-01               US-03a               US-04L
Account Health  →   Keyword Analysis →  Review & Approve  →  Feed Crawl
Monitor                                                       + Theme List
                    US-02
                    Generate Plan     →  US-03b
                                        Monitor Execution
```

---

## Recommended Sprint Breakdown

| Sprint | Stories | Deliverable |
|--------|---------|-------------|
| Sprint 1A | US-00, US-01, US-02 | Safety monitor chạy được + user có thể tạo plan |
| Sprint 1B | US-03a, US-03b | Full plan → approve → run loop |
| Sprint 1C | US-04L | First real output — themes từ real Facebook data |

**Sprint 1A gate:** Schema contracts (PlanStep, PlanRun, StepRun, ApprovalGrant) phải được sign off trước khi Sprint 1A done. Không bắt đầu Sprint 1B nếu schema chưa locked.

**Sprint 1C gate:** Account health monitor phải pass 2-week soak test (không có false bans) trước khi US-04L demo với real account.

---

## INVEST Check

| Story | I | N | V | E | S | T | Flag |
|-------|---|---|---|---|---|---|------|
| US-00 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| US-01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| US-02 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Estimable chỉ sau khi schema locked |
| US-03a | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Depends on US-02 schema |
| US-03b | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Needs durable StepRun checkpoint design |
| US-04L | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Scope rõ ràng nhờ "Lite" boundary |

---

## Out of Phase 1

Những feature sau đây **không thuộc Phase 1**. Không mở sprint cho các items này cho đến khi Phase 1 complete.

| Feature | Lý do defer | Phase đề xuất |
|---------|-------------|---------------|
| US-04 Full insight analysis (sentiment, filtering, export) | Phase 1 chỉ cần Lite để prove value | Phase 2 |
| US-05 Comment analysis | Phụ thuộc US-04 full | Phase 2 |
| US-06 Create group post | Cần write safety validated trước | Phase 3 |
| US-07 Suggest comments | Cần thread context model | Phase 3 |
| US-08a/b/c Sales workflow | Phụ thuộc toàn bộ Listen + Engage | Phase 4 |
| UC-A Group Quality Scoring | Analytics layer, phụ thuộc US-04 | Phase 2 |
| UC-B Buying Intent Detection | Vietnamese NLP cần validate trước | Phase 2/3 |
| UC-C Post Variation Generator | Phụ thuộc US-06 | Phase 3 |
| UC-E Peak Time Optimizer | Analytics layer, phụ thuộc crawl history | Phase 2 |
| UC-F Competitor Post Intelligence | Phụ thuộc US-04 | Phase 2/3 |
| UC-G Post Bump Strategy | Phụ thuộc UC-D + US-07 | Phase 3 |
| Multi-account support | Architecture decision chưa chốt (OQ-5) | Phase 2+ |
| Scheduled recurring plans | Infrastructure không cần cho Phase 1 | Phase 3+ |
| CRM export / Zalo integration | Out of product scope hiện tại | TBD |

---

## Open Questions — Cần Chốt Trước Sprint 1A

| # | Câu hỏi | Impact | Owner |
|---|---------|--------|-------|
| OQ-1 | Multi-account support có cần trong Phase 1 không? Sellers VN thường dùng 2-4 accounts. | Architecture | Product/Tech |
| OQ-2 | Tool chạy trên desktop browser hay cần mobile support? 96% FB users VN dùng mobile. | Platform scope | Product |
| OQ-3 | Privacy policy cho Phase 1: opaque_id only, hay có thể lưu display name encrypted? | Schema + Legal | Product/Legal |
| OQ-4 | AI model nào dùng cho keyword generation và theme classification? Cost envelope per run? | Infrastructure | Tech |
| OQ-5 | Safe rate limits mặc định là bao nhiêu? (posts/hour, joins/day) | Safety | Tech |
| OQ-6 | Distribution model: internal tool, managed SaaS, hay desktop app? Ảnh hưởng session management. | Architecture | Product/Legal |
| OQ-7 | Account warm-up protocol là gì trước khi test write actions? | Safety | Tech |

---

## Phân tích Assumptions Cần Validate Trước Khi Build

Dựa trên Assumption Mapping từ phân tích critical thinking.

**Tigers — Validate TRƯỚC Sprint 1B:**

| Assumption | Experiment tối thiểu |
|-----------|----------------------|
| User chịu được friction của review-before-run | Prototype clickable approval flow, test với 3 sellers, measure time-to-approve. Target: dưới 30 giây. |
| Browser automation không bị ban trong 2 tuần đầu | Chạy read-only session với 1 account test, rate limit tối thiểu, monitor liên tục 14 ngày trước khi cho user real account chạm vào tool. |
| Vietnamese NLP đủ tốt cho keyword + theme | Chạy 50 real Vietnamese group posts qua AI, measure: precision/recall của theme labels, % keyword suggestions user edit. |

**Elephants — Cần quyết định trước khi architect:**

| Blind spot | Quyết định cần đưa ra |
|-----------|----------------------|
| Mobile vs Desktop | Chốt ngay: desktop-only cho Phase 1 hay không? Nếu desktop-only, document rõ. |
| Multi-account | Hỏi 5 sellers "bạn dùng bao nhiêu Facebook account?". Nếu >1 account là norm, architecture cần session abstraction layer từ đầu. |
