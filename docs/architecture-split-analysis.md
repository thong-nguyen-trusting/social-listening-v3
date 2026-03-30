# Architecture Split Analysis: `social-listening-v3`

## 1. Scope

This document analyzes the current `social-listening-v3` codebase and proposes how to split the app into two separately deployable services:

1. `browser-worker` on a separate machine
2. `main-service` on the current machine

The target operating model is:

- `browser-worker` owns all Facebook browser automation, browser state, VNC/noVNC streaming, and Facebook session lifecycle.
- `main-service` owns FastAPI business APIs, React frontend, SQLite/app data, run orchestration, health views, labeling, and AI analysis.

## 2. Files Reviewed

The analysis is based on the current implementation in these areas:

- Container/runtime
  - `Dockerfile`
  - `docker-compose.yml`
  - `entrypoint.sh`
- Backend runtime and wiring
  - `backend/app/main.py`
  - `backend/app/infrastructure/lifespan.py`
  - `backend/app/infrastructure/config.py`
  - `backend/app/infrastructure/database.py`
- Browser automation and health
  - `backend/app/infra/browser_agent.py`
  - `backend/app/infra/event_bus.py`
  - `backend/app/infra/pii_masker.py`
  - `backend/app/api/browser.py`
  - `backend/app/api/health.py`
  - `backend/app/services/health_monitor.py`
- Plan/run orchestration and downstream processing
  - `backend/app/services/runner.py`
  - `backend/app/services/planner.py`
  - `backend/app/services/approval.py`
  - `backend/app/services/label_job_service.py`
  - `backend/app/services/insight.py`
  - `backend/app/domain/action_registry.py`
- Frontend
  - `frontend/src/lib/api.ts`
  - `frontend/src/App.tsx`
  - `frontend/src/app/shell/AppHeader.tsx`
  - `frontend/src/pages/SetupPage.tsx`
  - `frontend/src/pages/ApprovePage.tsx`
  - `frontend/src/pages/MonitorPage.tsx`
- Data model and tests/docs
  - `backend/app/models/health.py`
  - `backend/app/models/crawled_post.py`
  - `backend/tests/e2e_smoke.py`
  - `docs/phases/phase-1/architecture.md`
  - `docs/phases/phase-1/checkpoints/cp2-browser-session/README.md`
  - `docs/phases/phase-1/checkpoints/cp7-execution-engine/README.md`

## 3. Current Architecture Summary

### 3.1 Runtime topology today

The app is a single container that bundles:

- FastAPI backend
- built React frontend served as static files
- Camoufox browser runtime
- Xvfb virtual display
- x11vnc
- noVNC via websockify
- SQLite database and browser profile volume mounts

Startup flow in `entrypoint.sh`:

1. start Xvfb
2. start x11vnc on `:5900`
3. start noVNC on `:6080`
4. run Alembic migrations
5. start `uvicorn`

The Docker image explicitly installs browser-display dependencies and exposes both app and browser-view ports:

- `8000` for API/UI
- `6080` for noVNC browser view

### 3.2 Application topology today

At runtime, `backend/app/infrastructure/lifespan.py` instantiates everything in-process and stores them on `app.state`:

- `BrowserAgent`
- `HealthMonitorService`
- `PlannerService`
- `ApprovalService`
- `RunnerService`
- `LabelJobService`
- `InsightService`
- `AIClient`

Important consequence:

- Browser automation is not treated as an external dependency.
- It is an in-memory collaborator directly injected into `RunnerService`.
- Health monitoring also depends on in-process browser-originated signals via an asyncio queue.

### 3.3 Frontend topology today

The frontend is coupled only to the FastAPI backend, not directly to the browser runtime:

- `SetupPage.tsx` calls `/api/browser/status`, `/api/browser/setup`, `/api/browser/setup/stream`
- `ApprovePage.tsx` calls `/api/plans/.../approve` then `/api/runs`
- `MonitorPage.tsx` calls `/api/runs/...` and `/api/runs/.../stream`

This is favorable for the split because the browser worker can remain invisible to the frontend and be mediated by the main service.

## 4. Code Map: Browser vs Main Service Responsibilities

### 4.1 Browser-related code

These areas are strongly browser-runtime specific and belong in the future `browser-worker`:

#### Infrastructure and runtime

- `Dockerfile`
  - installs `xvfb`, `x11vnc`, `novnc`, `websockify`, GTK/X11 libs, Camoufox assets
- `docker-compose.yml`
  - maps browser profile volume
  - exposes noVNC port
  - sets browser-related env vars
- `entrypoint.sh`
  - starts Xvfb, VNC, noVNC

#### Browser automation

- `backend/app/infra/browser_agent.py`
  - owns persistent browser profile
  - starts/stops Camoufox
  - login detection via `c_user` cookie
  - manual login flow
  - Facebook group search
  - group join
  - join-status checks
  - public post search
  - comment crawling
  - in-group search
  - feed crawling
  - route interception for CAPTCHA/action-block/session-expired signals
  - HMAC hashing of FB account/group identifiers
  - URL normalization and content extraction
  - PII masking before content leaves browser collection methods

#### Browser setup API

- `backend/app/api/browser.py`
  - `/api/browser/status`
  - `/api/browser/setup`
  - `/api/browser/setup/stream`

This API is currently exposed by the monolith but semantically represents browser-worker control operations.

### 4.2 Main service code

These areas should stay on the future `main-service`:

- `backend/app/services/planner.py`
- `backend/app/services/approval.py`
- `backend/app/services/runner.py` as orchestrator, but with browser calls replaced by remote client calls
- `backend/app/services/label_job_service.py`
- `backend/app/services/insight.py`
- `backend/app/infra/ai_client.py`
- all SQLAlchemy models and migrations
- React frontend and static serving
- runtime metadata/release notes APIs

### 4.3 Shared/domain concepts

These concepts span both services:

- action types in `backend/app/domain/action_registry.py`
- account session state
- health/risk signals
- crawl result payload schemas
- run-step checkpoint semantics

These should become explicit API contracts instead of implicit in-process Python objects.

## 5. Current Coupling Analysis

### 5.1 Tight coupling: `RunnerService` -> `BrowserAgent`

The strongest coupling is `backend/app/services/runner.py`.

`RunnerService` directly invokes browser methods for every executable action:

- `search_groups`
- `crawl_feed`
- `join_group`
- `check_join_status`
- `search_posts`
- `crawl_comments`
- `search_in_group`

This means the current executor assumes:

- low-latency local method calls
- in-process exceptions
- single shared browser instance
- single shared browser session
- local mutable page/context state

To split the services, this direct dependency must be replaced with a network client abstraction such as `BrowserWorkerClient`.

### 5.2 Tight coupling: health signals are in-process events

Today:

- `BrowserAgent` emits `HealthSignal` objects into an in-memory asyncio queue
- `HealthMonitorService` consumes that queue and persists state into SQLite

This only works because browser runtime and health monitor share memory. Once browser moves out of process, health signals must be delivered over HTTP, SSE, or WebSocket, then re-persisted by `main-service`.

### 5.3 Tight coupling: startup lifecycle assumes one process

Today:

- `lifespan.py` instantiates `BrowserAgent` directly
- app startup owns browser setup hub and browser task state
- shutdown calls `browser_agent.stop()`

After the split:

- `main-service` should not own browser process lifecycle
- `browser-worker` should own its own startup/shutdown
- `main-service` should only own connectivity, status sync, and control requests

### 5.4 Tight coupling: browser setup state is app-local, not durable

`backend/app/api/browser.py` uses:

- `app.state.browser_setup_task`
- `BrowserSetupHub` subscriber queues

This works for one FastAPI process but is not durable or shareable across services. If the browser worker becomes a separate machine, setup progress must come from the worker itself or via a brokered stream.

### 5.5 Coupling through implicit data contracts

`BrowserAgent` returns Python dict shapes consumed directly by `RunnerService`.

Examples:

- `search_groups()` returns `groups` and `primary_group_id`
- `search_posts()` returns `posts` and `discovered_groups`
- `join_group()` returns `status`, `confirmed`, `can_access`, `privacy`
- `crawl_feed()` returns `RawPost[]`

These are de facto API contracts already, but they are undocumented and unversioned. Splitting the services requires formalizing them.

### 5.6 Coupling through checkpoint semantics

`RunnerService` stores step checkpoints in DB and passes checkpoint data into browser methods, especially `crawl_feed`.

This is good in one important way:

- resume logic is already persisted in the main DB, not in browser memory

But there is still an issue:

- the browser side does not have its own explicit job model or durable operation state
- if a long browser call dies mid-request, the only durable state is the main service checkpoint

That is acceptable for an MVP split, but not sufficient for robust distributed execution without retries/idempotency rules.

## 6. Data and State Boundaries Today

### 6.1 State that currently lives with the browser runtime

- Camoufox persistent profile directory
- Facebook cookies/session
- current page/context/browser instance
- Xvfb display state
- VNC/noVNC runtime
- route-interception-based health signal detection

### 6.2 State that currently lives in main DB

- account health state
- account health logs
- plans and plan steps
- approval grants
- plan runs and step runs
- crawled posts
- label jobs and labels
- theme results

### 6.3 Important observation

The app already persists crawl outputs, approvals, and execution state centrally in the main DB. That is a strong foundation for splitting the browser runtime out, because the worker does not need the main database to function if the main service stays the source of truth for business state.

## 7. Gaps and Constraints Discovered

### 7.1 Browser session persistence is partially implicit

The browser profile is persisted to disk, but `load_persisted_account_hash()` only restores a mock-session hash from a mock file. In real mode, startup does not re-check the persisted Facebook session automatically and restore `account_health_state.account_id_hash`.

Implication:

- the existing implementation does not fully separate "profile exists" from "session is validated and synchronized"
- the split should explicitly add a `sync session state from worker` behavior

### 7.2 Single-browser assumption

The current code assumes one browser context and effectively one Facebook account. That matches the product constraints, but it means the split should still stay single-tenant per worker initially.

### 7.3 SQLite remains local to main service

This is fine if:

- browser worker does not need direct DB access
- main service persists all outputs

This becomes a limitation only if the worker needs durable internal queues or multi-step recovery. For the proposed split, keep DB ownership in main service.

### 7.4 Existing API/UI do not expose browser video directly

The current UI starts setup but does not embed noVNC or explicitly present the worker browser URL. The browser view is accessible separately at port `6080`.

For the new requirement "viewable from mobile browser", a proper worker access URL must be exposed by the main service.

## 8. Proposed Target Architecture

### 8.1 Service boundaries

#### `main-service`

Responsibilities:

- serve React frontend
- serve public/backend APIs
- own SQLite and all business persistence
- own plans, approvals, run orchestration, checkpoints, labels, themes, AI calls
- own displayed health/session state for the product
- call browser-worker via authenticated API
- translate worker events/status into persisted health/session state

#### `browser-worker`

Responsibilities:

- own Camoufox/Playwright runtime
- own browser profile directory and Facebook cookies
- own Xvfb/VNC/noVNC or equivalent remote browser view stack
- expose authenticated control/status APIs
- execute browser actions requested by main-service
- emit or expose health/risk/session state
- optionally expose a signed noVNC/mobile viewer URL

### 8.2 High-level topology

```text
User Browser
  -> Main Service UI/API
       -> Browser Worker API
            -> Camoufox / Facebook
            -> Xvfb + x11vnc + noVNC

Main Service
  -> SQLite
  -> Anthropic / LLM provider

Browser Worker
  -> Persistent browser profile volume
```

### 8.3 Recommended integration style

Use synchronous request/response APIs for browser actions first, not a queue-based job system.

Reason:

- current `RunnerService` is sequential
- there is one account/browser
- step execution is already serialized
- a simple HTTP client can preserve current semantics with lower migration cost

Add timeouts, retries, and idempotency keys where needed.

Only introduce a distributed job queue if:

- multiple workers are needed
- steps become long-running enough that request timeouts are consistently a problem
- operator handoff/retry complexity becomes high

## 9. Proposed API Contract Between `main-service` and `browser-worker`

### 9.1 Design principles

- version every endpoint under `/api/v1`
- worker owns browser session and browser-view details
- main service owns business run IDs and step IDs
- payloads should be explicit JSON schemas, not loosely shaped dicts
- every mutating request should carry:
  - `request_id`
  - `run_id`
  - `step_id`
  - optional `idempotency_key`

### 9.2 Control and status endpoints

#### Session and status

`GET /api/v1/session`

Response:

```json
{
  "worker_status": "READY",
  "session_status": "VALID",
  "account_id_hash": "hex-hmac",
  "browser_view": {
    "viewer_url": "https://worker.example.com/view/abc",
    "expires_at": "2026-03-30T12:00:00Z"
  },
  "health": {
    "signal_status": "HEALTHY",
    "cooldown_until": null,
    "last_signal": null
  }
}
```

`POST /api/v1/session/setup`

Purpose:

- ensure browser is running
- open Facebook login form if needed
- return viewer metadata for operator login

Response:

```json
{
  "setup_state": "PENDING_LOGIN",
  "viewer_url": "https://worker.example.com/view/abc",
  "viewer_token_expires_at": "2026-03-30T12:00:00Z"
}
```

`GET /api/v1/session/setup/stream`

SSE events:

- `browser_opened`
- `login_detected`
- `session_valid`
- `session_expired`
- `setup_failed`

Main-service can proxy this stream to preserve the current frontend contract.

#### Health and events

`GET /api/v1/health`

Purpose:

- return worker-observed browser risk state

`GET /api/v1/events/stream`

Purpose:

- long-lived SSE stream for worker-originated events such as:
  - CAPTCHA
  - ACTION_BLOCKED
  - SESSION_EXPIRED
  - RATE_LIMIT

Main-service should subscribe and persist them into `account_health_log` and `account_health_state`.

### 9.3 Browser action endpoints

Recommended pattern:

`POST /api/v1/actions/{action_type}`

Headers:

- `Authorization: Bearer <worker-shared-secret-or-jwt>`
- `Idempotency-Key: <uuid>`

Request envelope:

```json
{
  "request_id": "req-123",
  "run_id": "run-abc",
  "step_id": "step-2",
  "checkpoint": {
    "phase": "running",
    "collected_count": 4
  },
  "payload": {
    "query": "tpbank evo",
    "target_count": 10
  }
}
```

Response envelope:

```json
{
  "request_id": "req-123",
  "status": "ok",
  "session_status": "VALID",
  "health_signals": [],
  "result": {
    "...": "action-specific payload"
  }
}
```

#### Action-specific payloads

`SEARCH_GROUPS`

Request payload:

```json
{
  "query": "tpbank evo",
  "target_count": 3
}
```

Response result:

```json
{
  "groups": [
    {
      "group_id": "12345",
      "name": "TPBank EVO Community",
      "privacy": "PUBLIC"
    }
  ],
  "primary_group_id": "12345"
}
```

`JOIN_GROUP`

Request payload:

```json
{
  "group_id": "12345"
}
```

Response result:

```json
{
  "group_id": "12345",
  "status": "requested",
  "confirmed": true,
  "privacy": "PRIVATE",
  "can_access": false,
  "action_labels": ["Pending"]
}
```

`CHECK_JOIN_STATUS`

Request payload:

```json
{
  "group_id": "12345"
}
```

`CRAWL_FEED`

Request payload:

```json
{
  "group_id": "12345",
  "target_count": 12,
  "checkpoint": {
    "collected_count": 4
  }
}
```

Response result:

```json
{
  "posts": [
    {
      "post_id": "opaque-post-id",
      "group_id_hash": "opaque-group-hash",
      "content": "masked content",
      "record_type": "POST",
      "source_url": "https://www.facebook.com/...",
      "parent_post_id": null,
      "parent_post_url": null,
      "posted_at": null,
      "reaction_count": 0,
      "comment_count": 0
    }
  ]
}
```

`SEARCH_POSTS`, `CRAWL_COMMENTS`, and `SEARCH_IN_GROUP` should mirror the current return shapes already used by `RunnerService`.

### 9.4 Proxy compatibility layer on `main-service`

To minimize frontend changes, keep these existing frontend-facing routes on main-service:

- `/api/browser/status`
- `/api/browser/setup`
- `/api/browser/setup/stream`

Internally, these become proxy/adaptor routes to the browser worker.

This keeps the React code largely unchanged.

## 10. Session and Cookie Handling

### 10.1 Recommended ownership model

The browser worker should be the sole owner of:

- browser profile directory
- Facebook cookies
- local storage/session storage
- any anti-bot/browser fingerprint state

Do not copy raw Facebook cookies back to main-service unless there is a strong operational need. The main service should only receive:

- `session_status`
- `account_id_hash`
- last validated timestamp
- signal/health summaries

Reason:

- smaller attack surface
- fewer secrets replicated across machines
- cleaner separation of responsibilities

### 10.2 Session identity

Preserve the current opaque-hash model:

- worker extracts `c_user`
- worker computes `account_id_hash` using shared HMAC secret or sends raw `c_user` only to main-service over mTLS and lets main-service hash it

Recommended:

- main-service remains canonical owner of the HMAC secret
- worker should avoid long-term ownership of the opaque-ID secret if possible

Practical options:

#### Option A: worker hashes locally

Pros:

- current implementation maps more directly

Cons:

- secret duplicated to worker

#### Option B: worker sends raw FB uid to main-service over secure channel, main hashes centrally

Pros:

- one canonical secret owner
- lower secret sprawl

Cons:

- raw uid crosses the network

Recommendation:

- for MVP, Option A is acceptable if worker is private and tightly controlled
- for stronger security posture, move to Option B or a derived-token design later

### 10.3 Session revalidation

Add an explicit worker boot flow:

1. worker starts browser profile
2. worker checks whether Facebook session is still valid
3. worker exposes current `session_status`
4. main-service syncs this state into `account_health_state`

This closes the current gap where real persisted sessions are not explicitly synchronized at startup.

### 10.4 Multiple accounts

Do not design for multi-account in the first split. Keep:

- one worker
- one browser profile
- one Facebook account

But make the API slightly future-proof by including:

- `worker_id`
- `session_id`

in responses.

## 11. Browser View Streaming to Mobile

### 11.1 Current mechanism

The current app already uses:

- Xvfb
- x11vnc
- noVNC/websockify

That is compatible with mobile browsers. noVNC is the simplest path to satisfy "viewable from mobile browser."

### 11.2 Recommended approach

Keep the same model on browser-worker:

- Xvfb display
- x11vnc attached to the display
- noVNC exposed over HTTPS

Expose a temporary viewer URL, ideally signed and expiring:

```text
https://browser-worker.example.com/view/<short-lived-token>
```

The main-service should surface this URL in the setup response and optionally the UI.

### 11.3 Security model for browser view

Do not expose a permanent open noVNC endpoint.

Recommended controls:

- HTTPS only
- short-lived signed view tokens
- per-session or per-setup token issuance
- optional IP allowlist or VPN
- optional basic auth in front of noVNC for defense in depth
- automatic token expiry after login/setup window

### 11.4 User experience recommendation

Add to setup flow:

- `browser_view_url`
- `browser_view_expires_at`
- a clear "Open browser worker" CTA

Optional improvement:

- embed the noVNC page inside an iframe in the main-service UI for desktop
- keep direct-link support for mobile browser use

## 12. Security Considerations

### 12.1 Service-to-service authentication

Minimum acceptable:

- shared bearer token between main-service and browser-worker

Recommended:

- mTLS between services if they are on private infrastructure
- otherwise signed JWTs with short TTL and audience restriction

### 12.2 Network exposure

Browser worker should not be publicly open except the secured browser-view path. Prefer:

- private network between services
- reverse proxy with strict ingress rules
- separate public path only for noVNC/mobile viewing if required

### 12.3 Secret placement

`main-service` should keep:

- Anthropic/API keys
- DB credentials
- app-level HMAC secret if possible

`browser-worker` should keep only:

- browser-view auth secrets
- service auth secret
- optional opaque-ID secret only if hashing remains local

Do not place Anthropic credentials on the browser worker.

### 12.4 Input hardening

All worker action endpoints should validate:

- allowed action type
- payload schema
- maximum target counts
- timeout budgets
- allowed URL domains when passing URLs back into browser navigation

### 12.5 Result sanitization

The current implementation already masks PII before persistence-oriented results are returned. Keep this invariant:

- browser worker must only return masked text content to main-service
- raw personally identifiable text should not cross the service boundary

### 12.6 Replay/idempotency protection

Write actions such as `JOIN_GROUP` should accept idempotency keys. If the main service retries a request due to timeout, the worker should avoid double-submitting when possible.

### 12.7 Auditability

Persist in main-service:

- every worker request
- every worker response status
- every health signal received from worker
- viewer token issuance metadata if operationally needed

## 13. Feasibility

### 13.1 Overall feasibility

The split is feasible without a major product rewrite because:

- frontend already talks only to FastAPI
- persistence is already centralized in the main DB
- browser behavior is mostly concentrated in one file: `browser_agent.py`
- run orchestration is already step-based and sequential

### 13.2 Feasibility assessment by area

#### High feasibility

- split container/runtime into two images
- keep frontend unchanged
- proxy browser setup/status through main-service
- replace direct `BrowserAgent` injection with HTTP client

#### Medium feasibility

- health signal propagation from worker to main-service
- long-lived SSE or event stream handling across services
- durable step retries and idempotency for browser actions

#### Higher-risk areas

- reliable mobile-friendly remote browser viewing in production networking environments
- Facebook session fragility across remote hosting environments
- handling long-running browser operations over network timeouts

## 14. Estimated Effort

Rough implementation estimate for one experienced engineer familiar with this codebase:

### Phase A: analysis and contract extraction

- 1 to 2 days

Tasks:

- define worker API schemas
- extract browser client interface
- decide auth and networking model

### Phase B: create `browser-worker`

- 3 to 5 days

Tasks:

- new FastAPI worker app
- move `BrowserAgent`
- worker Dockerfile and entrypoint
- session/status/setup endpoints
- action endpoints
- noVNC exposure

### Phase C: adapt `main-service`

- 2 to 4 days

Tasks:

- add `BrowserWorkerClient`
- replace direct browser calls in `RunnerService`
- proxy `/api/browser/*`
- sync worker signals/status into DB

### Phase D: testing and hardening

- 2 to 4 days

Tasks:

- integration tests
- timeout/retry handling
- auth hardening
- deployment smoke tests

### Total

- MVP split: about 8 to 15 working days
- production-hardening beyond MVP: add 3 to 7 more days

## 15. Main Risks

### 15.1 Network-induced partial failures

Today a browser call is a Python method call. After the split it becomes a distributed operation.

Risks:

- request timeout while browser action actually succeeded
- duplicate retries on join/write operations
- worker restarts mid-step

Mitigation:

- idempotency keys
- explicit timeout classes
- request logging
- keep step checkpoints in main DB

### 15.2 Session drift

Main-service may think session is valid while worker has already lost it.

Mitigation:

- periodic session sync
- worker-originated health/event stream
- main-service treats worker session status as authoritative

### 15.3 Browser-view exposure risk

noVNC is powerful because it exposes the full browser session.

Mitigation:

- short-lived signed links
- HTTPS
- auth layer
- network scoping
- operator awareness that the viewer is privileged access

### 15.4 Distributed observability gap

Debugging becomes harder across two machines.

Mitigation:

- structured logs with `request_id`, `run_id`, `step_id`
- worker and main-service correlation IDs
- health event audit trail

### 15.5 Facebook anti-automation variability

Moving the browser to another machine may change:

- network fingerprint
- IP reputation
- login challenge rate

Mitigation:

- run worker on a stable host/IP
- keep persistent profile storage
- test remote-hosted session stability early before deeper refactor work

## 16. Recommended Migration Plan

### Step 1. Introduce an abstraction in main-service

Create an interface such as:

- `BrowserRuntime` or `BrowserExecutor`

Implementations:

- `LocalBrowserAgentAdapter`
- `RemoteBrowserWorkerClient`

Update `RunnerService` and browser setup routes to depend on the abstraction, not directly on `BrowserAgent`.

This is the most important refactor because it reduces the current coupling without changing behavior yet.

### Step 2. Move browser runtime into a dedicated worker app

Build a new worker service that initially copies:

- `BrowserAgent`
- session/setup APIs
- Xvfb/VNC/noVNC startup logic

Keep behavior as close as possible to current monolith semantics.

### Step 3. Proxy browser APIs through main-service

Maintain current frontend routes on main-service:

- `/api/browser/status`
- `/api/browser/setup`
- `/api/browser/setup/stream`

Main-service becomes the stable frontend-facing API layer.

### Step 4. Replace run-step local calls with remote calls

Change `RunnerService` so every browser-dependent action goes through the remote client.

### Step 5. Add worker event ingestion

Main-service should ingest worker-originated:

- session changes
- CAPTCHA/action-block/rate-limit signals

and persist them using the current health tables.

### Step 6. Remove browser dependencies from main-service container

After cutover:

- remove Xvfb/VNC/noVNC/Camoufox from main-service image
- keep only backend/frontend/AI/runtime needs

This will materially simplify the main-service deployment.

## 17. Recommended Target Deployment Layout

### `browser-worker` image

Contains:

- Python app
- `BrowserAgent`
- Camoufox
- Xvfb
- x11vnc
- noVNC/websockify

Persistent volume:

- browser profile directory

Ports:

- worker API port, e.g. `8100`
- browser-view port behind reverse proxy, not necessarily directly exposed

### `main-service` image

Contains:

- FastAPI backend
- built React frontend
- AI integrations
- SQLite volume or future DB connection

Does not contain:

- Camoufox
- Xvfb
- x11vnc
- noVNC

## 18. Suggested Internal Refactor Targets

Before or during the split, these code changes will reduce risk:

### 18.1 Extract browser client protocol types

Create shared schemas for:

- session status
- search groups result
- join group result
- search posts result
- crawled post payload
- health signal payload

Today these are implicit dicts.

### 18.2 Separate browser-side health from persisted app health

Keep:

- worker observed state
- main persisted state

as distinct concepts. Then explicitly sync from worker to main.

### 18.3 Move browser setup stream ownership to worker

The current `BrowserSetupHub` should not remain a main-service-local in-memory coordination primitive once the worker exists. Main-service can proxy worker SSE, but the source of truth should move to worker.

### 18.4 Add correlation metadata

For every worker request/response, include:

- `request_id`
- `run_id`
- `step_id`
- `action_type`
- `worker_id`

## 19. Final Recommendation

Proceed with the split.

This codebase is structurally ready for a two-service design because:

- browser logic is concentrated
- UI is already backend-mediated
- persistence and AI logic are already outside browser code

Recommended implementation strategy:

1. first introduce a browser-runtime abstraction inside main-service
2. then stand up a remote browser-worker with near-identical browser behavior
3. then switch main-service from local adapter to remote client
4. then remove browser runtime dependencies from main-service deployment

Avoid over-design at this stage. A simple authenticated HTTP worker with SSE for setup/events is the best fit for the current sequential, single-account execution model.

## 20. Concrete MVP Decisions

If implementation starts immediately, these are the recommended MVP decisions:

- One browser worker, one Facebook account, one persistent profile
- FastAPI on both services
- HTTP JSON action API plus SSE for setup/events
- noVNC retained on worker for mobile/browser access
- Main-service remains the only frontend-facing service
- Main-service remains the only DB owner
- Worker returns masked text only
- Shared bearer auth initially, upgrade to mTLS/JWT later if needed
- Idempotency keys for write operations from day one

