# CP1 — Mantine Theme Foundation

**Muc tieu:** Dat theme foundation, dependency setup, va provider wiring cho toan bo frontend.
**Requires:** CP0 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp1-mantine-theme-foundation/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP1 — Mantine Theme Foundation",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Cai dependencies trong `frontend/`

```bash
cd frontend
npm install @mantine/core @mantine/hooks @mantine/notifications @fontsource-variable/inter
```

## Buoc 2 — Tao theme files

- Tao `frontend/src/theme/tokens.ts` voi primitive tokens cho colors, spacing, radius, shadows, font families
- Tao `frontend/src/theme/status.ts` voi:
  - `STATUS_MAP` uppercase-only keys
  - `normalizeStatus(status)` = `trim().toUpperCase()`
  - `getStatusLevel()` va `getStatusColor()`
  - fallback `neutral`
- Tao `frontend/src/theme/index.ts` voi `createTheme()` va component overrides cho `Paper`, `Button`, `TextInput`, `Badge`, `Alert`, `Card`

## Buoc 3 — Tao provider va wire vao entrypoint

- Tao `frontend/src/app/providers/ThemeProvider.tsx`
- Mount `MantineProvider` + `Notifications`
- Update `frontend/src/main.tsx`:
  - import `@mantine/core/styles.css`
  - import `@mantine/notifications/styles.css`
  - import `@fontsource-variable/inter`
  - wrap `<App />` trong `ThemeProvider`

## Buoc 4 — Verify foundation build

```bash
cd frontend && npm run build
```

## Buoc 5 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp1-mantine-theme-foundation \
    --role implementer \
    --status READY \
    --summary "Mantine deps, theme files, status map, ThemeProvider, va main.tsx wiring da xong" \
    --result-file docs/phases/phase-4/checkpoints/cp1-mantine-theme-foundation/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp1-mantine-theme-foundation/result.json
```
