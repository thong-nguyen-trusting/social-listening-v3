# VPS Deployment Analysis: Single-Machine, Mobile-First Operation

## 1. Goal

This document analyzes the current `social-listening-v3` codebase for a simpler deployment target:

- one VPS
- one public domain such as `app.example.com`
- HTTPS only
- no raw port exposure to the user
- mobile-first operation for Facebook login, browser watching, CAPTCHA solving, and crawl monitoring

The focus is the simplest path that works reliably on a phone, not the most scalable architecture.

## 2. Files Reviewed

The analysis is grounded in these current files:

- `entrypoint.sh`
- `docker-compose.yml`
- `Dockerfile`
- `backend/app/main.py`
- `backend/app/infrastructure/lifespan.py`
- `backend/app/infrastructure/config.py`
- `backend/app/api/browser.py`
- `backend/app/api/runs.py`
- `backend/app/api/health.py`
- `backend/app/api/plans.py`
- `backend/app/api/labels.py`
- `backend/app/api/insights.py`
- `backend/app/infra/browser_agent.py`
- `frontend/src/App.tsx`
- `frontend/src/app/shell/AppLayout.tsx`
- `frontend/src/app/shell/AppHeader.tsx`
- `frontend/src/pages/SetupPage.tsx`
- `frontend/src/pages/MonitorPage.tsx`
- `frontend/src/lib/api.ts`
- `docs/architecture-split-analysis.md`

## 3. Current Architecture Summary

### 3.1 Runtime topology today

The current app is already structurally close to a single-VPS deployment:

- one Docker image contains FastAPI, built React assets, Camoufox, Xvfb, x11vnc, and noVNC
- `entrypoint.sh` starts:
  1. `Xvfb`
  2. `x11vnc` on `5900`
  3. `websockify` + noVNC on `6080`
  4. Alembic migrations
  5. `uvicorn` on `8000`
- `docker-compose.yml` exposes:
  - `8000` for API/UI
  - `6080` for noVNC
- the browser profile and SQLite DB are already persisted as Docker volumes

This means the app does not need a service split for the new requirement. It needs packaging, routing, security, and UX changes.

### 3.2 Backend topology today

The backend is a single FastAPI process with in-process collaborators:

- `BrowserAgent`
- `HealthMonitorService`
- `PlannerService`
- `ApprovalService`
- `RunnerService`
- `LabelJobService`
- `InsightService`

That is favorable for a single VPS. There is no need to introduce brokers, remote workers, or an inter-service API for this deployment mode.

### 3.3 Frontend topology today

The React app is a dashboard-style SPA served by FastAPI:

- `SetupPage` handles browser setup and browser setup SSE
- `MonitorPage` handles run streaming and controls
- the UI uses Mantine layout primitives and does collapse to 1 column at small breakpoints

However, the current UX is not actually mobile-first:

- no integrated browser viewport
- no mobile navigation pattern
- dense control layout in `MonitorPage`
- no clear operator flow for "connect browser -> solve issue -> resume crawl"
- no app authentication

## 4. What The New Requirement Really Implies

The user is not asking for generic monitoring. They need a phone-operator workflow:

1. open `https://app.example.com`
2. sign in to the app itself
3. start Facebook setup
4. see the live browser on the same domain
5. interact with the live browser from the phone when Facebook requires it
6. monitor crawl progress and health from the phone
7. jump back into the live browser if CAPTCHA or login friction happens

This makes browser interactivity the central design decision.

## 5. Best Approach For Mobile Browser Interaction

### 5.1 Option A: noVNC, kept as the primary remote browser surface

#### What it is

Keep the current Xvfb + x11vnc + noVNC stack, but do not expose it as a separate raw port. Instead:

- proxy it under the app domain, for example:
  - `https://app.example.com/browser/`
- optionally embed it inside the React UI with an `iframe`
- also provide an "Open full browser" button for a dedicated view

#### Pros

- already present in the codebase
- lowest engineering effort
- interactive, not just visual
- works with touch input better than custom screenshot-stream hacks
- good enough for login, OTP, checkpoint prompts, and CAPTCHA solving
- no need to translate taps into Playwright DOM actions
- no need to build custom streaming infrastructure

#### Cons

- mobile UX is not elegant
- pinch/zoom, text input, and drag interactions are only acceptable, not excellent
- VNC bandwidth is heavier than targeted image streaming
- if embedded in a small panel, the browser becomes difficult to use on phones

#### Practical verdict

This is the best default choice for this product right now.

It is already installed, already booted, already persistent, and already matches the requirement of "watch browser actions in real time and interact when needed." It is not beautiful, but it is the shortest path to something operational.

The important change is not replacing noVNC. The important change is:

- route it through the same domain
- mobile-optimize how it is presented
- make it easy to switch between dashboard mode and fullscreen remote browser mode

### 5.2 Option B: embedded browser view inside React UI

#### What it is

Render the existing noVNC page inside the main app, likely via:

- `iframe` to `/browser/vnc.html?...`
- a dedicated React route such as `#/browser`
- or a responsive split layout on larger screens and fullscreen on phones

#### Pros

- keeps the user on one domain and one app
- lets the dashboard and browser feel like one product
- minimal backend change if it simply frames proxied noVNC
- can add app chrome around it:
  - status badges
  - reconnect button
  - "open fullscreen"
  - "resume crawl"

#### Cons

- if embedded too tightly, mobile usability becomes poor
- cross-frame sizing and focus need care
- some noVNC keyboard interactions are better in a dedicated page than inside a dashboard card

#### Practical verdict

This should be used, but only as the shell around noVNC, not as a custom browser renderer.

Recommended pattern:

- desktop: browser panel can sit next to status panels
- mobile: browser gets its own dedicated route and fills most of the viewport

### 5.3 Option C: browser live streaming via screenshots or video

This category includes:

- periodic Playwright screenshots over SSE/WebSocket
- MJPEG/WebRTC/HLS style streams
- server-side encoded video of the browser

#### Pros

- can look cleaner than VNC
- can reduce UI chrome and tailor the viewport
- screenshot streaming is simple for passive viewing

#### Cons

- passive viewing is not enough; the user must interact
- true interactivity means mapping phone events back into the browser
- latency and coordinate mapping become fragile
- CAPTCHA and login screens are exactly where fragile remote control fails
- WebRTC/video pipelines add moving parts that the current codebase does not need

#### Practical verdict

Not recommended for this phase.

If the product only needed "watch what the bot is doing", screenshot streaming would be reasonable. But the user explicitly needs intervention from the phone. VNC is simpler and more reliable for that requirement.

### 5.4 Option D: Playwright CDP-based screenshot streaming + custom controls

#### What it is

Use Playwright or CDP to:

- grab screenshots on a timer
- overlay click hotspots or a transparent interaction layer
- send taps/keystrokes back to the active page

#### Pros

- potentially tighter integration with app state
- can selectively expose browser operations
- could hide browser chrome

#### Cons

- high implementation complexity
- brittle across layout changes, scrolling, popups, native dialogs, and anti-bot flows
- much worse fit for manual Facebook login and CAPTCHA than raw remote desktop
- duplicates functionality that VNC already provides

#### Practical verdict

Do not do this unless the product later evolves into a guided, constrained operator console and no longer needs general browser control.

### 5.5 Option E: Other creative solutions

#### Appium / mobile emulation / DevTools frontend

Not a fit. The real problem is remote interaction with one persistent desktop browser context on the server. DevTools-style tooling does not replace a remote desktop for arbitrary login friction.

#### Guacamole instead of noVNC

Apache Guacamole can provide a more polished remote desktop gateway than raw noVNC, but it is another system to operate and is not already in the stack. It is only worth considering if:

- noVNC proves too unstable on phones
- multi-user session brokering becomes important
- clipboard, auth, and gateway features become requirements

For the current requirement, it is unnecessary complexity.

## 6. Recommended Solution

### 6.1 Decision

Use this architecture:

- keep the app as one containerized monolith on one VPS
- keep Xvfb + x11vnc + noVNC inside the app container
- add a reverse proxy container in front
- terminate HTTPS at the reverse proxy
- expose everything via one domain
- proxy noVNC under a path, not a public raw port
- integrate the proxied noVNC surface into the React app
- add app-level authentication in front of both the SPA and browser path

### 6.2 Why this is the best fit

It is the simplest architecture that satisfies all requirements:

- single VPS: yes
- single domain: yes
- mobile browser login: yes
- live browser viewing: yes
- touch interaction when needed: yes
- monitoring from phone: yes
- minimal code churn: yes

## 7. Proposed Single-VPS Deployment Architecture

### 7.1 Components

#### Reverse proxy

Use either:

- `Caddy` for the simplest HTTPS and reverse proxy setup
- or `nginx` + `certbot` if the team strongly prefers nginx

For this repo, `Caddy` is the better default because it minimizes operational scripting.

#### App container

One container based on the existing Dockerfile:

- FastAPI on internal `8000`
- noVNC/websockify on internal `6080`
- Xvfb + x11vnc + Camoufox inside the same container

#### Persistent volumes

- browser profile volume
- SQLite volume
- optionally Caddy certificate storage volume

### 7.2 Network and routing

Recommended public routing:

- `https://app.example.com/` -> FastAPI + React
- `https://app.example.com/api/...` -> FastAPI
- `https://app.example.com/browser/...` -> noVNC/websockify

No public `:8000` or `:6080` access.

Only the reverse proxy publishes `80` and `443`.

### 7.3 HTTPS

Use Let's Encrypt certificates at the reverse proxy layer.

For Caddy this is nearly automatic. Requirements:

- DNS `A` record for `app.example.com` to the VPS IP
- ports `80` and `443` open

### 7.4 Docker compose topology

Recommended services:

1. `app`
   - current application container
   - no published ports to the internet
   - exposed internally to Docker network on `8000` and `6080`
2. `proxy`
   - Caddy or nginx
   - published ports `80:80` and `443:443`
   - routes `/` to `app:8000`
   - routes `/browser/` to `app:6080`

### 7.5 Suggested request flow

#### Main app flow

`phone browser -> HTTPS reverse proxy -> FastAPI/React`

#### Browser interaction flow

`phone browser -> HTTPS reverse proxy -> /browser/ -> noVNC/websockify -> x11vnc -> Xvfb -> Camoufox`

This preserves a single-origin user experience while reusing the current browser runtime.

## 8. Reverse Proxy Recommendation: Caddy vs nginx

### 8.1 Caddy

#### Pros

- automatic HTTPS
- very small configuration
- easier WebSocket proxying than nginx for many teams
- fewer deployment steps

#### Cons

- less familiar than nginx in some teams
- finer-grained auth patterns sometimes push teams back toward nginx

#### Verdict

Best choice for this deployment.

### 8.2 nginx

#### Pros

- familiar
- flexible
- easy to layer with `auth_basic` or an external auth service

#### Cons

- more ceremony for HTTPS renewal and setup
- slightly more operational friction for a single-VPS app

#### Verdict

Still valid, but not the simplest path.

## 9. Mobile UX Design Recommendation

### 9.1 Core principle

Do not try to make the phone user operate a dense desktop dashboard.

Instead, define two clear mobile modes:

1. `Operations` mode
   - session status
   - health status
   - run state
   - step progress
   - pause/resume/stop
2. `Browser` mode
   - large remote browser viewport
   - minimal surrounding chrome
   - reconnect / open fullscreen / back to monitor actions

### 9.2 Recommended UI structure

#### Mobile routes

- `#/setup`
- `#/monitor`
- `#/browser`

#### Browser route behavior

On phones, `#/browser` should:

- dedicate most of the viewport height to the remote browser
- show a sticky top bar with:
  - session status
  - health status
  - reconnect
  - back to monitor
- offer a "fullscreen browser" button

#### Monitor route behavior

On phones, `#/monitor` should prioritize:

- current run status
- current step
- recent events
- health warnings
- quick button to jump to browser view

### 9.3 Recommended interaction model

The user should not need to manually open a second URL for browser access. The app should:

- start setup from `SetupPage`
- automatically surface a prominent "Open Browser View" action
- auto-navigate or suggest navigation to `#/browser` during setup or when health becomes `CAUTION` / `BLOCKED`

## 10. Is The Current Frontend Responsive Enough?

### 10.1 What is already acceptable

The current app has a baseline level of responsiveness:

- `SimpleGrid cols={{ base: 1, sm: 2 }}` already collapses panels to one column on small screens
- Mantine components generally behave acceptably on mobile
- the app shell is not hard-coded to desktop dimensions

### 10.2 What is not good enough

The current app is not genuinely mobile-first:

- the header is a desktop action row, not a compact mobile nav
- the entire dashboard loads as stacked cards, which becomes long and operationally noisy
- `MonitorPage` has too many inline controls in one `ActionBar`
- there is no browser viewport in the app at all
- no remote-browser-specific layout exists
- status updates are text-heavy and not optimized for quick scanning on small screens

### 10.3 Conclusion

The frontend is responsive in the narrow technical sense, but not mobile-ready for this use case.

It needs product-level layout changes, not just CSS tweaks.

## 11. Required Backend Changes

### 11.1 Add authenticated app access

There is currently no app authentication layer in FastAPI. Anyone who reaches the app can access:

- the dashboard
- run controls
- browser setup endpoints
- browser stream endpoints
- health reset endpoints

That is unacceptable once the app is public on a real domain.

#### Recommended simplest auth model

Add a single-user app login for the operator:

- session-cookie based auth
- username + password from environment variables
- password hashed with bcrypt/argon2 at startup or stored as a hash in env
- secure, httpOnly cookie
- same auth required for:
  - `/`
  - `/api/...`
  - `/browser/...` through proxy enforcement

#### Alternative quick shield

Reverse-proxy basic auth is simpler to add, but weaker as a product UX:

- good as a first emergency gate
- not ideal long term because the browser surface and SPA become tied to browser-native auth prompts

#### Recommended approach

Use app-level session auth plus optional reverse-proxy IP rate limiting.

### 11.2 Add browser URL support to backend/runtime metadata

The frontend currently knows nothing about the browser view except setup status.

Add runtime metadata or a dedicated endpoint returning:

- browser view path, for example `/browser/vnc.html?autoconnect=true&resize=remote`
- whether browser view is enabled
- whether browser session is currently interactive

### 11.3 Improve real-time status APIs

Current SSE coverage:

- setup flow SSE: yes
- run stream SSE: yes

Missing:

- browser attention events surfaced cleanly to UI
- explicit "operator action required" events
- consolidated health + run + browser status snapshot for the mobile dashboard

#### Recommended additions

Add an operator-focused status endpoint and/or SSE stream:

- `/api/operator/status`
- `/api/operator/stream`

Suggested payload:

- browser session status
- health status
- active run id
- active run status
- current step
- whether manual intervention is required
- reason: CAPTCHA / action blocked / session expired / login requested

This prevents the phone UI from stitching several APIs together with polling.

### 11.4 Optionally add browser focus endpoints

Not required for v1, but useful:

- `POST /api/browser/open-facebook-login`
- `POST /api/browser/focus`

This is optional because noVNC already exposes the raw browser. It only matters if the UI wants guided flows.

## 12. Required Frontend Changes

### 12.1 Add a dedicated Browser page

Add a new page, likely `BrowserPage.tsx`, that:

- embeds the proxied noVNC client
- supports fullscreen mode
- shows compact status badges
- provides reconnect/open-in-new-tab controls

Implementation options:

1. `iframe` to proxied noVNC
2. direct use of noVNC client JS inside React

Recommendation:

Start with `iframe`.

Why:

- far less code
- no need to own the noVNC client lifecycle yet
- easiest path to working mobile access

### 12.2 Improve app navigation for mobile

Current `AppHeader` is a desktop-style action row. On phone it should become:

- compact title
- menu button or tab bar
- primary actions only

Recommendation:

- keep desktop header for larger screens
- add a mobile nav bar or segmented control for `Setup`, `Monitor`, `Browser`

### 12.3 Redesign Setup flow

Current `SetupPage` is status + one button. It should become:

1. connect button
2. immediate CTA to open browser
3. clear instruction text:
   - "Log in to Facebook in the browser view"
   - "Return to monitor once session is valid"
4. health/session badges pinned near the top

### 12.4 Redesign Monitor page for operators

Current `MonitorPage` is functional but dense.

Recommended changes:

- break controls into stacked groups on mobile
- show active run summary first
- show current step card first
- show recent event timeline in plain language
- show a sticky `Open Browser` button when intervention may be needed
- auto-highlight health warnings

### 12.5 Add auth UI

The app will need:

- login page
- logout action
- auth guard for app routes

## 13. Browser View Integration Details

### 13.1 Routing pattern

Recommended proxied path:

- `/browser/` -> noVNC assets and websocket

Example embedded URL:

- `/browser/vnc.html?autoconnect=true&resize=remote&view_only=false`

Recommended React behavior:

- desktop: allow embedded panel with fixed aspect ratio
- mobile: open a dedicated route with near-full-height viewport

### 13.2 Fullscreen strategy

Phone usability improves if the browser page supports:

- browser fullscreen via Fullscreen API when available
- hiding nonessential app chrome

Even without true fullscreen, a minimal top bar and large viewport will be a major improvement.

### 13.3 Screen size strategy on the server

Current defaults:

- `1600x900`

For phone-based intervention, that is usable but small. Recommended:

- default server browser viewport around `1280x800` or `1365x768`

Reason:

- still desktop-like for Facebook layouts
- slightly easier to render legibly inside a phone viewport
- lower bandwidth than `1600x900`

Do not switch the server browser to a narrow mobile viewport. Facebook login and crawl logic likely assume desktop-ish layouts, and the browser agent currently automates desktop pages.

## 14. Security Design

### 14.1 Minimum required controls

For internet exposure, implement all of these:

- HTTPS only
- app authentication
- secure session cookies
- strong operator password
- hidden internal service ports
- no public `6080`
- no public `8000`
- rate limiting on login endpoint at proxy or app layer
- security headers at proxy layer

### 14.2 Strongly recommended controls

- fail2ban or equivalent SSH protection on the VPS
- firewall allowing only `22`, `80`, `443`
- automatic security updates
- Docker restart policies
- daily DB backup and browser profile backup
- `.env` permissions locked down on the VPS

### 14.3 Browser path protection

The browser route must be protected the same as the app.

Do not expose `/browser/` as an unauthenticated subpath. Otherwise anyone who discovers the URL gets live control over the Facebook session.

### 14.4 Multi-user concerns

The current app is effectively single-operator anyway:

- one persistent browser profile
- one browser display
- one shared run execution context

That is acceptable for this deployment scenario. Do not over-engineer multi-user support.

## 15. Concrete Docker Compose Design

### 15.1 Recommended production shape

Use a new production compose file or adapt the current one to:

- remove public mapping for app container ports
- add proxy container
- keep named volumes

Target shape:

- `proxy`
  - publishes `80` and `443`
  - mounts Caddyfile or nginx config
  - routes to `app:8000` and `app:6080`
- `app`
  - no public port publishing
  - `expose: 8000`
  - `expose: 6080`

### 15.2 Why this matters

Current `docker-compose.yml` publishes both app and browser ports directly. That violates the requirement of domain-only access and leaves the browser surface easier to misuse.

## 16. Caddy Example Topology

Illustrative routing only:

- `handle_path /browser/*` -> reverse proxy to `app:6080`
- `handle /*` -> reverse proxy to `app:8000`

Important details:

- preserve WebSocket upgrade support for noVNC/websockify
- set trusted reverse-proxy headers
- optionally add compression for app responses

## 17. Real-Time Monitoring Improvements

### 17.1 What exists now

Current monitoring is split across:

- `/api/browser/status`
- `/api/browser/setup/stream`
- `/api/health/status`
- `/api/runs/{run_id}`
- `/api/runs/{run_id}/stream`
- label polling endpoints

That is workable for desktop but fragmented for a mobile operator.

### 17.2 Recommended mobile monitoring model

Create one operator-oriented dashboard state:

- top status bar:
  - session
  - health
  - active run
  - intervention needed
- current action card:
  - current step
  - records collected
  - last event
- live event feed:
  - simplified language, not raw event dumps
- quick actions:
  - open browser
  - pause
  - resume
  - stop

### 17.3 Alerting behavior

When health signals indicate friction:

- `CAPTCHA`
- `ACTION_BLOCKED`
- `SESSION_EXPIRED`

The UI should surface:

- a red/yellow operator banner
- a direct button to open browser view

## 18. Recommended Implementation Plan

### Phase 1: Productionize single-domain deployment

#### Scope

- add reverse proxy container
- route app and noVNC through one domain
- enable HTTPS
- stop exposing raw public app/browser ports

#### Deliverables

- production `docker-compose` update
- proxy config
- deployment README

#### Effort

- 0.5 to 1 day

### Phase 2: Add authentication and harden public access

#### Scope

- add operator login
- protect SPA and APIs
- protect `/browser/`
- secure cookies and logout

#### Deliverables

- auth backend endpoints/middleware
- login page
- protected routes

#### Effort

- 1 to 1.5 days

### Phase 3: Integrate mobile browser view

#### Scope

- add `BrowserPage`
- embed proxied noVNC
- add fullscreen / open-in-new-tab actions
- add jump links from setup and monitor flows

#### Deliverables

- browser route in React
- mobile layout for browser surface
- setup flow CTA improvements

#### Effort

- 1 to 1.5 days

### Phase 4: Make monitoring genuinely mobile-first

#### Scope

- simplify `MonitorPage`
- add operator status aggregation
- improve intervention banners and quick actions

#### Deliverables

- updated monitor UX
- optional `/api/operator/status` endpoint
- optional operator SSE stream

#### Effort

- 1.5 to 2 days

### Phase 5: Validation and ops polish

#### Scope

- test real phone workflows
- tune browser resolution and noVNC settings
- backup/restore instructions
- VPS hardening checklist

#### Deliverables

- tested deployment guide
- phone QA notes
- rollback notes

#### Effort

- 0.5 to 1 day

### Total estimated effort

- fastest functional path: 3 to 4 days
- safer, better-polished path: 5 to 7 days

## 19. Specific Code Changes By Area

### 19.1 `docker-compose.yml`

Change from direct port publishing to internal service exposure behind a proxy.

Add:

- proxy service
- internal network routing
- certificate storage volume if using Caddy

### 19.2 `entrypoint.sh`

Likely only light changes:

- keep current Xvfb/VNC/noVNC startup
- update readiness logging to reflect internal-only ports
- optionally tune noVNC startup flags and default resolution

No major redesign is needed here.

### 19.3 Backend API

Add:

- auth endpoints or middleware
- runtime/browser config endpoint for frontend
- optional operator aggregate status endpoint/stream

### 19.4 Frontend

Add:

- login page
- browser page
- mobile navigation

Update:

- `SetupPage`
- `MonitorPage`
- `AppHeader`
- route handling in `App.tsx`

## 20. Recommended Final Architecture

### 20.1 Production deployment

- one VPS
- one Docker network
- one reverse proxy container
- one app container
- one public domain
- HTTPS only

### 20.2 Product UX

- authenticated operator app
- dashboard and browser accessible under one domain
- browser interaction via proxied noVNC
- dedicated mobile browser route for manual intervention
- monitoring optimized for quick phone checks

## 21. Final Recommendation

The best practical solution is not to invent a new browser streaming system.

The best solution is:

1. keep the current single-container browser architecture
2. put Caddy in front of it
3. proxy noVNC under `/browser/`
4. add app authentication
5. add a dedicated mobile `Browser` view in React
6. simplify the monitor flow for phone use

This gives the user the simplest deployment that actually works:

- one VPS
- one domain
- one persistent Facebook browser
- live remote interaction from a phone
- crawl monitoring from the same app

If later testing shows noVNC is not acceptable on mobile, the next upgrade path should be Guacamole, not a custom screenshot-stream-and-control system. But that should only happen after validating the simpler noVNC-through-the-app approach in production-like phone testing.
