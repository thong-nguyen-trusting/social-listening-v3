# Checkpoint System — AI Facebook Social Listening v3 / Phase 4: Shared Shell UI Refactor

## Tong quan luong lam viec

```text
[Implementation Agent]     [User]        [Validator Agent]
        |                    |                   |
        |  implement CP-N    |                   |
        |------------------>|                   |
        |  write result.json |                   |
        |  run notify.py     |                   |
        |------------------>| notification      |
        |                    | trigger validator>|
        |                    |                   | run CHECKLIST
        |                    |                   | write validation.json
        |                    |<-- notification --|
        |  [PASS] trigger N+1|                   |
        |<------------------|                   |
```

## Checkpoints

| CP | Code | Ten | Noi dung | Depends On | Sprint | Effort |
|----|------|-----|----------|------------|--------|--------|
| CP0 | cp0-phase4-setup | Phase 4 Setup | Tao workspace checkpoint, config dashboard, phase metadata | — | 4A | 0.5d |
| CP1 | cp1-mantine-theme-foundation | Mantine Theme Foundation | Install deps, theme tokens, status map, ThemeProvider, main.tsx wiring | CP0 | 4A | 1d |
| CP2 | cp2-shared-shell-primitives | Shared Shell + UI Primitives | AppHeader, AppLayout, PageSection, PageHeader, StatusBadge, ActionBar, KeyValueRow | CP1 | 4A | 1d |
| CP3 | cp3-entry-surfaces-migration | Entry Surfaces Migration | Migrate App.tsx, HealthBadge.tsx, SetupPage.tsx | CP2 | 4B | 1d |
| CP4 | cp4-workflow-pages-migration-a | Workflow Pages Migration A | Migrate KeywordPage.tsx, PlanPage.tsx, ApprovePage.tsx | CP3 | 4B | 1d |
| CP5 | cp5-workflow-pages-migration-b | Workflow Pages Migration B | Migrate MonitorPage.tsx, ThemesPage.tsx | CP4 | 4B | 1d |
| CP6 | cp6-css-cleanup-build-gate | CSS Cleanup + Build Gate | Thu gon styles.css, build gate, smoke notes | CP5 | 4C | 0.5d |

## Sprint Mapping

| Sprint | Checkpoints | Focus |
|--------|-------------|-------|
| Sprint 4A | CP0, CP1, CP2 | Setup + theme foundation + shell primitives |
| Sprint 4B | CP3, CP4, CP5 | App/page migration theo do phuc tap tang dan |
| Sprint 4C | CP6 | CSS cleanup, build verification, smoke gate |

## Cau truc moi CP folder

```text
docs/phases/phase-4/checkpoints/cp{N}-{name}/
├── README.md
├── INSTRUCTIONS.md
├── CHECKLIST.md
├── result.json
└── validation.json
```

## Setup

```bash
cp docs/phases/phase-4/checkpoints/config.example.json \
   docs/phases/phase-4/checkpoints/config.json
# Sua ntfy_topic neu can; project_slug mac dinh cho Phase 4 la ai-facebook-social-listening-engagement-v3-phase-4
```
