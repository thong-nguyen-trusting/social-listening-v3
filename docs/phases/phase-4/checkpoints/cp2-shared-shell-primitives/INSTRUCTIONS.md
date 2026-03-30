# CP2 — Shared Shell + UI Primitives

**Muc tieu:** Tao shell va reusable UI primitives de chuan hoa migration cho tat ca pages.
**Requires:** CP1 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp2-shared-shell-primitives/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP2 — Shared Shell + UI Primitives",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Tao shell components

- Tao `frontend/src/app/shell/AppHeader.tsx`
  - Left: `Social Listening v3`
  - Center/right: API quick links
  - Right: color scheme toggle
- Tao `frontend/src/app/shell/AppLayout.tsx`
  - `AppShell`
  - header height 60
  - `Container size="lg"`

## Buoc 2 — Tao UI primitives

- `PageSection.tsx` -> `Paper`
- `PageHeader.tsx` -> eyebrow + title + optional description
- `StatusBadge.tsx` -> `Badge` + central status map
- `ActionBar.tsx` -> `Group gap="sm"`
- `KeyValueRow.tsx` -> dimmed label + value, optional monospace

## Buoc 3 — Verify primitive contracts

```bash
rg -n "AppShell|Container" frontend/src/app/shell/AppLayout.tsx
rg -n "ActionIcon|Social Listening v3|apiUrl" frontend/src/app/shell/AppHeader.tsx
rg -n "Badge|getStatusColor" frontend/src/components/ui/StatusBadge.tsx
cd frontend && npm run build
```

## Buoc 4 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp2-shared-shell-primitives \
    --role implementer \
    --status READY \
    --summary "App shell va 5 UI primitives da san sang cho page migration" \
    --result-file docs/phases/phase-4/checkpoints/cp2-shared-shell-primitives/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp2-shared-shell-primitives/result.json
```
