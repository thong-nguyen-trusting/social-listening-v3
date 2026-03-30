# CP2 — Taxonomy + Prompt Contract

**Muc tieu:** Freeze taxonomy va prompt contract truoc khi viet engine.
**Requires:** CP0 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp2-taxonomy-prompt/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP2 — Taxonomy + Prompt Contract",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Tao taxonomy source of truth

- Tao constants cho `author_role`, `content_intent`, `commerciality_level`, `user_feedback_relevance`
- Them audience presets `end_user_only`, `include_seller`, `include_brand`

## Buoc 2 — Viet prompt

- Tao `content_labeling.md`
- JSON-only output
- Co `label_reason`, `label_confidence`, `label_source`
- Khong cho chain-of-thought

## Buoc 3 — Heuristic signals

- Tao helper file cho markers seller, end-user, official, admin
- Khong exclude record o day; chi pre-score

## Buoc 4 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
