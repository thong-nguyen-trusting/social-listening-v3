# CP1 — Labeling Schema + Migration

**Muc tieu:** Lock schema Phase 2 cho content labeling.
**Requires:** CP0 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp1-labeling-schema/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP1 — Labeling Schema + Migration",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Them models moi

- Tao `LabelJob` va `ContentLabel`
- Noi FK voi `plan_runs` va `crawled_posts`
- Them constraints cho `author_role`, `content_intent`, `commerciality_level`, `user_feedback_relevance`, `label_source`

## Buoc 2 — Cap nhat `CrawledPost`

- Them `label_status`
- Them `current_label_id`
- Dam bao default safe la `PENDING`

## Buoc 3 — Tao migration

- Tao Alembic migration
- Verify roundtrip upgrade/downgrade

## Buoc 4 — Viet result.json va gui status

Tao `docs/phases/phase-2/checkpoints/cp1-labeling-schema/result.json` va post len dashboard bang `notify.py` + `post-status.py`.
