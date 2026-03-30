# CP5 — Filtered Theme API

**Muc tieu:** Bien theme analysis thanh policy-aware va explainable.
**Requires:** CP4 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp5-filtered-theme-api/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP5 — Filtered Theme API",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Policy engine

- Tao `AudienceFilterPolicy`
- Map presets -> include/exclude rules
- Ho tro comment duoc include du cha post commercial

## Buoc 2 — InsightService

- Load current labels
- Tinh `posts_included`, `posts_excluded`, `excluded_breakdown`
- Van giu warning low-volume khi can

## Buoc 3 — API/schema

- Them query param `audience_filter`
- Them response fields cho UI trust layer

## Buoc 4 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
