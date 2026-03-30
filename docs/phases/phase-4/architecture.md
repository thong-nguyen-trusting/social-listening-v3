# Architecture — Phase 4: Theme, Tokens, and Shared Shell
## AI Facebook Social Listening & Engagement v3

**Updated:** 2026-03-29
**Status:** Implementation-ready — all decisions locked

---

## 0. Execution Context

Frontend code for this phase lives in the nested Vite package:

```text
repo root/
  frontend/
    package.json
    src/
```

Rules for all implementation in this document:
- Run package commands from `frontend/`, not repo root
- File paths under `src/` mean `frontend/src/` unless explicitly stated otherwise
- `npm install` and `npm run build` mean `cd frontend && ...`

---

## 1. Current State Analysis

### 1.1. What exists

```text
frontend/src/
  App.tsx                  — root component, hero landing + grid layout
  main.tsx                 — React entry, renders App into #root
  styles.css               — 391 lines, sole presentation source of truth
  vite-env.d.ts
  components/
    HealthBadge.tsx         — health status polling, badge display
  lib/
    api.ts                  — fetchJson, apiUrl, withQuery utilities
  pages/
    SetupPage.tsx           — browser session setup + EventSource stream
    KeywordPage.tsx         — topic analysis, clarification Q&A loop
    PlanPage.tsx            — plan generation + natural language refinement
    ApprovePage.tsx         — step approval checklist + run trigger
    MonitorPage.tsx         — realtime SSE monitor + labeling pipeline
    ThemesPage.tsx          — theme extraction with audience filtering
```

Dependencies: react 18.3, react-dom 18.3, vite 6.2, typescript 5.7. No UI library.

### 1.2. Problems identified from code review

| Problem | Evidence |
|---------|----------|
| No theme provider | `styles.css` :root uses hardcoded values, no CSS variables, no dark mode |
| No token system | Colors, spacing, radius scattered as raw values across 391 lines |
| Landing-page hero pattern | `App.tsx:39-61` — large hero block with editorial typography occupying prime viewport |
| No app shell | `App.tsx` uses `<main className="shell">` with manual grids, no header/nav/layout system |
| One-off card styles per context | `.setup-card`, `.health-panel`, `.workflow-card`, `.card` — 4 nearly identical panel definitions |
| Status colors defined ad-hoc | `.badge-healthy`, `.badge-caution`, `.badge-blocked`, `.monitor-step-running/done/failed`, `.sentiment-*` — 3 separate status color systems |
| Every page repeats the same pattern | eyebrow + h2 + input + button-row + error/status/meta — no shared page/section primitive |
| Editorial typography | Serif font (Iowan Old Style) as primary — not suitable for product/dashboard UI |
| No accessibility tokens | No focus ring definitions, no disabled state tokens, no contrast system |
| CSS is sole source of truth | All layout, color, spacing decisions live in one flat CSS file |

### 1.3. What works and must be preserved

- **State flow chain**: App.tsx manages `activeContextId -> activePlanId -> activeRunId` callback chain. Stays untouched.
- **API layer**: `lib/api.ts` (fetchJson, apiUrl, withQuery). Stays as-is.
- **Business logic per page**: All useState/useEffect/fetch/EventSource logic inside pages. Stays as-is.
- **Type definitions**: All page-local types (BrowserStatus, SessionResponse, PlanStep, etc.). Stay as-is.

---

## 2. Architecture Principle

Phase 4 is a **foundation refactor** in 3 layers:

```text
Layer 1: Theme + Tokens           (foundation)
Layer 2: Shared Shell + Primitives (structure)
Layer 3: Page Migration + CSS Cleanup (application)
```

Rules:
- Business logic (state, API calls, event handlers) stays in page components untouched
- Change only the return JSX and CSS class references
- Shell-first, page-second
- Every repeated UI pattern becomes a shared primitive

---

## 3. Design System Standard

### Mantine as sole UI library

Install:
- `@mantine/core` ^7.x
- `@mantine/hooks` ^7.x
- `@mantine/notifications` ^7.x

Mantine 7 provides:
- `MantineProvider` with CSS variables + color scheme switching
- `AppShell` component for header/navbar/main layout
- `createTheme()` for token customization
- Component library: Paper, Card, Stack, Group, Badge, Alert, Modal, Tabs, TextInput, Textarea, Select, Checkbox, Button, ActionIcon, Notification

### No PostCSS config

Phase 4 does not use CSS modules. All presentation uses Mantine component props and inline style props. No `postcss.config.mjs` needed. If future phases need CSS modules, add PostCSS config at that time.

### No changes to index.html

Mantine's `ColorSchemeScript` for FOUC prevention is skipped. This is an internal product tool, not consumer-facing. A minor 1-frame flash on dark mode is acceptable. No `index.html` modification needed.

---

## 4. Theme and Token Architecture

### 4.1. Font loading

Install via npm:
```
npm install @fontsource-variable/inter
```

Import in `main.tsx`:
```ts
import '@fontsource-variable/inter';
```

Monospace: system fallback only. No extra font package.
```
ui-monospace, SFMono-Regular, Menlo, Consolas, monospace
```

Rationale: Inter is not a system font — npm package ensures it loads reliably without CDN dependency. Monospace is only used for IDs/hashes (minor usage), not worth a separate font install.

### 4.2. Token hierarchy

3 layers:

**Primitive tokens** — raw design values:

| Token | Values |
|-------|--------|
| `colors.brand` | 10-shade array, primary = blue-gray family `#2C3E50` anchor |
| `colors.status` | success green, warning amber, danger red, info blue (each 10 shades) |
| `spacing` | `{ xs: 4, sm: 8, md: 16, lg: 24, xl: 32 }` (rem-based via Mantine) |
| `radius` | `{ xs: 4, sm: 8, md: 12, lg: 16, xl: 24 }` |
| `shadows` | `{ xs: subtle, sm: panel, md: card-elevated, lg: overlay }` |
| `fontFamily` | `Inter Variable, Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif` |
| `fontFamilyMonospace` | `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` |
| `headings.fontFamily` | Same as body (no separate display font for product UI) |

**Semantic tokens** — via Mantine CSS variables + `createTheme()`:

| Semantic | Light mode | Dark mode |
|----------|-----------|-----------|
| `surface.app` | `gray.0` (#f8f9fa) | `dark.8` (#1a1b1e) |
| `surface.panel` | `white` | `dark.6` (#2e2e2e) |
| `surface.muted` | `gray.1` (#f1f3f5) | `dark.7` (#25262b) |
| `text.primary` | `dark.9` | `gray.0` |
| `text.secondary` | `gray.6` | `dark.2` |
| `border.default` | `gray.3` | `dark.4` |

**Component tokens** — Mantine component theme overrides:

| Component | Override |
|-----------|----------|
| `Paper` | `radius: 'md'`, default shadow |
| `Button` | `radius: 'md'` |
| `TextInput` | `radius: 'sm'` |
| `Badge` | `radius: 'xl'` |
| `Alert` | `radius: 'md'` |
| `Card` | `radius: 'lg'` |

### 4.3. Theme modes

Support light and dark via `MantineProvider colorScheme`. Default: `auto` (follows system).

Toggle mechanism: icon button in AppHeader.

### 4.4. Typography direction

Current (editorial/landing):
```
Iowan Old Style, Palatino Linotype, Book Antiqua, serif
Avenir Next, Segoe UI, sans-serif (headings only)
```

Target (product/dashboard):
```
Inter Variable, Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif  (all text)
ui-monospace, SFMono-Regular, Menlo, Consolas, monospace  (IDs, status codes, hashes)
```

Heading sizes (Mantine defaults, tuned):
- h1: 2rem (page title, max 1 per page)
- h2: 1.5rem (section heading)
- h3: 1.25rem (subsection)
- body: 0.875rem (sm) for dense panels, 1rem (md) for content

### 4.5. Status color mapping (single source of truth)

One mapping used by StatusBadge and all pages. **All keys uppercase. StatusBadge normalizes input before lookup. Fallback: `'neutral'` for unknown, empty, or missing statuses.**

```typescript
// frontend/src/theme/status.ts
type StatusLevel = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

const STATUS_MAP: Record<string, StatusLevel> = {
  // Health
  HEALTHY: 'success',
  CAUTION: 'warning',
  BLOCKED: 'danger',

  // Session
  VALID: 'success',
  NOT_SETUP: 'neutral',
  EXPIRED: 'danger',

  // Run / Step
  RUNNING: 'info',
  DONE: 'success',
  FAILED: 'danger',
  PENDING: 'neutral',
  COMPLETED: 'success',
  PAUSED: 'warning',
  CANCELLED: 'neutral',

  // Stream connection state
  IDLE: 'neutral',
  CONNECTING: 'info',
  CONNECTED: 'success',
  COMPLETE: 'neutral',
  DISCONNECTED: 'warning',

  // Sentiment
  POSITIVE: 'success',
  NEGATIVE: 'danger',
  NEUTRAL: 'neutral',

  // Plan action type
  READ: 'info',
  WRITE: 'danger',
};

const STATUS_COLORS: Record<StatusLevel, MantineColor> = {
  success: 'green',
  warning: 'yellow',
  danger: 'red',
  info: 'blue',
  neutral: 'gray',
};

function normalizeStatus(status?: string | null): string {
  return status?.trim().toUpperCase() ?? '';
}

function getStatusLevel(status?: string | null): StatusLevel {
  return STATUS_MAP[normalizeStatus(status)] ?? 'neutral';
}

function getStatusColor(status?: string | null): MantineColor {
  return STATUS_COLORS[getStatusLevel(status)];
}
```

Implementation rule:
- If a page introduces a new status string, add it to `theme/status.ts` before using it in `StatusBadge`
- Do not create page-local status color mappings

---

## 5. Shared Shell Architecture

### 5.1. Shell structure

Replace the current `<main className="shell">` + hero + grids with:

```text
MantineProvider (theme, colorScheme, notifications)
  Notifications (position="top-right")
  AppShell (header height=60)
    AppShell.Header
      AppHeader (app identity, color scheme toggle, API links)
    AppShell.Main
      Container (size="lg", ~1100px)
        [page content via PageSection]
```

### 5.2. AppHeader replaces hero

Current hero block (App.tsx:39-61) is **removed entirely**.

The hero showed:
- Eyebrow "Social Listening v3"
- Large heading "Setup and health controls are live."
- Long summary paragraph
- 4 API links as pill buttons

This becomes `AppHeader` (slim, 60px):
- Left: app name "Social Listening v3" (text, not hero)
- Center/right: API quick links as compact ButtonGroup (secondary variant)
- Right: color scheme toggle (ActionIcon)

No large heading. No summary paragraph. No decorative gradient.

### 5.3. Checkpoint cards — removed

The 3 checkpoint cards at the bottom of App.tsx are **removed entirely**.

```typescript
// REMOVED — these were dev status placeholders, not user-facing content
const checkpoints = [
  "Phase 2 labeling schema active",
  "Audience-aware themes active",
  "Trust panel and backfill ready",
];
```

Rationale: product shell should not contain decorative informational cards with no user action. If platform capability status is needed in the future, it belongs in release notes or a status notification — not cards on the main UI.

### 5.4. Layout migration

Current App.tsx layout:
```
hero section (removed)
grid-main (1.3fr / 0.7fr: SetupPage | HealthBadge)
grid-workflows (2 cols: 5 workflow pages)
grid (3 cols: 3 checkpoint cards) (removed)
```

Target layout:
```
AppHeader (slim, fixed)
Container
  Stack (spacing="lg")
    SimpleGrid (cols={base:1, sm:2}): [SetupPage, HealthBadge]  — equal columns
    SimpleGrid (cols={base:1, sm:2}): [KeywordPage, PlanPage, ApprovePage, MonitorPage, ThemesPage]
```

Equal columns for SetupPage + HealthBadge (replacing 1.3fr/0.7fr). Rationale: the unequal ratio was a landing-page aesthetic choice. Product shell with Paper panels looks more consistent with equal columns.

### 5.5. Shell responsibilities

Shell owns:
- App identity and header
- Page-level spacing
- Color scheme switching
- Notification host (ready, usage deferred to future phases)
- Container width constraint

Shell does NOT own:
- Page business logic
- Domain-specific state
- API calls

### 5.6. Notifications strategy

`@mantine/notifications` is installed and `<Notifications>` host is mounted in ThemeProvider.

**Phase 4 does NOT migrate any existing inline errors/warnings to toasts.** All page-level error feedback stays as inline `<Alert>`. Toast notifications are reserved for future async background events (e.g. "Run completed", "Labeling done"). The host is set up now so future phases don't need to touch the provider layer.

---

## 6. Shared UI Primitives

### 6.1. Component inventory

| Component | Purpose | Mantine base | Used by |
|-----------|---------|-------------|---------|
| `PageSection` | Replaces `.workflow-card`, `.setup-card`, `.health-panel`, `.card` | `Paper` + `Stack` | All pages |
| `PageHeader` | Replaces repeated eyebrow + h2 pattern | `Title` + `Text` | All pages |
| `StatusBadge` | Replaces `.badge-*`, `.sentiment-*`, `.monitor-step-*` | `Badge` | HealthBadge, SetupPage, MonitorPage, ThemesPage |
| `ActionBar` | Replaces `.button-row` | `Group` | All workflow pages |
| `EmptyState` | Placeholder when no data loaded | `Stack` + `Text` | Optional — only add if needed during migration |
| `KeyValueRow` | Replaces inline `<p className="workflow-meta">key: value</p>` pattern | `Group` + `Text` | All pages |

### 6.2. Component specifications

**PageSection**
```tsx
type PageSectionProps = {
  children: React.ReactNode;
  withBorder?: boolean;  // default true
  p?: MantineSpacing;    // default "lg"
};
// Renders: <Paper shadow="xs" radius="lg" p={p} withBorder={withBorder}>
```

**PageHeader**
```tsx
type PageHeaderProps = {
  eyebrow: string;       // e.g. "Setup", "Monitor"
  title: string;         // e.g. "Ket noi Facebook 1 lan, reuse session ve sau."
  description?: string;
};
// Renders: <Stack gap={4}>
//   <Text size="xs" tt="uppercase" c="dimmed" fw={600} lts="0.1em">{eyebrow}</Text>
//   <Title order={3} size="h4">{title}</Title>
//   {description && <Text size="sm" c="dimmed">{description}</Text>}
// </Stack>
```

**StatusBadge**
```tsx
type StatusBadgeProps = {
  status?: string | null; // any status string — normalized safely
  label?: string;        // override display text
  withDot?: boolean;     // default false
};
// Normalizes: trim() + toUpperCase() → STATUS_MAP → MantineColor
// Fallback: 'neutral' (gray) for unknown, empty, or missing statuses
// Renders: <Badge color={color} variant="light" leftSection={dot}>{label ?? status ?? 'UNKNOWN'}</Badge>
```

**ActionBar**
```tsx
type ActionBarProps = {
  children: React.ReactNode;  // Button elements
};
// Renders: <Group gap="sm" mt="sm">{children}</Group>
```

**KeyValueRow**
```tsx
type KeyValueRowProps = {
  label: string;
  value: React.ReactNode;
  mono?: boolean;  // monospace font for IDs/hashes
};
// Renders: <Group gap="xs">
//   <Text size="sm" c="dimmed">{label}:</Text>
//   <Text size="sm" ff={mono ? 'monospace' : undefined}>{value}</Text>
// </Group>
```

---

## 7. File Structure

### 7.1. New files to create

```text
frontend/src/
  app/
    providers/
      ThemeProvider.tsx      — MantineProvider + Notifications wrapper
    shell/
      AppLayout.tsx          — AppShell + Container + responsive layout
      AppHeader.tsx          — header bar with identity, links, theme toggle
  components/
    ui/
      PageSection.tsx        — Paper-based section wrapper
      PageHeader.tsx         — eyebrow + title primitive
      StatusBadge.tsx        — unified status badge
      ActionBar.tsx          — button group wrapper
      KeyValueRow.tsx        — label: value display row
  theme/
    index.ts                 — createTheme() + Mantine theme object
    tokens.ts                — spacing, radius, shadow, color constants
    status.ts                — STATUS_MAP + getStatusLevel + getStatusColor
```

Total new files: **11**

### 7.2. Files to modify

| File | Change |
|------|--------|
| `frontend/package.json` | Add @mantine/core, @mantine/hooks, @mantine/notifications, @fontsource-variable/inter |
| `frontend/src/main.tsx` | Import Mantine CSS, Inter font, wrap App in ThemeProvider |
| `frontend/src/App.tsx` | Remove hero + checkpoints, replace grids with AppLayout + SimpleGrid |
| `frontend/src/components/HealthBadge.tsx` | Replace CSS classes with PageSection + StatusBadge + KeyValueRow |
| `frontend/src/pages/SetupPage.tsx` | Replace `.setup-card` with PageSection + PageHeader + StatusBadge + Mantine Button/TextInput |
| `frontend/src/pages/KeywordPage.tsx` | Replace `.workflow-card` with PageSection + PageHeader + Mantine form components |
| `frontend/src/pages/PlanPage.tsx` | Replace with PageSection + PageHeader + StatusBadge for write actions |
| `frontend/src/pages/ApprovePage.tsx` | Replace with PageSection + Mantine Checkbox + ActionBar |
| `frontend/src/pages/MonitorPage.tsx` | Replace with PageSection + StatusBadge + ActionBar + KeyValueRow |
| `frontend/src/pages/ThemesPage.tsx` | Replace with PageSection + StatusBadge + Mantine SegmentedControl for filters |
| `frontend/src/styles.css` | Remove all component classes, keep only minimal global resets |

Total modified files: **11**

### 7.3. Files unchanged

| File | Reason |
|------|--------|
| `frontend/src/lib/api.ts` | Pure utility, no presentation |
| `frontend/src/vite-env.d.ts` | Type declaration |
| `frontend/index.html` | No changes needed (see Section 3) |

---

## 8. Migration Plan (Step by Step)

### Step 1 — Install + Foundation

1. Install packages:
   ```
   cd frontend && npm install @mantine/core @mantine/hooks @mantine/notifications @fontsource-variable/inter
   ```

2. Create `frontend/src/theme/tokens.ts` — raw token constants
3. Create `frontend/src/theme/status.ts` — status mapping with uppercase keys + normalize helper
4. Create `frontend/src/theme/index.ts` — `createTheme()` with all overrides
5. Create `frontend/src/app/providers/ThemeProvider.tsx` — MantineProvider + Notifications host
6. Update `frontend/src/main.tsx`:
   ```ts
   import '@mantine/core/styles.css';
   import '@mantine/notifications/styles.css';
   import '@fontsource-variable/inter';
   ```
   Wrap `<App />` in `<ThemeProvider>`

### Step 2 — Shell + Primitives

1. Create `frontend/src/app/shell/AppHeader.tsx`
2. Create `frontend/src/app/shell/AppLayout.tsx`
3. Create `frontend/src/components/ui/PageSection.tsx`
4. Create `frontend/src/components/ui/PageHeader.tsx`
5. Create `frontend/src/components/ui/StatusBadge.tsx`
6. Create `frontend/src/components/ui/ActionBar.tsx`
7. Create `frontend/src/components/ui/KeyValueRow.tsx`

EmptyState: only create if needed during page migration. Do not create speculatively.

### Step 3 — Page Migration

Migration order (dependency-based):

1. **App.tsx** — remove hero + checkpoints, replace with AppLayout + SimpleGrid
2. **HealthBadge.tsx** — simple, validates StatusBadge works
3. **SetupPage.tsx** — simple, validates PageSection + PageHeader
4. **KeywordPage.tsx** — medium complexity, validates form components
5. **PlanPage.tsx** — validates step rendering pattern
6. **ApprovePage.tsx** — validates checkbox + ActionBar
7. **MonitorPage.tsx** — most complex, validates all primitives
8. **ThemesPage.tsx** — validates SegmentedControl + StatusBadge

Per-page migration pattern:
```
1. Keep all state/effect/handler logic at top — do not touch
2. Replace return JSX only:
   <section className="workflow-card">     → <PageSection>
   <p className="eyebrow"> + <h2>         → <PageHeader eyebrow="..." title="...">
   <input className="text-input">         → <TextInput>
   <textarea className="text-input ...">  → <Textarea>
   <div className="button-row">           → <ActionBar>
   <button className="connect-button">    → <Button>
   <button className="ghost-button">      → <Button variant="light">
   <p className="error-copy">             → <Alert color="red" variant="light">
   <p className="warning-copy">           → <Alert color="yellow" variant="light">
   <p className="workflow-meta">key: val  → <KeyValueRow label="key" value="val">
   <span className="badge-*">            → <StatusBadge status="...">
   <span className="sentiment-*">        → <StatusBadge status="...">
3. Remove all className references to styles.css classes
```

### Step 4 — CSS Cleanup

After all pages migrated, reduce `styles.css` to:

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

Remove all other classes. Target: <10 lines.

---

## 9. Page-Specific Migration Details

### 9.1. App.tsx

**Before:**
```
<main className="shell">
  <section className="hero"> ... </section>
  <div className="grid grid-main"> SetupPage + HealthBadge </div>
  <section className="grid grid-workflows"> 5 workflow pages </section>
  <section className="grid"> 3 checkpoint cards </section>
</main>
```

**After:**
```
<AppLayout>
  <Stack gap="lg">
    <SimpleGrid cols={{ base: 1, sm: 2 }}>
      <SetupPage />
      <HealthBadge />
    </SimpleGrid>
    <SimpleGrid cols={{ base: 1, sm: 2 }}>
      <KeywordPage ... />
      <PlanPage ... />
      <ApprovePage ... />
      <MonitorPage ... />
      <ThemesPage ... />
    </SimpleGrid>
  </Stack>
</AppLayout>
```

Removed: hero section, checkpoints array, checkpoint card grid.
State management (`activeContextId`, `activePlanId`, `activeRunId`) and callbacks: **unchanged**.

### 9.2. HealthBadge.tsx

Replace:
- `<section className="health-panel">` -> `<PageSection>`
- `<div className={colors[status.status]}>` -> `<StatusBadge status={status.status} withDot>`
- `<p className="health-meta">` -> `<KeyValueRow>` or `<Text size="sm">`

All polling logic: **untouched**.

### 9.3. SetupPage.tsx

Replace:
- `<section className="setup-card">` -> `<PageSection>`
- `<p className="eyebrow">Setup</p>` + `<h2>` -> `<PageHeader eyebrow="Setup" title="...">`
- Session status and health status must render via `<StatusBadge status={status.session_status} />` and `<StatusBadge status={status.health_status} />`
- `<p className="setup-copy">` descriptive copy/message -> `<Text size="sm">` or `<KeyValueRow>` when it is true key/value metadata
- `<button className="connect-button">` -> `<Button>`
- `<code>{hash}</code>` -> `<Code>{hash}</Code>`

All useEffect, useState, EventSource, onConnect logic: **untouched**.

### 9.4. KeywordPage.tsx

Replace:
- `<section className="workflow-card">` -> `<PageSection>`
- `<input className="text-input">` -> `<TextInput>`
- `<textarea>` -> `<Textarea>`
- `<div className="button-row">` -> `<ActionBar>`
- `<button className="connect-button">` -> `<Button>`
- `<button className="ghost-button">` -> `<Button variant="light">`
- `<div className="clarification-history-item">` -> `<Paper p="sm" radius="sm" bg="gray.0">`
- `<p className="error-copy">` -> `<Alert color="red" variant="light">`
- keyword groups -> `<Stack>` with `<Text fw={600}>` + `<Text>`

All session/clarification logic: **untouched**.

### 9.5. PlanPage.tsx

Replace:
- Step cards: `<article className="plan-step plan-step-write">` -> `<Paper p="sm" withBorder>` with conditional red border for WRITE steps
- `<p className="step-explain">` -> `<Alert variant="light" color="blue" p="xs">`
- `<p className="warning-copy">` -> `<Alert color="yellow" variant="light">`
- Inline status: use `<StatusBadge status={step.read_or_write}>` for READ/WRITE

All generate/refine logic: **untouched**.

### 9.6. ApprovePage.tsx

Replace:
- `<label className="approve-item">` -> Mantine `<Checkbox>` inside `<Paper p="sm">`
- WRITE highlight: conditional border color on Paper
- `<p className="warning-copy">` -> `<Alert color="yellow" variant="light">`

All approval/run logic: **untouched**.

### 9.7. MonitorPage.tsx

Replace:
- Step cards: `<article className="monitor-step monitor-step-running">` -> `<Paper p="sm">` with `<StatusBadge status={step.status}>`
- Event log: `<div className="event-log">` -> `<Paper p="sm" radius="sm" bg="gray.0"><Stack gap={4}><Code block>...</Code></Stack></Paper>`
- Button group -> `<ActionBar>` with `<Button variant="light">`
- Label panel -> `<Paper>` sub-panel with `<KeyValueRow>` rows
- Label chips: `<span className="label-chip">` -> `<Badge variant="light">`
- `streamStatus` and `labelSummary.status` must render via `<StatusBadge>` using the central map, not plain text

All EventSource, controlRun, labeling logic: **untouched**.

### 9.8. ThemesPage.tsx

Replace:
- Filter chips -> `<SegmentedControl>` with data array for 3 audience filters
- Theme cards: `<article className="theme-card">` -> `<Paper p="sm">`
- Sentiment: `<span className="sentiment sentiment-positive">` -> `<StatusBadge status={sentiment}>`
- Breakdown chips: `<span className="label-chip">` -> `<Badge variant="light">`
- Quote list: `<ul className="tag-list">` -> `<List>` or `<Stack gap="xs">`

All theme loading/filter logic: **untouched**.

---

## 10. Dev Rules

1. Business logic (state, API calls, event handlers) stays untouched inside page components.
2. Only Mantine. No second UI library.
3. Do not expand `styles.css`. Every new UI element uses Mantine components or theme tokens.
4. Any pattern used 2+ times across pages becomes a shared primitive in `components/ui/`.
5. Use `StatusBadge` for ALL status display — no page-local color definitions.
6. Use `PageSection` for ALL card/panel containers — no one-off card classes.
7. Use `PageHeader` for ALL page header patterns — no inline eyebrow/h2 combos.
8. Accessibility baseline: Mantine provides focus states and disabled states by default — do not override them.
9. Status strings always normalized via `toUpperCase()` before mapping — no duplicate lowercase/uppercase keys.

---

## 11. Acceptance Criteria

Phase 4 is complete when:

- [ ] `MantineProvider` wraps the entire app with light/dark support
- [ ] `theme/index.ts` exists with `createTheme()` defining brand colors, spacing, radius, typography, component overrides
- [ ] `theme/status.ts` provides single status-to-color mapping with uppercase normalization
- [ ] `AppLayout` wraps all content with `AppShell` + `AppHeader`
- [ ] Hero section removed, replaced by compact AppHeader
- [ ] Checkpoint cards removed
- [ ] At least 5 shared UI primitives exist in `components/ui/` (PageSection, PageHeader, StatusBadge, ActionBar, KeyValueRow)
- [ ] All 6 pages + HealthBadge migrated to use shell + primitives
- [ ] `styles.css` reduced to <10 lines of global resets
- [ ] `cd frontend && npm run build` succeeds with no type errors
- [ ] No API contracts or request flows changed
- [ ] Dark mode toggle works
- [ ] Inter font loads via `@fontsource-variable/inter`

---

## 12. Non-goals

- Pixel-perfect visual polish
- Router architecture changes
- Shared domain widgets
- Chart/visualization framework
- Animation system
- Full multi-app Blackbird shell
- Multi-brand theme support (just leave the door open via Mantine's theme structure)
- FOUC prevention in index.html
- Toast notification usage (host only, usage deferred)

---

## 13. Locked Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Font: `@fontsource-variable/inter` via npm, system monospace | No CDN dependency. Monospace only for IDs — not worth extra font. |
| 2 | Notifications: host only, no migration | Inline Alert is correct UX for form errors. Toast for async events in future phases. |
| 3 | No index.html changes | Internal tool. Minor dark mode flash is acceptable. |
| 4 | No PostCSS config | No CSS modules used. All presentation via Mantine props. |
| 5 | STATUS_MAP: uppercase-only keys, normalize in StatusBadge | One convention, no duplicates. `toUpperCase()` before lookup, fallback `'neutral'`. |
| 6 | Equal columns for SetupPage + HealthBadge | 1.3fr/0.7fr was landing aesthetic. Equal columns suit product shell. |
| 7 | Checkpoint cards removed | Dev placeholders. No user action. Product shell should not have decorative info cards. |
| 8 | Remove hero entirely | Landing-page pattern incompatible with product shell. App identity moves to header. |
| 9 | Keep single scroll view | No router needed yet. SimpleGrid preserves current UX. |
| 10 | Keep state management local | Context/store refactor out of scope. Callback chain works. |
| 11 | SegmentedControl for ThemesPage | Better product UX than pill-button toggles. Same behavior. |
