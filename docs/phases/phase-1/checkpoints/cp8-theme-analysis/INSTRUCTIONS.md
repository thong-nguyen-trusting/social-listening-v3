# CP8 — Theme Analysis

**Muc tieu:** InsightService classify themes + sentiment tu crawled posts. First visible value.
**Requires:** CP7 PASS (co crawled_posts trong DB)

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp8-theme-analysis/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP8 — Theme Analysis (first visible value)",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — Theme classification prompt

Tao `backend/app/skills/theme_classification.md`:
- Input: list of post texts (PII-masked)
- Output: JSON array of themes, moi theme co:
  - label: pain_point | positive_feedback | question | comparison | other
  - dominant_sentiment: positive | negative | neutral
  - post_count: so posts thuoc theme nay
  - sample_quotes: 2-3 representative quotes (max 200 chars each)
- Vietnamese-aware: hieu slang, viet tat
- Taxonomy: 5 categories max cho Lite version

## Buoc 2 — InsightService

Tao `backend/app/services/insight.py` theo architecture.md Section 6.5:

```python
class InsightService:
    async def analyze_themes(self, run_id: str) -> ThemeAnalysis:
        # 1. Load crawled posts
        posts = await repo.get_posts_for_run(run_id)

        # 2. Filter noise (spam, seller posts)
        clean_posts, excluded = self._filter_noise(posts)

        # 3. Warning if < 10 posts
        warning = "It hon 10 posts..." if len(clean_posts) < 10 else None

        # 4. Batch classify voi claude-haiku-4-5
        themes = await ai_client.classify_themes(
            posts=clean_posts,
            model="claude-haiku-4-5",
            taxonomy=["pain_point","positive_feedback","question","comparison","other"],
            include_sentiment=True,
        )

        # 5. PII mask sample quotes
        for theme in themes:
            theme.sample_quotes = [pii_masker.mask(q) for q in theme.sample_quotes]

        # 6. Persist
        await repo.save_theme_results(run_id, themes)
        return ThemeAnalysis(themes=themes, warning=warning, excluded_count=len(excluded))

    def _filter_noise(self, posts) -> Tuple[List, List]:
        # Rule-based: regex cho spam patterns
        # "Ban gap — ib ngay", "Hang sale soc", repeated emoji patterns
        ...
```

## Buoc 3 — Insight API

Tao `backend/app/api/insights.py`:
- `GET /api/runs/{run_id}/themes` — goi analyze_themes() (hoac return cached)
- Response schema:
  ```json
  {
    "run_id": "...",
    "posts_crawled": 47,
    "posts_excluded": 5,
    "themes": [
      {
        "theme_id": "...",
        "label": "pain_point",
        "dominant_sentiment": "negative",
        "post_count": 12,
        "sample_quotes": ["...", "..."]
      }
    ],
    "warning": null
  }
  ```

## Buoc 4 — Frontend ThemesPage

Tao `frontend/src/pages/ThemesPage.tsx`:
- Header: posts crawled, posts excluded
- Warning banner (neu co)
- Theme cards/list:
  - Theme label (translated to Vietnamese: "Van de / Diem dau", "Phan hoi tich cuc", ...)
  - Sentiment badge: Positive (xanh), Negative (do), Neutral (xam)
  - Post count
  - 2-3 sample quotes
- Click theme → "Full comment analysis available in Phase 2" note

## Buoc 5 — Viet result.json va gui notification

```json
{
  "cp": "cp8-theme-analysis",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Theme analysis with Haiku 4.5. 5 categories, sentiment labels, spam filter, PII masking.",
  "artifacts": [
    {"file": "backend/app/services/insight.py", "action": "created"},
    {"file": "backend/app/skills/theme_classification.md", "action": "created"},
    {"file": "backend/app/api/insights.py", "action": "created"},
    {"file": "frontend/src/pages/ThemesPage.tsx", "action": "created"}
  ],
  "issues": [],
  "notes": "Requires crawled posts from CP7 run."
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp8-theme-analysis \
    --role implementer \
    --status READY \
    --summary "Theme analysis — first visible value delivered." \
    --result-file docs/phases/phase-1/checkpoints/cp8-theme-analysis/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp8-theme-analysis/result.json
```
