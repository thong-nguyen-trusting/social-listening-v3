# CP4 — Workflow Pages Migration A

**Muc tieu:** Migrate Keyword, Plan, Approve pages sang Mantine components va shared primitives.
**Requires:** CP3 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp4-workflow-pages-migration-a/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP4 — Workflow Pages Migration A",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Migrate `frontend/src/pages/KeywordPage.tsx`

- `workflow-card` -> `PageSection`
- eyebrow + `h2` -> `PageHeader`
- `input` -> `TextInput`
- `textarea` -> `Textarea`
- `button-row` -> `ActionBar`
- error/warning/meta -> `Alert`, `Text`, `KeyValueRow`
- clarification history items -> `Paper p="sm" radius="sm"`

## Buoc 2 — Migrate `frontend/src/pages/PlanPage.tsx`

- Dung `PageSection` + `PageHeader`
- Dung Mantine buttons/inputs
- Step cards -> `Paper`
- READ/WRITE -> `StatusBadge`
- `step.explain` va warnings -> `Alert`

## Buoc 3 — Migrate `frontend/src/pages/ApprovePage.tsx`

- Dung `PageSection` + `PageHeader`
- `label.approve-item` -> `Paper` + `Checkbox`
- Write steps co visual highlight thong qua Mantine props
- Dung `ActionBar` va `Alert`

## Buoc 4 — Verify migration

```bash
rg -n "PageSection|PageHeader|TextInput|Textarea|ActionBar" frontend/src/pages/KeywordPage.tsx
rg -n "StatusBadge|Paper|Alert" frontend/src/pages/PlanPage.tsx
rg -n "Checkbox|Paper|ActionBar" frontend/src/pages/ApprovePage.tsx
cd frontend && npm run build
```

## Buoc 5 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp4-workflow-pages-migration-a \
    --role implementer \
    --status READY \
    --summary "Keyword, Plan, va Approve pages da migrate sang shared Mantine patterns" \
    --result-file docs/phases/phase-4/checkpoints/cp4-workflow-pages-migration-a/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp4-workflow-pages-migration-a/result.json
```
