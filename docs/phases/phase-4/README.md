# Phase 4 — Shared Shell UI Refactor
## AI Facebook Social Listening & Engagement v3

**Status:** Implementation-ready — all decisions locked
**Depends on:** Phase 3 — Smart Crawl Pipeline
**Updated:** 2026-03-29

---

## Goal

Phase 4 khong thay doi business runtime cua app.

Phase nay tap trung vao:

> Dua frontend hien tai ve dung huong `Shared Product Shell` cua Blackbird, de app nay co the gan vao shared platform sau Phase 1 ma khong bi lech ve UI architecture.

Cu the, Phase 4 se:

- chuan hoa design system bang Mantine (sole UI library)
- tao theme va token foundation voi `createTheme()`, light/dark support
- xoa hero landing pattern, thay bang compact AppHeader
- xoa checkpoint placeholder cards
- dua app ve 1 shell layout dung chuan product app (`AppShell` + `AppHeader` + `Container`)
- chuan hoa component patterns bang shared UI primitives (PageSection, PageHeader, StatusBadge, ActionBar, KeyValueRow)
- thong nhat status color mapping (1 file `status.ts`, uppercase keys, normalize trong StatusBadge)
- migrate 6 pages + HealthBadge sang shell va primitives moi
- thu gon `styles.css` xuong duoi 10 dong global resets

---

## Expected Outcomes

- App duoc wrap bang `MantineProvider` voi light/dark support
- Co `theme/index.ts` voi token system va `createTheme()` ro rang
- Co `theme/status.ts` lam single source of truth cho status-to-color mapping
- Co `AppLayout` (AppShell + AppHeader) thay the hero + manual grids
- Co 5+ shared UI primitives duoc dung lai across pages
- 6 pages + HealthBadge da migrate sang shell va primitives
- `styles.css` con duoi 10 dong — khong con la source of truth cua UI
- Inter font loaded via `@fontsource-variable/inter`
- Dark mode toggle hoat dong
- `npm run build` thanh cong

---

## Documents

- [Architecture](./architecture.md) — source of truth cho moi quyet dinh ky thuat
- [UI Refactor Agent Brief](./ui-refactor-agent-brief.md) — implementation instructions cho agent

Architecture la authoritative. Neu agent brief hoac README conflict voi architecture, architecture thang.

---

## Non-goals

- Khong doi flow backend/API
- Khong doi nghiep vu crawl/plan/approve/monitor
- Khong lam pixel-perfect visual polish
- Khong build full multi-app navigation
- Khong shared domain widgets qua som
- Khong them router architecture
- Khong them PostCSS / CSS modules
- Khong sua index.html
- Khong migrate inline errors sang toast notifications (host only)
- Khong them UI framework thu 2
