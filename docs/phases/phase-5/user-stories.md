# User Stories — Phase 5: Resilient AI Routing & Release Notes
## AI Facebook Social Listening & Engagement v3

**Product:** AI-powered Facebook research and engagement assistant
**Primary users:** Researcher, Marketer, Sales/BD
**Language:** Vietnamese first, English supported
**Phase:** 5 — Resilient AI Routing & Release Notes
**Updated:** 2026-03-29

---

## Tại sao cần Phase 5

Phase 4 da dua UI ve dung shared shell, nhung 3 khoang trong van con ro:

- AI runtime van mac dinh theo Claude-only path, trong khi team muon uu tien endpoint marketplace OpenAI-compatible
- release note chua co cho end user, nen thay doi theo phase dang bi giu trong docs/noi bo
- ten shell chua phan anh phase hien hanh, nen user khong nhin thay nhan dien phien ban dang dung

Phase 5 giai quyet bai toan reliability + communication cua mot phase ship duoc.

---

## Cross-Cutting Rules

**R-50 — Centralize provider routing**  
Moi AI service phai di qua `AIClient`. Khong service nao tu goi provider rieng.

**R-51 — Timeout-only fallback**  
Claude chi duoc goi khi request marketplace bi timeout. Loi auth, 4xx, 5xx, hay response malformed khong tu dong doi provider tru khi do la buoc JSON repair da duoc route qua abstraction chung.

**R-52 — Phase artifacts are source-driven**  
Release note page phai lay noi dung tu artifact phase trong repo, khong viet text release note truc tiep trong component.

**R-53 — Shell naming follows current phase**  
Ten hien thi trong shell phai duoc derive tu current phase metadata, khong hard-code.

---

## User Stories

### US-50: Default AI Requests Use Marketplace Endpoint

**As a** product/runtime owner  
**I want** every normal AI request to use the marketplace OpenAI-compatible endpoint by default  
**So that** the app follows the subscribed marketplace model path without rewriting each AI service

**Acceptance Criteria:**

- Given an AI-capable service calls `AIClient`
  When provider credentials for the marketplace endpoint are configured
  Then the request is sent to `https://llm.chiasegpu.vn/v1/chat/completions`

- Given the request reaches the marketplace endpoint
  When the payload is built
  Then it uses the OpenAI-compatible chat completions shape with `model`, `messages`, and `stream=false`

- Given the marketplace call succeeds
  When the response returns
  Then the existing planner/insight/labeling flows keep receiving parsed JSON output without service-level changes

- Given the marketplace key is missing
  When Claude credentials are available
  Then the app may use Claude directly as the only configured provider instead of failing at boot

**Out of scope:**
- Per-feature provider selection UI
- Streaming UI
- Multi-provider load balancing

---

### US-51: Retry to Claude Only on Timeout

**As a** runtime engineer  
**I want** Claude retry to happen only when the marketplace request times out  
**So that** fallback stays predictable and does not hide other classes of integration failure

**Acceptance Criteria:**

- Given the marketplace request exceeds the configured timeout
  When `AIClient` detects the timeout
  Then it retries once through the existing Claude path

- Given the marketplace request fails with a non-timeout error
  When the error is returned
  Then `AIClient` does not silently switch providers and the error surfaces normally

- Given the marketplace request times out and Claude is available
  When the retry succeeds
  Then downstream services still receive a normal parsed payload

- Given neither marketplace nor Claude is configured
  When the app runs in local dev mode
  Then mock responses continue to work as before

**Out of scope:**
- Automatic retry loops beyond one timeout fallback
- Fallback on validation/auth/rate-limit errors

---

### US-52: Publish End-User Release Notes Per Phase

**As an** end user  
**I want** to open release notes for the current phase from inside the app  
**So that** I understand what changed, why it matters, and what to expect next

**Acceptance Criteria:**

- Given a phase has locked user stories
  When the phase artifact is prepared
  Then it includes a release note payload that can be rendered by the frontend

- Given the shell is loaded
  When release notes are available for the current phase
  Then the header shows a link to the release note page

- Given I open the release note link
  When the page renders
  Then I see a professional layout with headline, summary, highlights, and user-facing details

- Given a phase has no release note artifact
  When the frontend asks for it
  Then the UI degrades gracefully instead of crashing

**Out of scope:**
- WYSIWYG release note editor
- Public marketing site outside the app shell

---

### US-53: Show Phase-Aware Product Name In Shell

**As a** repeat user  
**I want** the shell title to show the active phase number  
**So that** I can immediately tell which milestone build I am using

**Acceptance Criteria:**

- Given `.phase.json` marks `phase-5` as current
  When the shell loads
  Then the product name displays as `Social Listening v3.5`

- Given the current phase changes in metadata later
  When the UI reads runtime metadata again
  Then the displayed name updates without hard-coding a new string in the component

- Given the browser tab title is set
  When phase metadata is available
  Then the title also reflects the current phase display name

**Out of scope:**
- Semantic versioning overhaul
- Distinct branding per page/module
