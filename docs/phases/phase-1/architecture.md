# Architecture — Phase 1: Safe Core Loop
## AI Facebook Social Listening & Engagement v3

**Phase:** 1 — Safe Core Loop
**Stories covered:** US-00, US-01, US-02, US-03a, US-03b, US-04L
**Updated:** 2026-03-28
**Status:** Draft — cần sign-off trước Sprint 1A

---

## 1. Constraints & Non-Functional Requirements

### Hard constraints (không thương lượng)

| Constraint | Nguồn | Ảnh hưởng kiến trúc |
|-----------|-------|---------------------|
| Personal Facebook account, không có API | Bản chất sản phẩm | Bắt buộc dùng browser automation |
| Mọi write action phải có human approval | R-01, R-02 | ApprovalGrant phải là backend record, không phải client flag |
| Safety stop ngay lập tức khi detect risk signal | R-03 | Safety monitor phải chạy trên thread/process riêng, không bị block bởi crawl |
| Plan definition ≠ plan execution | R-04 | Hai bảng/models riêng biệt ngay từ đầu |
| PII masking trước khi persist | R-06 | Mask tại tầng storage, không phải tầng display |
| Phase 1 policy: opaque_id only | OQ-3 | Không lưu display name, Facebook user ID chỉ lưu dạng hash |

### Non-functional requirements (Phase 1)

| NFR | Target | Ghi chú |
|-----|--------|---------|
| Single user | 1 concurrent session | Multi-user là Phase 2+ |
| Desktop-only | macOS / Windows | Mobile deferred (OQ-2 answered: desktop-only Phase 1) |
| Offline-capable | App chạy được khi không có internet (ngoại trừ AI calls và Facebook) | Local DB |
| Durability | Plan run state survive app crash | StepRun.checkpoint phải được flush trước khi bắt đầu step |
| Safety latency | CAPTCHA detection → write stop < 500ms | Safety monitor không polling, event-driven |
| AI cost per run | < $0.10 cho plan generation + theme analysis | Model selection per task |

---

## 2. Distribution Model Decision

**Quyết định: Local Server + Browser UI (không phải full Electron)**

Lý do chọn thay vì Electron:

```
Option A: Electron
  ✓ Bundle thành .app dễ distribute
  ✗ Camoufox trong Electron phức tạp sandbox permissions
  ✗ Build pipeline nặng, chậm iterate

Option B: Local Server + Web UI (CHỌN)
  ✓ Python backend chạy local (localhost:8000)
  ✓ Camoufox chạy tự nhiên không bị sandbox
  ✓ Web UI mở trong user's Chrome — dễ debug
  ✓ Dev cycle nhanh hơn nhiều
  ✗ User cần start server thủ công (acceptable cho Phase 1 internal tool)

Option C: SaaS hosted
  ✗ Facebook session không thể live trên server (personal account)
  ✗ PDP Law compliance phức tạp hơn
  ✗ Overkill cho Phase 1
```

**Topology Phase 1:**

```
User's Machine
├── Python Backend (FastAPI @ localhost:8000)
│   ├── API routes
│   ├── Plan/Run engine
│   ├── AI service (Claude API client)
│   └── SQLite DB (local file)
├── Camoufox Browser (Firefox-patched, headless optional)
│   └── Facebook session (logged in manually by user)
└── Web UI (served by FastAPI @ localhost:8000/ui)
    └── React SPA
```

---

## 3. System Architecture

### Layer Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     WEB UI (React SPA)                           │
│         localhost:8000/ui — served bởi FastAPI static            │
└─────────────────────────┬────────────────────────────────────────┘
                          │ HTTP + WebSocket (SSE)
┌─────────────────────────▼────────────────────────────────────────┐
│                    FastAPI Application                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Plan Router  │  │ Run Router   │  │ Health Router          │  │
│  │ POST /plans  │  │ POST /runs   │  │ GET /health/status     │  │
│  │ GET /plans   │  │ GET /runs/{} │  │ POST /health/reset     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘  │
│         │                 │                       │               │
│  ┌──────▼─────────────────▼───────────────────────▼────────────┐ │
│  │                   Service Layer                              │ │
│  │  PlannerService  │  RunnerService  │  HealthMonitorService  │ │
│  └──────┬─────────────────┬───────────────────────┬────────────┘ │
│         │                 │                       │               │
│  ┌──────▼─────────────────▼───────────────────────▼────────────┐ │
│  │                 Infrastructure Layer                         │ │
│  │  AIClient  │  BrowserAgent  │  Repository  │  EventBus      │ │
│  └──────┬─────────────────┬───────────────────────────────────┘  │
└─────────┼─────────────────┼────────────────────────────────────────┘
          │                 │
    Claude API         Camoufox
    (external)         (local Firefox-patched)
                            │
                      Facebook.com
```

### Module Responsibilities

| Module | Responsibility | Stories |
|--------|---------------|---------|
| `PlannerService` | Generate keywords, create plan, versioning | US-01, US-02 |
| `ApprovalService` | Issue ApprovalGrant, validate before run | US-03a |
| `RunnerService` | Orchestrate step execution, checkpoint, pause/resume | US-03b |
| `HealthMonitorService` | Passive signal detection, status machine, safety stop | US-00 |
| `InsightService` | Theme classification, PII masking, quote extraction | US-04L |
| `BrowserAgent` | Camoufox wrapper: login check, feed crawl, action execution | US-03b, US-04L |
| `AIClient` | Claude API wrapper: prompt assembly, ProductContext injection, streaming | US-01, US-02, US-04L |
| `Repository` | SQLite CRUD, migrations, opaque_id hashing | All |
| `EventBus` | In-process async event dispatch (asyncio) | US-00, US-03b |

---

## 4. Data Models (Full Schema)

### 4.1 Core Tables

```sql
-- ProductContext: AI memory per research session
CREATE TABLE product_contexts (
  context_id        TEXT PRIMARY KEY,  -- slug: tpbank-evo-2026-03
  topic             TEXT NOT NULL,
  status            TEXT NOT NULL CHECK(status IN ('clarification_required','keywords_ready')),
  keyword_json      TEXT,              -- JSON: {brand:[], pain_points:[], ...}
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Plans: versioned research plans
CREATE TABLE plans (
  plan_id           TEXT PRIMARY KEY,
  context_id        TEXT NOT NULL REFERENCES product_contexts(context_id),
  version           INTEGER NOT NULL DEFAULT 1,
  status            TEXT NOT NULL CHECK(status IN ('draft','ready','archived')),
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- PlanSteps: ordered steps in a plan
CREATE TABLE plan_steps (
  step_id           TEXT PRIMARY KEY,
  plan_id           TEXT NOT NULL REFERENCES plans(plan_id),
  plan_version      INTEGER NOT NULL,
  step_order        INTEGER NOT NULL,
  action_type       TEXT NOT NULL CHECK(action_type IN (
                      'CRAWL_FEED','JOIN_GROUP','CRAWL_COMMENTS',
                      'CRAWL_GROUP_META','SEARCH_GROUPS'
                    )),
  read_or_write     TEXT NOT NULL CHECK(read_or_write IN ('READ','WRITE')),
  target            TEXT NOT NULL,       -- group_id or search_query
  estimated_count   INTEGER,
  estimated_duration_sec INTEGER,
  risk_level        TEXT NOT NULL CHECK(risk_level IN ('LOW','MEDIUM','HIGH')),
  dependency_step_ids TEXT DEFAULT '[]'  -- JSON array of step_ids
);

-- ApprovalGrants: backend-issued approval records
CREATE TABLE approval_grants (
  grant_id          TEXT PRIMARY KEY,
  plan_id           TEXT NOT NULL REFERENCES plans(plan_id),
  plan_version      INTEGER NOT NULL,
  approved_step_ids TEXT NOT NULL,       -- JSON array
  approver_id       TEXT NOT NULL DEFAULT 'local_user',
  approved_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at        DATETIME,
  invalidated_at    DATETIME,            -- set when plan is re-edited after approval
  invalidated_reason TEXT
);

-- PlanRuns: execution instances
CREATE TABLE plan_runs (
  run_id            TEXT PRIMARY KEY,
  plan_id           TEXT NOT NULL REFERENCES plans(plan_id),
  plan_version      INTEGER NOT NULL,
  grant_id          TEXT NOT NULL REFERENCES approval_grants(grant_id),
  status            TEXT NOT NULL CHECK(status IN (
                      'RUNNING','PAUSED','DONE','FAILED','CANCELLED'
                    )),
  started_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at          DATETIME,
  total_records     INTEGER DEFAULT 0
);

-- StepRuns: per-step execution state
CREATE TABLE step_runs (
  step_run_id       TEXT PRIMARY KEY,
  run_id            TEXT NOT NULL REFERENCES plan_runs(run_id),
  step_id           TEXT NOT NULL REFERENCES plan_steps(step_id),
  status            TEXT NOT NULL CHECK(status IN (
                      'PENDING','RUNNING','DONE','FAILED','SKIPPED'
                    )),
  started_at        DATETIME,
  ended_at          DATETIME,
  actual_count      INTEGER,
  error_message     TEXT,
  checkpoint_json   TEXT,               -- JSON blob, enough to resume
  retry_count       INTEGER DEFAULT 0
);

-- CrawledPosts: raw crawled content (PII-masked)
CREATE TABLE crawled_posts (
  post_id           TEXT PRIMARY KEY,   -- opaque hash of FB post URL
  step_run_id       TEXT NOT NULL REFERENCES step_runs(step_run_id),
  group_id_hash     TEXT NOT NULL,      -- opaque hash of group ID
  content_masked    TEXT NOT NULL,      -- PII-masked post text
  posted_at         DATETIME,
  reaction_count    INTEGER DEFAULT 0,
  comment_count     INTEGER DEFAULT 0,
  is_excluded       BOOLEAN DEFAULT FALSE,
  exclude_reason    TEXT,               -- 'spam'|'seller_noise'|'irrelevant'
  crawled_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ThemeResults: US-04L output
CREATE TABLE theme_results (
  theme_id          TEXT PRIMARY KEY,
  run_id            TEXT NOT NULL REFERENCES plan_runs(run_id),
  label             TEXT NOT NULL CHECK(label IN (
                      'pain_point','positive_feedback','question',
                      'comparison','other'
                    )),
  dominant_sentiment TEXT NOT NULL CHECK(dominant_sentiment IN (
                      'positive','negative','neutral'
                    )),
  post_count        INTEGER NOT NULL,
  sample_quotes     TEXT NOT NULL,      -- JSON array, max 3 quotes, PII-masked
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- AccountHealthLog: audit trail of health events
CREATE TABLE account_health_log (
  log_id            TEXT PRIMARY KEY,
  signal_type       TEXT NOT NULL CHECK(signal_type IN (
                      'CAPTCHA','ACTION_BLOCKED','RATE_LIMIT',
                      'REDUCED_REACH','SESSION_EXPIRED','MANUAL_RESET'
                    )),
  status_before     TEXT NOT NULL,
  status_after      TEXT NOT NULL,
  detected_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  action_taken      TEXT,
  cooldown_until    DATETIME,
  raw_signal        TEXT               -- JSON, non-PII debug info
);

-- AccountHealthState: current health + session state (singleton table)
CREATE TABLE account_health_state (
  id                INTEGER PRIMARY KEY DEFAULT 1,  -- always 1 row
  status            TEXT NOT NULL CHECK(status IN ('HEALTHY','CAUTION','BLOCKED')),
  session_status    TEXT NOT NULL CHECK(session_status IN (
                      'NOT_SETUP','VALID','EXPIRED'
                    )) DEFAULT 'NOT_SETUP',
  account_id_hash   TEXT,             -- HMAC-SHA256 của FB user ID, null until first login
  last_checked      DATETIME,
  cooldown_until    DATETIME,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Entity Relationship

```
product_contexts
    │ 1
    │ N
  plans ────── plan_steps (versioned)
    │ 1             │
    │               │ referenced by
  approval_grants   │
    │ 1             │
    │               │
  plan_runs ─────────
    │ 1
    │ N
  step_runs
    │ 1
    │ N
  crawled_posts
        │ (aggregated into)
  theme_results (1 per run)

account_health_state (singleton)
account_health_log (append-only audit)
```

---

## 5. API Contracts

### 5.1 Browser Session API

```
GET /api/browser/status
Response: {
  session_status: "NOT_SETUP" | "VALID" | "EXPIRED",
  account_id_hash: string | null,   -- opaque, never display name
  health_status: "HEALTHY" | "CAUTION" | "BLOCKED",
  cooldown_until: ISO8601 | null
}
-- UI polls này khi app khởi động để biết có cần show setup screen không

POST /api/browser/setup
Response: { ok: true }
-- Triggers wait_for_login(): mở browser visible, poll until is_logged_in() == true
-- Blocking SSE stream (dùng /api/browser/setup/stream) hoặc poll /api/browser/status

GET /api/browser/setup/stream
Content-Type: text/event-stream
Events:
  browser_opened:   {}
  login_detected:   { account_id_hash: string }
  setup_complete:   { session_status: "VALID" }
  setup_failed:     { reason: string }
-- UI subscribe stream này để update realtime trong setup screen
```

### 5.2 Health Monitor API

```
GET  /api/health/status
Response: {
  status: "HEALTHY" | "CAUTION" | "BLOCKED",
  cooldown_until: ISO8601 | null,
  last_signal: {type, detected_at} | null
}

POST /api/health/acknowledge
Body: { signal_log_id: string }
Response: { ok: true }

POST /api/health/reset
Body: { confirm: true }
Response: { status: "HEALTHY" }
-- Chỉ available khi cooldown đã hết
```

### 5.2 Planning API

```
POST /api/sessions
Body: { topic: string }
Response: {
  context_id: string,
  status: "clarification_required" | "keywords_ready",
  clarifying_questions: string[] | null,
  keywords: {
    brand: string[],
    pain_points: string[],
    sentiment: string[],
    behavior: string[],
    comparison: string[]
  } | null
}

PATCH /api/sessions/{context_id}/keywords
Body: { keywords: KeywordMap }
Response: { context_id, status: "keywords_ready", keywords: KeywordMap }

POST /api/plans
Body: { context_id: string }
Response: {
  plan_id: string,
  version: 1,
  steps: PlanStep[],
  estimated_total_duration_sec: number,
  warnings: string[]
}

PATCH /api/plans/{plan_id}
Body: { instruction: string }
-- Natural language refinement, e.g. "chỉ crawl 2 groups"
Response: {
  plan_id: string,
  version: number,      -- tăng lên
  steps: PlanStep[],
  diff_summary: string  -- "Reduced from 5 to 2 groups"
}
```

### 5.3 Approval API

```
POST /api/plans/{plan_id}/approve
Body: {
  plan_version: number,
  approved_step_ids: string[]
}
Response: {
  grant_id: string,
  approved_at: ISO8601,
  expires_at: ISO8601 | null
}
-- 400 nếu account status != HEALTHY và có write steps
-- 400 nếu plan_version không khớp với latest version
-- 400 nếu approved_step_ids empty

GET /api/plans/{plan_id}/approval
Response: {
  grant_id: string | null,
  is_valid: boolean,
  invalidated_reason: string | null
}
```

### 5.4 Execution API

```
POST /api/runs
Body: { grant_id: string }
Response: {
  run_id: string,
  status: "RUNNING",
  steps: StepRunSummary[]
}

GET /api/runs/{run_id}
Response: {
  run_id, plan_id, status,
  steps: StepRunDetail[],
  started_at, ended_at | null,
  summary: ExecutionSummary | null
}

POST /api/runs/{run_id}/pause
Response: { run_id, status: "PAUSED" }

POST /api/runs/{run_id}/resume
Response: { run_id, status: "RUNNING" }

POST /api/runs/{run_id}/steps/{step_run_id}/retry
Response: { step_run_id, status: "PENDING" }

POST /api/runs/{run_id}/stop
Response: { run_id, status: "CANCELLED" }

-- Real-time updates via SSE:
GET /api/runs/{run_id}/stream
Content-Type: text/event-stream
Events:
  step_started:     { step_run_id, step_id, action_type }
  step_done:        { step_run_id, actual_count }
  step_failed:      { step_run_id, error_message }
  run_paused:       { run_id, reason }
  safety_stop:      { run_id, signal_type }
  session_expired:  { run_id }   -- run tự pause, chờ user re-login
  run_done:         { run_id, summary }
```

### 5.5 Insight API (US-04L)

```
GET /api/runs/{run_id}/themes
Response: {
  run_id: string,
  posts_crawled: number,
  posts_excluded: number,
  themes: [
    {
      theme_id: string,
      label: "pain_point"|"positive_feedback"|"question"|"comparison"|"other",
      dominant_sentiment: "positive"|"negative"|"neutral",
      post_count: number,
      sample_quotes: string[],  -- max 3, PII-masked
    }
  ],
  warning: string | null  -- "< 10 posts, results may not be representative"
}
```

---

## 6. Module Design

### 6.1 HealthMonitorService

State machine với 3 trạng thái:

```
HEALTHY ──[detect CAPTCHA]──────────────────────────────────→ BLOCKED
   │                                                              │
   │──[detect ACTION_BLOCKED]──────────────────────────────→ CAUTION
   │                                                              │
   │──[detect RATE_LIMIT]──────────────────────────────────→ CAUTION
   │                                                              │
   └────────────────────────────────[cooldown expires]───────────┘
```

**Implementation design:**

```python
class HealthMonitorService:
    # Chạy trong asyncio background task, KHÔNG blocking RunnerService
    # Nhận events từ BrowserAgent qua asyncio Queue

    async def start(self):
        # Subscribe to browser events
        self._task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self):
        async for event in self._browser_event_queue:
            signal = self._classify_signal(event)
            if signal:
                await self._transition(signal)

    async def _transition(self, signal: HealthSignal):
        new_status = self._state_machine(self.current_status, signal)
        await self._persist_state(new_status, signal)
        await self._emit_event(HealthChangedEvent(new_status, signal))
        # EventBus.emit() sẽ trigger RunnerService.emergency_stop()

    def is_write_allowed(self) -> bool:
        return self.current_status == HealthStatus.HEALTHY
```

**Signal sources từ BrowserAgent:**
- HTTP response headers: `x-fb-debug`, rate-limit patterns
- DOM detection: CAPTCHA overlay selector, action-blocked dialog
- Session errors: login page redirect → `SESSION_EXPIRED` signal → run pauses, UI prompts re-login

### 6.2 PlannerService + AIClient

**Flow US-01 (Keyword analysis):**

```
User input: "Khách hàng nghĩ gì về TPBank EVO?"
    ↓
PlannerService.analyze_topic(topic)
    ↓
AIClient.call(
  model="claude-opus-4-6",
  system=KEYWORD_SKILL_PROMPT,  -- includes Vietnamese NLP instructions
  user=topic,
  thinking={"type": "adaptive"}
)
    ↓ (nếu ambiguous)
Return {status: "clarification_required", questions: [...]}
    ↓ (nếu clear)
Return {status: "keywords_ready", keywords: KeywordMap}
    ↓
Repository.create_product_context(context_id, topic, keywords)
```

**Flow US-02 (Plan generation):**

```
PlannerService.generate_plan(context_id)
    ↓
context = Repository.get_product_context(context_id)
    ↓
AIClient.call(
  model="claude-opus-4-6",
  system=PLAN_SKILL_PROMPT,
  user=f"Context: {context.keyword_json}\nGenerate research plan",
  thinking={"type": "adaptive"},
  streaming=True  -- plan có thể dài
)
    ↓
Parse AI response → List[PlanStep]
    ↓
Repository.create_plan(plan_id, steps)  -- với schema PlanStep đã lock
```

**ProductContext injection vào AI calls:**

```python
KEYWORD_SKILL_PROMPT = """
Bạn là AI assistant giúp researcher phân tích thị trường qua Facebook Groups tại Việt Nam.

NHIỆM VỤ: Phân tích topic và gợi ý keywords để tìm kiếm và phân loại posts trên Facebook.

NGUYÊN TẮC VIETNAMESE NLP:
- Luôn bao gồm cả dạng có dấu và không dấu
- Nhận diện slang: "ok bạn", "tốt lắm", "chán vl", "hàng xịn"
- Buying intent patterns: "ship không", "ib mình nhé", "còn hàng không", "giá bao nhiêu vậy"
- Phân biệt buyer comment vs seller post

OUTPUT FORMAT (JSON):
{
  "status": "clarification_required" | "keywords_ready",
  "clarifying_questions": [...] | null,
  "keywords": {
    "brand": [...],
    "pain_points": [...],
    "sentiment": [...],
    "behavior": [...],
    "comparison": [...]
  } | null
}
"""
```

### 6.3 RunnerService

**Execution loop design:**

```python
class RunnerService:
    def __init__(self, health_monitor: HealthMonitorService, ...):
        # Subscribe to health events
        event_bus.subscribe(HealthChangedEvent, self._on_health_changed)

    async def start_run(self, grant_id: str) -> PlanRun:
        grant = await self._validate_grant(grant_id)
        run = await repo.create_plan_run(grant)
        asyncio.create_task(self._execute_run(run))
        return run

    async def _execute_run(self, run: PlanRun):
        steps = await repo.get_approved_steps(run)
        for step in steps:
            if self._is_paused or self._is_cancelled:
                break
            if not await self._can_execute_step(step):
                await repo.mark_step_skipped(step)
                continue
            await self._execute_step(step, run)

    async def _execute_step(self, step: PlanStep, run: PlanRun):
        step_run = await repo.create_step_run(step, run)
        try:
            # Checkpoint: persist state TRƯỚC khi bắt đầu
            await repo.update_step_checkpoint(step_run, self._build_checkpoint(step))

            # Safety check: write actions cần HEALTHY
            if step.read_or_write == 'WRITE':
                if not health_monitor.is_write_allowed():
                    raise SafetyStopException("Account not HEALTHY")

            result = await browser_agent.execute_step(step)
            await repo.complete_step_run(step_run, result)
        except SafetyStopException as e:
            await repo.fail_step_run(step_run, str(e))
            await self._emergency_stop(run, reason=str(e))
        except Exception as e:
            await repo.fail_step_run(step_run, str(e))
            await self._emit_step_failed(step_run, e)

    async def _on_health_changed(self, event: HealthChangedEvent):
        # Triggered ngay lập tức khi health monitor detect risk
        if event.new_status in (CAUTION, BLOCKED):
            await self._emergency_stop_write_actions()
```

**Checkpoint design cho resume:**

```python
# Checkpoint lưu đủ state để BrowserAgent biết tiếp tục từ đâu
# Ví dụ cho CRAWL_FEED step:
{
  "step_type": "CRAWL_FEED",
  "target_group_id_hash": "abc123",
  "posts_collected_ids": ["hash1", "hash2", ...],  # đã crawl
  "last_scroll_position": 1500,                    # pixel
  "next_cursor": "fb_pagination_token_xyz",
  "target_count": 50,
  "collected_count": 23
}
```

### 6.4 BrowserAgent

**Camoufox** wrapper với 4 trách nhiệm.

**Tại sao Camoufox thay vì Playwright thuần:**

| | Playwright (Chromium) | Camoufox |
|--|----------------------|----------|
| Engine | Chromium | Firefox (patched) |
| Canvas fingerprint | Bị detect | Randomized per session |
| WebGL fingerprint | Bị detect | Patched |
| AudioContext fingerprint | Exposed | Patched |
| navigator.webdriver | Thường bị leak | Removed |
| Font fingerprinting | Standard Chromium fonts | Randomized |
| Meta AI classifier (2025) | HIGH risk | LOWER risk |
| API compatibility | Playwright API | Playwright-like async API |

Meta dùng AI classifier từ 2025, **Chromium automation bị detect với false-positive rate cao**. Camoufox được thiết kế specifically cho use case này.

```python
from camoufox.async_api import AsyncCamoufox
from pathlib import Path
import hmac, hashlib, asyncio

BROWSER_PROFILE_DIR = Path.home() / ".social-listening" / "browser_profile"

class BrowserAgent:
    def __init__(self, event_queue: asyncio.Queue):
        self._browser: AsyncCamoufox | None = None
        self._page = None
        self._event_queue = event_queue

    async def start(self):
        # user_data_dir = persistent Firefox profile
        # Session (cookies, localStorage) tồn tại qua các lần restart app
        BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        self._browser = AsyncCamoufox(
            headless=False,                          # visible — user thấy được browser
            geoip=True,                              # locale/timezone từ IP thực
            humanize=True,                           # human-like mouse/keyboard delays
            user_data_dir=str(BROWSER_PROFILE_DIR),  # persistent profile
        )
        await self._browser.__aenter__()
        self._page = await self._browser.new_page()
        await self._page.route("**/*", self._on_route)

    # 1. Session management
    async def is_logged_in(self) -> bool:
        await self._page.goto("https://www.facebook.com")
        # Login button present → not logged in
        return await self._page.locator('[data-testid="royal_login_button"]').count() == 0

    async def wait_for_login(self) -> str:
        """First-run setup: chờ user tự đăng nhập. Trả về account_id_hash."""
        await self._page.goto("https://www.facebook.com")
        # Poll until home feed accessible (login button gone)
        while not await self.is_logged_in():
            await asyncio.sleep(2)
        # Extract opaque fingerprint — never store raw user ID
        fb_uid = await self._page.evaluate(
            "() => document.cookie.match(/c_user=(\\d+)/)?.[1] ?? ''"
        )
        account_id_hash = hmac.new(
            _load_local_secret(), fb_uid.encode(), hashlib.sha256
        ).hexdigest()
        return account_id_hash

    async def assert_session_valid(self) -> None:
        """Gọi trước mỗi step. Nếu session hết hạn → emit event, raise."""
        if not await self.is_logged_in():
            await self._event_queue.put(HealthSignal.SESSION_EXPIRED)
            raise SessionExpiredException("Facebook session expired — run paused")

    # 2. Signal emission (feeds HealthMonitorService)
    async def _on_route(self, route):
        response = await route.fetch()
        await route.fulfill(response=response)
        if self._detect_captcha_in_response(response):
            await self._event_queue.put(HealthSignal.CAPTCHA)
        elif self._detect_action_blocked(response):
            await self._event_queue.put(HealthSignal.ACTION_BLOCKED)

    # 3. Read actions (safe, no approval needed)
    async def crawl_feed(self, group_id: str, target_count: int,
                         checkpoint: dict | None) -> List[RawPost]:
        ...

    # 4. Write actions (only called after grant validation)
    async def join_group(self, group_id: str, grant_id: str) -> None:
        # Validates grant trước khi thực hiện
        # Nếu health != HEALTHY → raises SafetyStopException
        ...

    async def stop(self):
        if self._browser:
            await self._browser.__aexit__(None, None, None)
```

**Rate limiting trong BrowserAgent:**

```python
RATE_LIMITS = {
    "CRAWL_FEED": RateLimit(max_per_hour=10, min_delay_sec=5),
    "JOIN_GROUP": RateLimit(max_per_day=3, min_delay_sec=30),
    "CRAWL_COMMENTS": RateLimit(max_per_hour=20, min_delay_sec=3),
}

async def _throttled_action(self, action_type: str, fn: Callable):
    limit = RATE_LIMITS[action_type]
    await self._rate_limiter.acquire(action_type)
    delay = limit.min_delay_sec + random.uniform(0, limit.min_delay_sec * 0.5)
    await asyncio.sleep(delay)  # Human-like jitter
    return await fn()
```

### 6.5 InsightService (US-04L)

```python
class InsightService:
    async def analyze_themes(self, run_id: str) -> ThemeAnalysis:
        # 1. Load crawled posts
        posts = await repo.get_posts_for_run(run_id)

        # 2. Pre-filter spam/seller noise (rule-based, không cần AI)
        clean_posts, excluded = self._filter_noise(posts)

        # 3. Warn nếu quá ít posts
        if len(clean_posts) < 10:
            warning = "Ít hơn 10 posts — kết quả có thể chưa đại diện"
        else:
            warning = None

        # 4. Batch classify với claude-haiku-4-5 (cheaper, sufficient)
        # Single call returns both theme label AND dominant_sentiment per theme
        themes = await ai_client.classify_themes(
            posts=clean_posts,
            model="claude-haiku-4-5",  # classification task, không cần Opus
            taxonomy=["pain_point","positive_feedback","question","comparison","other"],
            include_sentiment=True,    # returns dominant_sentiment: positive|negative|neutral
        )

        # 5. PII mask quotes trước khi lưu
        for theme in themes:
            theme.sample_quotes = [pii_masker.mask(q) for q in theme.sample_quotes]

        # 6. Persist
        await repo.save_theme_results(run_id, themes)
        return ThemeAnalysis(themes=themes, warning=warning, excluded_count=len(excluded))

    def _filter_noise(self, posts) -> Tuple[List, List]:
        # Rule-based: detect seller posts, spam patterns
        # Patterns: price listing format, multiple emoji, contact info heavy
        SELLER_PATTERNS = [
            r'\d+[kK]\s*/', r'inbox|ib|pm|zalo',
            r'(giá|price|bán|sell).*\d+',
        ]
        ...
```

**PII Masker:**

```python
class PIIMasker:
    PATTERNS = {
        'phone': r'(?:0|\+84)\d{9,10}',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'cccd':  r'\b\d{9}(?:\d{3})?\b',
        'fb_uid': r'(?:uid|id)[:=]\s*\d{10,}',
    }

    def mask(self, text: str) -> str:
        for name, pattern in self.PATTERNS.items():
            text = re.sub(pattern, f'[{name}_masked]', text)
        return text
```

---

## 7. Event System

Phase 1 dùng **in-process asyncio event bus** (không phải Redis). Đơn giản, zero dependencies, đủ cho single-user tool.

```python
# Events được định nghĩa rõ ràng, không phải string
@dataclass
class HealthChangedEvent:
    new_status: HealthStatus
    signal_type: str
    cooldown_until: datetime | None

@dataclass
class StepStartedEvent:
    run_id: str
    step_run_id: str

@dataclass
class StepCompletedEvent:
    run_id: str
    step_run_id: str
    actual_count: int

@dataclass
class SafetyStopEvent:
    run_id: str
    signal_type: str
    stopped_steps: List[str]

# EventBus
class EventBus:
    _subscribers: Dict[Type, List[Callable]] = {}

    def subscribe(self, event_type: Type, handler: Callable):
        ...

    async def emit(self, event):
        for handler in self._subscribers.get(type(event), []):
            await handler(event)
```

**Subscriptions Phase 1:**

| Publisher | Event | Subscriber | Action |
|-----------|-------|-----------|--------|
| BrowserAgent | `HealthSignal` | HealthMonitorService | State transition |
| BrowserAgent | `SESSION_EXPIRED` | RunnerService | Pause run, set `session_status=EXPIRED` |
| BrowserAgent | `SESSION_EXPIRED` | SSE endpoint | Push `session_expired` event to UI |
| HealthMonitorService | `HealthChangedEvent` | RunnerService | Emergency stop writes |
| HealthMonitorService | `HealthChangedEvent` | SSE endpoint | Push to UI |
| RunnerService | `StepCompletedEvent` | SSE endpoint | Push to UI |
| RunnerService | `SafetyStopEvent` | SSE endpoint | Push alert to UI |

---

## 8. Technology Stack

### Quyết định stack Phase 1

| Layer | Choice | Lý do |
|-------|--------|-------|
| Backend language | **Python 3.12** | Claude API SDK mature, Playwright support tốt, team familiar |
| Web framework | **FastAPI** | Async native, SSE support built-in, auto OpenAPI docs |
| Database | **SQLite** (via SQLAlchemy) | Single-user, zero-config, file-based (portable) |
| Browser automation | **Camoufox** (Python) | Firefox-based, anti-fingerprinting built-in, thiết kế cho scraping stealthy |
| AI SDK | **anthropic** Python SDK | Official, streaming + adaptive thinking support |
| Frontend | **React + Vite** | Served as static files bởi FastAPI |
| Real-time | **SSE** (Server-Sent Events) | Simpler than WebSocket cho one-direction updates |
| Dependency injection | **dependency-injector** | Testable services |
| Migrations | **Alembic** | SQLAlchemy-native, reproducible schema |

### Không dùng trong Phase 1

| Rejected | Lý do |
|----------|-------|
| Redis | Single-user không cần external broker |
| Celery | Asyncio đủ cho sequential task runner |
| PostgreSQL | Overkill cho single-user local tool |
| WebSocket | SSE đủ vì UI chỉ nhận data, không gửi ngược |
| Docker | Overhead không cần thiết cho dev phase |
| **Playwright thuần** | Chromium bị Meta AI classifier detect cao; không có built-in fingerprint patching |

### File structure

```
social-listening-v3/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entry
│   │   ├── api/
│   │   │   ├── health.py         # Health monitor routes
│   │   │   ├── plans.py          # Plan + keyword routes
│   │   │   ├── runs.py           # Execution routes
│   │   │   └── insights.py       # Theme results routes
│   │   ├── services/
│   │   │   ├── health_monitor.py # US-00
│   │   │   ├── planner.py        # US-01, US-02
│   │   │   ├── approval.py       # US-03a
│   │   │   ├── runner.py         # US-03b
│   │   │   └── insight.py        # US-04L
│   │   ├── infra/
│   │   │   ├── ai_client.py      # Claude API wrapper
│   │   │   ├── browser_agent.py  # Camoufox wrapper
│   │   │   ├── pii_masker.py     # PII masking
│   │   │   ├── event_bus.py      # In-process events
│   │   │   └── repository.py     # SQLite CRUD
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic request/response
│   │   └── skills/               # AI prompt templates
│   │       ├── keyword_analysis.md
│   │       ├── plan_generation.md
│   │       └── theme_classification.md
│   ├── alembic/                  # DB migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── KeywordPage.tsx   # US-01
│   │   │   ├── PlanPage.tsx      # US-02
│   │   │   ├── ApprovePage.tsx   # US-03a
│   │   │   ├── MonitorPage.tsx   # US-03b
│   │   │   └── ThemesPage.tsx    # US-04L
│   │   └── components/
│   │       └── HealthBadge.tsx   # US-00 status indicator
│   └── package.json
└── docs/
    └── phases/phase-1/
        ├── user-stories.md       # (existing)
        └── architecture.md       # (this file)
```

---

## 9. AI Integration Design

### Model selection per task

| Task | Model | Lý do | Avg tokens | Est. cost |
|------|-------|-------|-----------|-----------|
| US-01: Keyword analysis | `claude-opus-4-6` + adaptive thinking | Vietnamese NLP cần reasoning tốt | ~3K in, ~1K out | ~$0.04 |
| US-02: Plan generation | `claude-opus-4-6` + adaptive thinking + streaming | Multi-step planning | ~5K in, ~2K out | ~$0.075 |
| US-04L: Theme classification | `claude-haiku-4-5` | Batch classification, cost-sensitive | ~10K in, ~500 out | ~$0.013 |
| US-04L: Spam filter | Rule-based regex | No AI needed | — | $0 |

**Prompt caching strategy:**

```
Cached (stable across calls):
├── system prompt (Vietnamese NLP instructions)   ~2K tokens → cache
├── ProductContext (keyword_json per session)      ~1K tokens → cache per session
└── Theme taxonomy definition                      ~500 tokens → cache

Not cached (varies per call):
└── User input / posts batch
```

Cache tại system prompt breakpoint:
```python
messages.create(
  model="claude-opus-4-6",
  system=[{
    "type": "text",
    "text": SKILL_PROMPT + PRODUCT_CONTEXT,
    "cache_control": {"type": "ephemeral"}  # 5-min TTL default
  }],
  messages=[{"role": "user", "content": user_input}]
)
```

---

## 10. Security & Safety Design

### Write Action Guard (layered defense)

```
Layer 1 — UI: Write action steps visually disabled khi health != HEALTHY
    ↓
Layer 2 — API: POST /plans/{id}/approve returns 400 nếu health != HEALTHY và có write steps
    ↓
Layer 3 — ApprovalService: Validate grant chưa bị invalidated
    ↓
Layer 4 — RunnerService: Check health trước mỗi write step
    ↓
Layer 5 — BrowserAgent: Final check trước khi execute action
```

Nếu bất kỳ layer nào fail → stop, không fallthrough.

### Approval Grant Invalidation

```python
# Tình huống khiến grant bị invalidated:
def invalidate_grant_if_needed(plan_id: str, new_version: int):
    grant = repo.get_valid_grant(plan_id)
    if grant and grant.plan_version != new_version:
        repo.invalidate_grant(grant.grant_id, reason="plan_edited_after_approval")
        # User phải approve lại
```

### Browser Profile Security

```
~/.social-listening/
├── browser_profile/      ← Firefox profile: chứa FB session cookies
│   ├── cookies.sqlite    ← session cookies (sensitive)
│   └── ...
├── app.db                ← SQLite DB (chứa account_id_hash, không có plaintext)
└── .secret               ← OPAQUE_ID_SECRET (local-only, không bao giờ commit)
```

**Quy tắc bắt buộc:**
- `browser_profile/` và `.secret` phải được `.gitignore`
- App không bao giờ đọc `cookies.sqlite` trực tiếp — chỉ Camoufox/Firefox mới đọc
- `account_id_hash` trong DB: HMAC của `c_user` cookie value — không reversible
- Nếu user muốn "đăng xuất": xóa `browser_profile/` → session mất, DB còn nguyên

### PII Data Flow

```
Facebook DOM
    ↓ (raw HTML)
BrowserAgent.parse_posts()
    ↓ (RawPost với FB user info)
PIIMasker.mask()              ← PII removed HERE, trước khi đi vào bất cứ đâu
    ↓ (MaskedPost)
Repository.save_post()        ← chỉ lưu masked content
    ↓
AIClient (theme classification) ← chỉ nhận masked content
    ↓
ThemeResult.sample_quotes     ← already masked
    ↓
API Response                  ← no PII ever reaches client
```

**opaque_id generation:**

```python
import hashlib, hmac

SECRET_KEY = os.environ["OPAQUE_ID_SECRET"]  # local .env

def make_opaque_id(fb_identifier: str) -> str:
    # HMAC-SHA256 để không reversible nhưng consistent
    return hmac.new(
        SECRET_KEY.encode(),
        fb_identifier.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
```

---

## 11. Trade-off Analysis

### T1: SQLite vs PostgreSQL

**Chọn SQLite cho Phase 1**

| | SQLite | PostgreSQL |
|--|--------|------------|
| Setup | Zero config | Requires server |
| Single user | Perfect fit | Overkill |
| Concurrent writes | Not needed Phase 1 | Needed Phase 2+ |
| Migration path | Alembic hỗ trợ cả hai | — |
| Phase 2 cost | ~1 week migrate | — |

Quyết định: SQLite Phase 1, migrate sang PostgreSQL khi multi-user (Phase 2+). Alembic schema đảm bảo migration sạch.

### T2: In-process EventBus vs Redis Pub/Sub

**Chọn in-process asyncio cho Phase 1**

Redis Pub/Sub sẽ cần thiết khi:
- Nhiều worker processes (Phase 2+ với multi-account)
- Event durability (business-critical events như `variant_approved`)

Phase 1: 1 process, sequential runner → in-process đủ và đơn giản hơn nhiều.

### T3: SSE vs WebSocket

**Chọn SSE cho Phase 1**

- UI chỉ cần nhận status updates từ server (one-direction)
- SSE simpler, works over HTTP/1.1, auto-reconnect built-in browsers
- WebSocket khi cần bidirectional (Phase 3+ engage flow)

### T4: Camoufox vs Playwright thuần

**Chọn Camoufox**

Playwright thuần (Chromium) có các fingerprinting vectors mà Meta's AI classifier (2025+) đã được training để detect:
- `navigator.webdriver = true` trong Chromium automation
- Chromium-specific canvas/WebGL fingerprint patterns
- Inconsistent audio context fingerprint
- Predictable timing patterns

Camoufox patches Firefox ở mức binary để:
- Remove tất cả automation markers
- Randomize fingerprinting vectors per session
- Apply human-like timing trên DOM interactions (khi `humanize=True`)

**Trade-off:**
- Camoufox dùng Firefox, không phải Chrome. Nếu Facebook có behavior khác nhau giữa Firefox và Chrome → cần test
- API tương thích với Playwright Python → migration risk thấp
- `pip install camoufox` + `python -m camoufox fetch` để download patched Firefox binary (~100MB one-time)

### T5: Polling vs Event-driven cho Health Monitor

**Chọn event-driven (không phải polling)**

Polling mỗi N giây sẽ:
- Miss CAPTCHA signal nếu xảy ra giữa 2 polls
- Tạo delay trong safety stop

Event-driven từ Camoufox response interceptor (`page.route`):
- Detect ngay lập tức khi Facebook response chứa signal
- Zero polling overhead

---

## 12. Implementation Slices

### Sprint 1A — Safety Infra + Planning Foundation

**Slice 1A.0 — Schema Lock (blocker)**
```
Deliverable: Alembic migration files cho tất cả tables
Acceptance: `alembic upgrade head` chạy sạch, tất cả tables exist
Owner: Tech Lead
Duration: 1 day
```

**Slice 1A.1 — HealthMonitorService + BrowserAgent skeleton**
```
Deliverable:
  - BrowserAgent.is_logged_in()
  - Signal emission từ response interceptor
  - HealthMonitorService state machine
  - AccountHealthState persisted trong SQLite
  - GET /api/health/status trả về đúng trạng thái
Test: Manual — start app, trigger "action blocked" DOM, verify status → CAUTION
Duration: 2 days
```

**Slice 1A.2 — AIClient + PlannerService (US-01)**
```
Deliverable:
  - AIClient.call() với adaptive thinking + streaming
  - KEYWORD_SKILL_PROMPT với Vietnamese NLP rules
  - PlannerService.analyze_topic()
  - POST /api/sessions
  - PATCH /api/sessions/{id}/keywords
Test: curl POST /api/sessions với topic tiếng Việt → nhận keywords JSON
Duration: 2 days
```

**Slice 1A.3 — Plan Generation (US-02)**
```
Deliverable:
  - PLAN_SKILL_PROMPT
  - PlannerService.generate_plan()
  - PlanStep schema validated
  - POST /api/plans
  - PATCH /api/plans/{id} (natural language refinement)
Test: POST /api/plans → nhận plan với steps đúng format
Duration: 2 days
```

### Sprint 1B — Approval Gate + Execution Loop

**Slice 1B.1 — ApprovalService (US-03a)**
```
Deliverable:
  - ApprovalService.issue_grant()
  - Grant invalidation khi plan re-edited
  - POST /api/plans/{id}/approve
  - 400 nếu health != HEALTHY + write steps present
Test: Approve plan → grant_id in DB. Edit plan → grant invalidated.
Duration: 1.5 days
```

**Slice 1B.2 — RunnerService core (US-03b)**
```
Deliverable:
  - RunnerService._execute_run() với step loop
  - Pause / Resume logic
  - Emergency stop khi HealthChangedEvent received
  - StepRun checkpoint flush
  - POST /api/runs, POST /api/runs/{id}/pause, resume, stop
Test: Start run → pause → resume → steps complete in order
Duration: 3 days
```

**Slice 1B.3 — SSE streaming**
```
Deliverable:
  - GET /api/runs/{id}/stream (SSE)
  - Events: step_started, step_done, step_failed, safety_stop, run_done
  - UI MonitorPage connects to SSE, shows real-time step updates
Duration: 1 day
```

**Slice 1B.4 — BrowserAgent CRAWL_FEED**
```
Deliverable:
  - BrowserAgent.crawl_feed() với checkpoint support
  - Rate limiting + human-like delays
  - CAPTCHA/signal detection
Test: Crawl 1 real group → posts in crawled_posts table, PII masked
Duration: 3 days (highest risk slice)
```

### Sprint 1C — First Visible Output

**Slice 1C.1 — InsightService (US-04L)**
```
Deliverable:
  - InsightService.analyze_themes() với claude-haiku-4-5
  - Spam/noise filter (rule-based)
  - PII masking trước khi save
  - GET /api/runs/{id}/themes
  - UI ThemesPage với 5 theme buckets
Test: Run crawl → analyze → see themes with quotes in UI
Duration: 2 days
```

**Slice 1C.2 — End-to-end smoke test**
```
Deliverable: Demo script chạy full flow:
  1. Enter topic → keywords
  2. Generate plan (read-only, no JOIN_GROUP)
  3. Approve plan
  4. Run → crawl 1 group
  5. View themes
Acceptance: Full flow chạy được trong 1 session, không crash, không ban account
Duration: 1 day (soak test với real account)
```

---

## 13. Open Questions với Architecture Answers

| OQ | Quyết định architecture |
|----|------------------------|
| OQ-1: Multi-account Phase 1? | **Không.** Single account. `approver_id` hardcoded `local_user`. Account abstraction layer được thiết kế nhưng không implement. |
| OQ-2: Mobile support? | **Không, desktop-only Phase 1.** Camoufox chạy trên user's desktop machine. Document rõ trong README. |
| OQ-3: Privacy policy? | **opaque_id only.** Display name không bao giờ được lưu. HMAC-SHA256 với local secret key. |
| OQ-4: AI model? | Opus 4.6 cho planning (needs reasoning). Haiku 4.5 cho classification (cost). Xem Section 9. |
| OQ-5: Rate limits? | Defaults: CRAWL_FEED 10/hour, JOIN_GROUP 3/day. Configurable trong `config.json`. |
| OQ-6: Distribution? | **Local server + Web UI.** Xem Section 2. |
| OQ-7: Account warm-up? | 14-day soak test với read-only actions trước khi enable JOIN_GROUP. Protocol trong `docs/safety-protocol.md`. |
