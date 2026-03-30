# Checkpoint System — AI Facebook Social Listening v3 / Phase 2: Trustworthy Feedback Labeling

## Luong lam viec

```
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

| CP | Code | Ten | Depends On | Effort |
|----|------|-----|------------|--------|
| CP0 | cp0-phase2-setup | Phase 2 Setup & Contracts | -- | 0.5 ngay |
| CP1 | cp1-labeling-schema | Labeling Schema + Migration | CP0 | 1 ngay |
| CP2 | cp2-taxonomy-prompt | Taxonomy + Prompt Contract | CP0 | 1 ngay |
| CP3 | cp3-label-job-orchestration | Label Job Orchestration | CP1, CP2 | 1 ngay |
| CP4 | cp4-content-labeling-engine | Content Labeling Engine | CP3 | 2 ngay |
| CP5 | cp5-filtered-theme-api | Filtered Theme API | CP4 | 1.5 ngay |
| CP6 | cp6-monitor-labeling-ui | Monitor Labeling UI | CP3 | 1 ngay |
| CP7 | cp7-themes-audience-ui | Themes Audience UI | CP5, CP6 | 1.5 ngay |
| CP8 | cp8-audit-backfill-smoke | Audit, Backfill & Smoke | CP7 | 1 ngay |

## Sprint Mapping

| Sprint | Checkpoints | Focus |
|--------|-------------|-------|
| Sprint 2A | CP0, CP1, CP2, CP3 | Contracts + data model + orchestration |
| Sprint 2B | CP4, CP5 | AI labeling + policy aware insights |
| Sprint 2C | CP6, CP7, CP8 | UI trust layer + audit + smoke |

## Cau truc moi CP folder

```
docs/phases/phase-2/checkpoints/cp{N}-{name}/
  README.md
  INSTRUCTIONS.md
  CHECKLIST.md
  result.json
  validation.json
```

## Setup

```bash
cp docs/phases/phase-2/checkpoints/config.example.json \
   docs/phases/phase-2/checkpoints/config.json
# Sua ntfy_topic neu can; project_slug da tro san toi social-listening-v3-phase-2
```
