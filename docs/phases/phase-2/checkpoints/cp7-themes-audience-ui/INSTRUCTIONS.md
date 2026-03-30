# CP7 — Themes Audience UI

**Muc tieu:** Dua trust/filter controls len Themes page.
**Requires:** CP5 PASS, CP6 PASS

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp7-themes-audience-ui/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP7 — Themes Audience UI",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Filter presets

- Them 3 preset:
  - `End-user only`
  - `Include seller`
  - `Include brand`

## Buoc 2 — Summary va UX

- Hien `posts_included`, `posts_excluded`, `excluded_by_label_count`
- Hien breakdown
- Disable request khi loading

## Buoc 3 — Viet result.json va gui status

Tao `result.json` va post len dashboard bang `notify.py` + `post-status.py`.
