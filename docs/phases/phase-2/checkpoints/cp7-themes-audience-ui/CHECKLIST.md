# CP7 Validation Checklist — Themes Audience UI

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp7-themes-audience-ui/result.json`
**Muc tieu:** Verify audience filter flow tren Themes.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp7-themes-audience-ui/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP7 — Themes Audience UI",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: 3 presets

```bash
rg -n "End-user only|Include seller|Include brand" frontend/src/pages/ThemesPage.tsx
```

**Expected:** Co du 3 preset
**Fail if:** Thieu preset nao

### CHECK-02: Refetch on change

```bash
rg -n "audience_filter|fetchJson|load themes" frontend/src/pages/ThemesPage.tsx
```

**Expected:** Filter doi -> goi API lai
**Fail if:** UI chi doi local state

### CHECK-03: Excluded summary

```bash
rg -n "excluded by label|excluded_breakdown|posts_excluded" frontend/src/pages/ThemesPage.tsx
```

**Expected:** Co render summary
**Fail if:** Khong co trust signal

### CHECK-04: Disable while loading

```bash
rg -n "disabled=.*loading|isLoading|loading" frontend/src/pages/ThemesPage.tsx
```

**Expected:** CTA duoc disable
**Fail if:** User co the spam request

### CHECK-05: Default preset

```bash
rg -n "end_user_only|End-user only" frontend/src/pages/ThemesPage.tsx
```

**Expected:** Default filter = end-user
**Fail if:** Mac dinh khac

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
