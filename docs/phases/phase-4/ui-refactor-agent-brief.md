# UI Refactor Agent Brief — Phase 4
## AI Facebook Social Listening & Engagement v3

**Updated:** 2026-03-29
**Target code path:** `frontend/src/`
**Authority:** All decisions locked in [architecture.md](./architecture.md). If this brief conflicts with architecture, architecture wins.

---

## 0. Execution Context

Frontend nay la 1 nested package.

```text
repo root/
  frontend/
    package.json
    src/
```

Rules:
- Tat ca package commands chay trong `frontend/`, khong chay o repo root
- Moi duong dan `src/...` trong brief nay deu co nghia la `frontend/src/...`
- `npm install` va `npm run build` phai duoc hieu la `cd frontend && ...`

---

## 1. Nhiem vu cua ban

Refactor frontend hien tai theo huong `Shared Product Shell` cua Blackbird.

Ban khong duoc tiep can task nay nhu mot lan `restyle`.

Ban phai coi day la `UI foundation refactor` gom:

1. theme/tokens foundation
2. shared shell
3. shared UI primitives
4. page migration
5. CSS cleanup

Doc ky architecture truoc khi code:

- [Architecture](./architecture.md) — source of truth cho moi quyet dinh

---

## 2. Context quan trong

App nay se duoc gan vao `Shared Business Platform` cua Blackbird sau Phase 1.

Dieu do co nghia:

- UI cua app nay phai san sang song cung he sinh thai app khac
- can dung mot shell va visual language mang tinh product platform
- khong the giu cach style "one-off local app" nhu hien tai

App nay van so huu runtime nghiep vu rieng.

Nhung ve mat UI foundation, no phai di theo huong co the dung chung shell va pattern voi cac app khac.

---

## 3. Standard da chot

Ban phai dung:

- `@mantine/core` ^7.x
- `@mantine/hooks` ^7.x
- `@mantine/notifications` ^7.x
- `@fontsource-variable/inter` (font loading via npm)

Monospace: system fallback only (`ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`). Khong install font rieng.

Khong dua them:

- MUI, Chakra, Ant Design, Tailwind, shadcn/ui
- PostCSS config / CSS modules
- Bat ky thay doi nao cho index.html

---

## 4. Ket qua dau ra mong doi

Sau khi xong, frontend phai co:

- `MantineProvider` wrap app voi light/dark support
- `theme/index.ts` voi `createTheme()` ro rang
- `theme/status.ts` — single source of truth cho status-to-color mapping (uppercase keys, normalize via `toUpperCase()`, fallback `'neutral'`)
- `AppLayout` (AppShell + AppHeader) — compact header thay cho hero
- 5+ shared UI primitives trong `components/ui/`
- 6 pages + HealthBadge da migrate sang shell + primitives
- `styles.css` duoi 10 dong global resets
- Hero section da xoa
- Checkpoint cards da xoa
- `cd frontend && npm run build` thanh cong
- Dark mode toggle hoat dong

---

## 5. File structure can tao

Trong `frontend/src/`, tao theo dung structure nay:

```text
frontend/src/
  app/
    providers/
      ThemeProvider.tsx      — MantineProvider + Notifications host
    shell/
      AppLayout.tsx          — AppShell + Container + responsive layout
      AppHeader.tsx          — header bar: app name, API links, theme toggle
  components/
    ui/
      PageSection.tsx        — Paper-based section wrapper (thay .workflow-card, .setup-card, .health-panel, .card)
      PageHeader.tsx         — eyebrow + title primitive (thay pattern eyebrow + h2)
      StatusBadge.tsx        — unified status badge (thay .badge-*, .sentiment-*, .monitor-step-*)
      ActionBar.tsx          — button group wrapper (thay .button-row)
      KeyValueRow.tsx        — label: value display (thay .workflow-meta key:value pattern)
  theme/
    index.ts                 — createTheme() + Mantine theme object
    tokens.ts                — spacing, radius, shadow, color constants
    status.ts                — STATUS_MAP + getStatusLevel + getStatusColor
```

**Khong co trong scope:**
- `AppPage.tsx` — khong can, content truc tiep trong AppLayout + SimpleGrid
- `DataPanel.tsx` — thay bang `KeyValueRow`
- `EmptyState.tsx` — chi tao neu thuc su can trong luc migrate. Khong tao truoc.

---

## 6. Scope code cu the

### 6.1. Foundation (Step 1)

Ban phai:

- install `@mantine/core`, `@mantine/hooks`, `@mantine/notifications`, `@fontsource-variable/inter` trong `frontend/`
- tao `theme/tokens.ts`, `theme/status.ts`, `theme/index.ts`
- tao `app/providers/ThemeProvider.tsx` — wrap MantineProvider + Notifications host
- update `main.tsx`:
  - import `@mantine/core/styles.css`
  - import `@mantine/notifications/styles.css`
  - import `@fontsource-variable/inter`
  - wrap `<App />` trong `<ThemeProvider>`

Notifications strategy: **host only**. Khong migrate inline errors sang toast. Inline `<Alert>` van la dung pattern cho form-level feedback. Toast chi dung cho async background events trong tuong lai — nhung Phase 4 chua can.

### 6.2. Shell (Step 2)

Ban phai tao:

- `AppHeader.tsx` — slim 60px header:
  - Left: app name "Social Listening v3"
  - Center/right: API quick links (compact ButtonGroup, secondary variant)
  - Right: dark mode toggle (ActionIcon)
- `AppLayout.tsx` — AppShell wrapper + Container (size="lg", ~1100px)

Va tao 5 shared UI primitives:

- `PageSection.tsx` — Paper shadow="xs" radius="lg" withBorder
- `PageHeader.tsx` — Stack: eyebrow Text (xs, uppercase, dimmed) + Title (order=3, size=h4)
- `StatusBadge.tsx` — Badge voi status normalization an toan (`trim() + toUpperCase()` → STATUS_MAP → color). Fallback: 'neutral' (gray) cho unknown/empty/missing status
- `ActionBar.tsx` — Group gap="sm" mt="sm"
- `KeyValueRow.tsx` — Group: label Text (dimmed) + value Text (optional monospace)

Xem architecture.md Section 6.2 cho full component specs.

Status mapping phai cover toi thieu:
- Health: `HEALTHY`, `CAUTION`, `BLOCKED`
- Session: `VALID`, `NOT_SETUP`, `EXPIRED`
- Run/step/label job: `RUNNING`, `DONE`, `FAILED`, `PENDING`, `COMPLETED`, `PAUSED`, `CANCELLED`
- Stream state trong UI: `IDLE`, `CONNECTING`, `CONNECTED`, `COMPLETE`, `DISCONNECTED`
- Sentiment: `POSITIVE`, `NEGATIVE`, `NEUTRAL`
- Plan action type: `READ`, `WRITE`

Neu trong luc migrate xuat hien status string moi, phai update `theme/status.ts` truoc. Khong duoc tao mapping rieng trong page.

### 6.3. Page migration (Step 3)

Ban phai migrate theo thu tu:

1. `App.tsx` — xoa hero + checkpoints, thay grids bang AppLayout + SimpleGrid (equal columns)
2. `HealthBadge.tsx` — don gian nhat, validate StatusBadge
3. `SetupPage.tsx` — validate PageSection + PageHeader
4. `KeywordPage.tsx` — medium, validate form components
5. `PlanPage.tsx` — validate step rendering
6. `ApprovePage.tsx` — validate Checkbox + ActionBar
7. `MonitorPage.tsx` — complex nhat, validate moi primitive
8. `ThemesPage.tsx` — validate SegmentedControl + StatusBadge

Nguyen tac migration moi page:
1. Giu nguyen toan bo state/effect/handler logic — khong cham
2. Chi thay return JSX:

| Cu (CSS class) | Moi (Mantine) |
|----------------|---------------|
| `<section className="workflow-card">` | `<PageSection>` |
| `<p className="eyebrow">` + `<h2>` | `<PageHeader eyebrow="..." title="...">` |
| `<input className="text-input">` | `<TextInput>` |
| `<textarea className="text-input ...">` | `<Textarea>` |
| `<div className="button-row">` | `<ActionBar>` |
| `<button className="connect-button">` | `<Button>` |
| `<button className="ghost-button">` | `<Button variant="light">` |
| `<p className="error-copy">` | `<Alert color="red" variant="light">` |
| `<p className="warning-copy">` | `<Alert color="yellow" variant="light">` |
| `<p className="workflow-meta">key: val` | `<KeyValueRow label="key" value="val">` |
| `<span className="badge-*">` | `<StatusBadge status="...">` |
| `<span className="sentiment-*">` | `<StatusBadge status="...">` |
| `<button className="filter-chip">` | `<SegmentedControl>` (ThemesPage) |
| `<span className="label-chip">` | `<Badge variant="light">` |

3. Xoa tat ca className references sang styles.css

Xem architecture.md Section 9 cho migration details tung page.

Bat buoc them cho page migration:
- `SetupPage.tsx`: render `session_status` va `health_status` bang `StatusBadge`, khong de plain text status
- `MonitorPage.tsx`: render `streamStatus`, `run.status`, `step.status`, `labelSummary.status` bang `StatusBadge` wherever they are shown as statuses
- `ThemesPage.tsx`: render `dominant_sentiment` bang `StatusBadge`

### 6.4. CSS cleanup (Step 4)

Sau khi migrate het, thu gon `styles.css` xuong chi con:

```css
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}
```

Target: duoi 10 dong. Xoa tat ca component classes khac.

---

## 7. Dev rules bat buoc

1. Khong duoc doi API contracts hoac request flow chi vi refactor UI.
2. Khong duoc tron them mot design system/framework thu 2.
3. Khong duoc viet them CSS classes moi. Moi UI element dung Mantine components hoac theme tokens.
4. Moi primitive moi phai duoc dat o muc generic du cho it nhat 2 page dung lai.
5. Dung `StatusBadge` cho TAT CA status display — khong dinh nghia color rieng trong page.
6. Dung `PageSection` cho TAT CA card/panel containers — khong one-off card styles.
7. Dung `PageHeader` cho TAT CA page header patterns — khong inline eyebrow/h2.
8. Khong duoc bo qua accessibility co ban — Mantine cung cap focus states va disabled states by default, khong override chung.
9. Status strings luon normalize via `toUpperCase()` truoc khi mapping — khong duplicate lowercase/uppercase keys.
10. Khong duoc lam vung runtime nghiep vu: state, effects, fetch, EventSource logic giu nguyen.
11. Neu command/build/install duoc nhac den ma khong co prefix, mac dinh chay trong `frontend/`.

---

## 8. Visual rules bat buoc

1. Giao dien phai nhin nhu `product app`, khong phai landing page. Hero da xoa.
2. Surface hierarchy ro rang: app bg (gray.0/dark.8), panel bg (white/dark.6), muted section (gray.1/dark.7).
3. Typography: Inter (sans-serif) cho tat ca text. System monospace cho IDs/hashes.
4. Status states nhat quan qua StatusBadge + status.ts mapping — khong tu dinh nghia mau.
5. Panels/cards dung PageSection thong nhat — khong moi page mot style.
6. Hanh dong chinh (Button) / phu (Button variant="light") ro rang.

---

## 9. Yeu cau token/theme

Tao token direction trong `theme/index.ts` + `theme/tokens.ts` cho:

- brand colors (10-shade array, `#2C3E50` anchor)
- surface (app, panel, muted — light + dark)
- text (primary, secondary — light + dark)
- border (default — light + dark)
- status (success/warning/danger/info/neutral -> green/yellow/red/blue/gray)
- spacing (`xs:4, sm:8, md:16, lg:24, xl:32`)
- radius (`xs:4, sm:8, md:12, lg:16, xl:24`)
- shadow (`xs:subtle, sm:panel, md:card-elevated, lg:overlay`)

Theme support: light + dark. Default: `auto` (system).

Xem architecture.md Section 4 cho full token specs.

---

## 10. Component mapping da chot

| UI element | Component |
|-----------|-----------|
| shell root | `AppLayout` (AppShell + Container) |
| top header | `AppHeader` (compact, 60px) |
| page intro | `PageHeader` (eyebrow + title) |
| page body block | `PageSection` (Paper-based) |
| state pills / status | `StatusBadge` (normalize + STATUS_MAP) |
| grouped buttons | `ActionBar` (Group) |
| key metadata | `KeyValueRow` (label + value) |
| filters (ThemesPage) | `SegmentedControl` (Mantine) |
| error messages | `Alert color="red" variant="light"` (inline, khong toast) |
| warning messages | `Alert color="yellow" variant="light"` (inline) |

---

## 11. Acceptance criteria de tu check truoc khi giao

Ban chi nen xem task la xong khi:

- [ ] `cd frontend && npm run build` thanh cong, khong type errors
- [ ] App co `MantineProvider` voi light/dark support
- [ ] `theme/index.ts` co `createTheme()` voi brand colors, spacing, radius, typography, component overrides
- [ ] `theme/status.ts` co STATUS_MAP uppercase keys + `getStatusLevel()` + `getStatusColor()`
- [ ] App co `AppLayout` (AppShell + AppHeader), khong con hero
- [ ] Checkpoint cards da xoa
- [ ] Co 5 shared UI primitives: PageSection, PageHeader, StatusBadge, ActionBar, KeyValueRow
- [ ] 6 pages + HealthBadge da dung shell + primitives moi
- [ ] `styles.css` duoi 10 dong global resets
- [ ] Khong API contract hay request flow nao bi thay doi
- [ ] Dark mode toggle hoat dong
- [ ] Inter font load dung qua `@fontsource-variable/inter`

---

## 12. Bao cao can nop sau khi xong

Khi xong, ban phai bao cao:

1. file nao da them/sua
2. theme structure da tao
3. shared primitives da tao
4. page nao da migrate
5. cho nao con de lai cho phase UI tiep theo
6. trade-off nao da chap nhan tam thoi

---

## 13. Non-goals

Khong can:

- pixel-perfect polish
- them charts framework
- them router refactor
- them animation system
- build full multi-app Blackbird shell
- multi-brand theme support (chi de duong)
- PostCSS / CSS modules
- sua index.html / FOUC prevention
- migrate errors sang toast (host only)

---

## 14. Thu tu code

1. install packages (`@mantine/core`, `@mantine/hooks`, `@mantine/notifications`, `@fontsource-variable/inter`)
2. tao theme (tokens.ts, status.ts, index.ts)
3. tao provider (ThemeProvider.tsx), update main.tsx
4. tao shell (AppHeader.tsx, AppLayout.tsx)
5. tao shared primitives (PageSection, PageHeader, StatusBadge, ActionBar, KeyValueRow)
6. migrate pages (App.tsx -> HealthBadge -> Setup -> Keyword -> Plan -> Approve -> Monitor -> Themes)
7. cleanup CSS (styles.css xuong <10 dong)
8. run `cd frontend && npm run build` va tu review consistency
