# CP5 — Workflow Pages Migration B

**Muc tieu:** Migrate MonitorPage va ThemesPage, chot central status rendering cho cac UX phuc tap nhat.
**Requires:** CP4 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp5-workflow-pages-migration-b/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP5 — Workflow Pages Migration B",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Migrate `frontend/src/pages/MonitorPage.tsx`

- Dung `PageSection` + `PageHeader`
- Button group -> `ActionBar`
- `streamStatus`, `run.status`, `step.status`, `labelSummary.status` -> `StatusBadge`
- Metadata rows -> `KeyValueRow`
- Event log -> `Paper` + `Code` / `Stack`
- Label chips -> `Badge variant="light"`
- Giu nguyen SSE / refresh / control logic

## Buoc 2 — Migrate `frontend/src/pages/ThemesPage.tsx`

- Dung `PageSection` + `PageHeader`
- Audience filters -> `SegmentedControl`
- Theme cards -> `Paper`
- Sentiment -> `StatusBadge`
- Excluded breakdown -> `Badge`
- Quotes -> `List` hoac `Stack`

## Buoc 3 — Verify migration

```bash
rg -n "StatusBadge|ActionBar|KeyValueRow|Badge|Paper" frontend/src/pages/MonitorPage.tsx
rg -n "SegmentedControl|StatusBadge|Badge|Paper" frontend/src/pages/ThemesPage.tsx
cd frontend && npm run build
```

## Buoc 4 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp5-workflow-pages-migration-b \
    --role implementer \
    --status READY \
    --summary "MonitorPage va ThemesPage da migrate sang shared Mantine primitives va central status rendering" \
    --result-file docs/phases/phase-4/checkpoints/cp5-workflow-pages-migration-b/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp5-workflow-pages-migration-b/result.json
```
