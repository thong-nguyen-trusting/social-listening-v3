# CP2 Validation Checklist — Shared Shell + UI Primitives

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp2-shared-shell-primitives/result.json`
**Muc tieu:** Verify shell va primitive contracts da san sang cho migration cac pages.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp2-shared-shell-primitives/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP2 — Shared Shell + UI Primitives",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: AppLayout dung AppShell + Container

```bash
rg -n "AppShell|Container" frontend/src/app/shell/AppLayout.tsx
```

**Expected:** Co ca `AppShell` va `Container`
**Fail if:** Shell wrapper sai hoac thieu

---

### CHECK-02: AppHeader co app name, links, theme toggle

```bash
rg -n "Social Listening v3|ActionIcon|apiUrl|Button" frontend/src/app/shell/AppHeader.tsx
```

**Expected:** Co app name, API link wiring, va `ActionIcon`
**Fail if:** Header thieu identity hoac theme toggle

---

### CHECK-03: Primitive files day du

```bash
test -f frontend/src/components/ui/PageSection.tsx \
  && test -f frontend/src/components/ui/PageHeader.tsx \
  && test -f frontend/src/components/ui/StatusBadge.tsx \
  && test -f frontend/src/components/ui/ActionBar.tsx \
  && test -f frontend/src/components/ui/KeyValueRow.tsx \
  && echo OK
```

**Expected:** `OK`
**Fail if:** Thieu primitive file nao

---

### CHECK-04: StatusBadge dung central status color helper

```bash
rg -n "getStatusColor|normalize|Badge" frontend/src/components/ui/StatusBadge.tsx
```

**Expected:** `StatusBadge` goi helper tu `theme/status.ts`
**Fail if:** Page-local mapping hoac badge hardcode colors

---

### CHECK-05: Build qua sau shell/primitives

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
    --cp cp2-shared-shell-primitives \
    --role validator \
    --status PASS \
    --summary "Shared shell va UI primitives verified" \
    --result-file docs/phases/phase-4/checkpoints/cp2-shared-shell-primitives/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp2-shared-shell-primitives/validation.json
```
