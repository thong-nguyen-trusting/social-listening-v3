# Checkpoint System — AI Facebook Social Listening v3 / Phase 3: Smart Crawl Pipeline

## Tổng quan luồng làm việc

```
[Implementation Agent]     [User]        [Validator Agent]
        │                    │                   │
        │  implement CP-N    │                   │
        │──────────────────>│                   │
        │  write result.json │                   │
        │  run notify.py     │                   │
        │──────────────────>│ notification      │
        │                    │ trigger validator>│
        │                    │                   │ run CHECKLIST
        │                    │                   │ write validation.json
        │                    │<── notification ──│
        │  [PASS] trigger N+1│                   │
        │<──────────────────│                   │
```

## Checkpoints

| CP | Code | Tên | Nội dung | Depends On | Sprint | Effort |
|----|------|-----|---------|------------|--------|--------|
| CP0 | cp0-phase3-setup | Environment Setup | text_utils, skeleton PipelineIntelligence, settings, migration 007 | — | 3A | 0.5d |
| CP1 | cp1-group-relevance | Group Relevance Scoring | score_group_relevance(), runner interceptors for JOIN/SEARCH_IN_GROUP | CP0 | 3A | 1d |
| CP2 | cp2-early-heuristic | Early Heuristic Labeling | heuristic_label_posts() after SEARCH_POSTS, label_status=HEURISTIC_LABELED | CP0 | 3A | 1d |
| CP3 | cp3-priority-crawl | Priority-Based Comment Crawl | prioritize_post_refs(), CRAWL_COMMENTS sorted by tier, budget 60/30/10 | CP2 | 3B | 1d |
| CP4 | cp4-quality-gate | Group Quality Gate | quality_gate_groups(), filter SEARCH_IN_GROUP by post quality ratio | CP1, CP2 | 3B | 0.5d |
| CP5 | cp5-pipeline-summary | Pipeline Summary API | build_pipeline_summary(), enrich GET /api/runs response | CP1-4 | 3B | 0.5d |
| CP6 | cp6-pipeline-dashboard | Pipeline Dashboard UI | Frontend funnel visualization in MonitorPage | CP5 | 3C | 1d |
| CP7 | cp7-smoke-test | E2E Smoke Test | Mock + real browser, verify funnel metrics, target >70% relevant | CP6 | 3C | 0.5d |

## Sprint Mapping

| Sprint | Checkpoints | Focus |
|--------|-------------|-------|
| Sprint 3A | CP0, CP1, CP2 | Foundation + scoring + labeling |
| Sprint 3B | CP3, CP4, CP5 | Priority crawl + quality gate + API |
| Sprint 3C | CP6, CP7 | Dashboard UI + smoke test |

## Cấu trúc mỗi CP folder

```
docs/phases/phase-3/checkpoints/cp{N}-{name}/
├── README.md          # Dashboard import (AI parse)
├── INSTRUCTIONS.md    # Hướng dẫn implement
├── CHECKLIST.md       # Danh sách validate
├── result.json        # Implementer viết (auto)
└── validation.json    # Validator viết (auto)
```

## Setup

```bash
cp docs/phases/phase-3/checkpoints/config.example.json \
   docs/phases/phase-3/checkpoints/config.json
# Sửa ntfy_topic thành tên unique của bạn
```
