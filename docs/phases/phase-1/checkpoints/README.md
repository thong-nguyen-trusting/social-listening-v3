# Checkpoint System — AI Facebook Social Listening v3 / Phase 1: Safe Core Loop

## Luồng làm việc

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
| CP0 | cp0-environment | Environment Setup | -- | 0.5 ngay |
| CP1 | cp1-schema-lock | Schema Lock + DB Migration | CP0 | 1 ngay |
| CP2 | cp2-browser-session | Browser Session Setup | CP1 | 1.5 ngay |
| CP3 | cp3-health-monitor | Health Monitor | CP2 | 1.5 ngay |
| CP4 | cp4-keyword-analysis | Keyword Analysis | CP1, CP3 | 2 ngay |
| CP5 | cp5-plan-generation | Plan Generation | CP4 | 2 ngay |
| CP6 | cp6-review-approve | Review & Approve | CP5 | 1.5 ngay |
| CP7 | cp7-execution-engine | Execution Engine | CP6, CP2 | 3 ngay |
| CP8 | cp8-theme-analysis | Theme Analysis | CP7 | 2 ngay |
| CP9 | cp9-smoke-test | End-to-end Smoke Test | CP8 | 1 ngay |

## Sprint Mapping

| Sprint | Checkpoints | Focus |
|--------|------------|-------|
| Sprint 1A | CP0, CP1, CP2, CP3, CP4, CP5 | Safety infra + planning foundation |
| Sprint 1B | CP6, CP7 | Approval gate + execution loop |
| Sprint 1C | CP8, CP9 | First visible output |

## Cau truc moi CP folder

```
docs/phases/phase-1/checkpoints/cp{N}-{name}/
  README.md          # Dashboard import (AI parse)
  INSTRUCTIONS.md    # Huong dan implement
  CHECKLIST.md       # Danh sach validate
  result.json        # Implementer viet (auto)
  validation.json    # Validator viet (auto)
```

## Setup

```bash
cp docs/phases/phase-1/checkpoints/config.example.json \
   docs/phases/phase-1/checkpoints/config.json
# Sua ntfy_topic va project_slug thanh gia tri cua ban
```
