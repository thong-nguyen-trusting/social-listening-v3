# CP1 Validation Checklist — Mantine Theme Foundation

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp1-mantine-theme-foundation/result.json`
**Muc tieu:** Verify Mantine foundation, theme status map, va provider wiring da dung architecture.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp1-mantine-theme-foundation/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP1 — Mantine Theme Foundation",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Package dependencies da duoc them

```bash
rg -n "\"@mantine/core\"|\"@mantine/hooks\"|\"@mantine/notifications\"|\"@fontsource-variable/inter\"" frontend/package.json
```

**Expected:** Co du 4 dependency entries
**Fail if:** Thieu package nao

---

### CHECK-02: status.ts dung central status map

```bash
rg -n "STATUS_MAP|normalizeStatus|getStatusLevel|getStatusColor|toUpperCase\\(|neutral" frontend/src/theme/status.ts
```

**Expected:** Co du status map, normalize helper, va fallback neutral
**Fail if:** File thieu helper hoac mapping local

---

### CHECK-03: ThemeProvider mount MantineProvider va Notifications

```bash
rg -n "MantineProvider|Notifications" frontend/src/app/providers/ThemeProvider.tsx
```

**Expected:** Co ca `MantineProvider` va `Notifications`
**Fail if:** Thieu provider host

---

### CHECK-04: main.tsx import CSS va wrap ThemeProvider

```bash
rg -n "@mantine/core/styles.css|@mantine/notifications/styles.css|@fontsource-variable/inter|ThemeProvider" frontend/src/main.tsx
```

**Expected:** Co 4 imports/wiring
**Fail if:** Entry point chua duoc wrap

---

### CHECK-05: Build qua sau foundation

```bash
cd frontend && npm run build
```

**Expected:** Build succeeds
**Fail if:** TypeScript/Vite build fail

---

## Ghi ket qua

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** (none)

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp1-mantine-theme-foundation \
    --role validator \
    --status PASS \
    --summary "Mantine foundation va theme wiring verified" \
    --result-file docs/phases/phase-4/checkpoints/cp1-mantine-theme-foundation/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp1-mantine-theme-foundation/validation.json
```
