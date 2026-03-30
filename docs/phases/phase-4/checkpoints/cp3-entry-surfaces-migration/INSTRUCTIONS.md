# CP3 — Entry Surfaces Migration

**Muc tieu:** Dua App root, HealthBadge, va SetupPage ve shell/product patterns moi.
**Requires:** CP2 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp3-entry-surfaces-migration/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP3 — Entry Surfaces Migration",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Migrate `frontend/src/App.tsx`

- Xoa `checkpoints` array
- Xoa hero section
- Wrap content trong `AppLayout`
- Dung `SimpleGrid` 2 cot bang nhau cho:
  - `SetupPage` + `HealthBadge`
  - `KeywordPage`, `PlanPage`, `ApprovePage`, `MonitorPage`, `ThemesPage`
- Giu nguyen callback chain `activeContextId -> activePlanId -> activeRunId`

## Buoc 2 — Migrate `frontend/src/components/HealthBadge.tsx`

- Xoa `colors` local mapping
- Dung `PageSection`
- Dung `StatusBadge` cho `status.status`
- Dung `KeyValueRow` hoac `Text` cho cooldown / last signal metadata

## Buoc 3 — Migrate `frontend/src/pages/SetupPage.tsx`

- Dung `PageSection` + `PageHeader`
- Dung `StatusBadge` cho `status.session_status` va `status.health_status`
- Dung Mantine `Button`, `Code`, `Text`
- Giu nguyen `useEffect`, `EventSource`, `onConnect`

## Buoc 4 — Verify migration

```bash
rg -n "AppLayout|SimpleGrid" frontend/src/App.tsx
rg -n "StatusBadge" frontend/src/components/HealthBadge.tsx frontend/src/pages/SetupPage.tsx
cd frontend && npm run build
```

## Buoc 5 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp3-entry-surfaces-migration \
    --role implementer \
    --status READY \
    --summary "App root, HealthBadge, va SetupPage da migrate sang shell/primitives moi" \
    --result-file docs/phases/phase-4/checkpoints/cp3-entry-surfaces-migration/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp3-entry-surfaces-migration/result.json
```
