# CP8 — Theme Analysis

**Code:** cp8-theme-analysis
**Order:** 8
**Depends On:** cp7-execution-engine
**Estimated Effort:** 2 ngay

## Muc tieu

Implement US-04L: InsightService phan tich posts da crawl → 5 theme categories + dominant sentiment per theme. Spam filter, PII masking tren quotes, va UI ThemesPage hien thi ket qua. Day la "first visible value" cua Phase 1.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/app/services/insight.py | created | InsightService: analyze_themes(), _filter_noise() |
| backend/app/skills/theme_classification.md | created | Haiku 4.5 classification prompt (theme + sentiment) |
| backend/app/api/insights.py | created | GET /api/runs/{id}/themes |
| backend/app/schemas/insights.py | created | Pydantic schemas cho theme API |
| frontend/src/pages/ThemesPage.tsx | created | Theme list voi sentiment labels va sample quotes |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | GET /api/runs/{id}/themes tra ve themes voi label, dominant_sentiment, post_count, sample_quotes | yes |
| CHECK-02 | Theme labels nam trong taxonomy: pain_point, positive_feedback, question, comparison, other | yes |
| CHECK-03 | Moi theme co dominant_sentiment: positive, negative, hoac neutral | yes |
| CHECK-04 | Spam posts bi excluded va user thay count excluded | yes |
| CHECK-05 | Sample quotes da duoc PII masked (khong co phone/email) | yes |
| CHECK-06 | Khi < 10 posts → warning message hien thi | no |
| CHECK-07 | ThemesPage hien thi themes grouped voi sentiment labels va quotes | no |
