# CP4 — Keyword Analysis

**Code:** cp4-keyword-analysis
**Order:** 4
**Depends On:** cp1-schema-lock, cp3-health-monitor
**Estimated Effort:** 2 ngay

## Muc tieu

Implement US-01: user nhap topic tieng Viet → AI (Opus 4.6) tra ve keywords theo 5 nhom (brand, pain_points, sentiment, behavior, comparison). ProductContext duoc tao va luu trong DB.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/infra/ai_client.py | created | Claude API wrapper voi adaptive thinking + streaming + prompt caching |
| backend/app/services/planner.py | created | PlannerService.analyze_topic() |
| backend/app/skills/keyword_analysis.md | created | Vietnamese NLP keyword skill prompt |
| backend/app/api/plans.py | created | POST /api/sessions, PATCH /api/sessions/{id}/keywords |
| backend/app/schemas/plans.py | created | Pydantic schemas cho session/keyword API |
| frontend/src/pages/KeywordPage.tsx | created | Topic input + keyword editor UI |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | POST /api/sessions voi topic tieng Viet tra ve keywords JSON voi 5 categories | yes |
| CHECK-02 | Keywords bao gom ca dang co dau va khong dau | yes |
| CHECK-03 | Topic mo ho → tra ve clarifying_questions thay vi keywords | yes |
| CHECK-04 | PATCH /api/sessions/{id}/keywords cho phep edit va persist | yes |
| CHECK-05 | ProductContext duoc luu trong DB voi status keywords_ready sau confirm | yes |
| CHECK-06 | AIClient su dung prompt caching (cache_control trong system prompt) | no |
| CHECK-07 | KeywordPage hien thi keywords grouped va cho phep add/remove/edit | no |
