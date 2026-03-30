# CP6 Validation Checklist — CSS Cleanup + Build Gate

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/result.json`
**Muc tieu:** Verify Phase 4 da dong bang cleanup CSS, build xanh, va smoke notes ro rang.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp6-css-cleanup-build-gate/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP6 — CSS Cleanup + Build Gate",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: styles.css con nho hon 10 dong

```bash
wc -l frontend/src/styles.css | awk '{print $1}'
```

**Expected:** So dong < `10`
**Fail if:** `styles.css` van con nhieu CSS component rules

---

### CHECK-02: styles.css khong con class selectors cu

```bash
if rg -n "\\.workflow-card|\\.setup-card|\\.health-panel|\\.theme-card|\\.monitor-step" frontend/src/styles.css; then exit 1; else echo OK; fi
```

**Expected:** `OK`
**Fail if:** Van con class selectors cu

---

### CHECK-03: Build gate pass

```bash
cd frontend && npm run build
```

**Expected:** Build succeeds
**Fail if:** TypeScript/Vite build fail

---

### CHECK-04: DEMO_LOG.md ton tai va co smoke notes

```bash
test -f docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/DEMO_LOG.md \
  && rg -n "build|hero|theme toggle|header|shell" docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/DEMO_LOG.md \
  && echo OK
```

**Expected:** `OK`
**Fail if:** Khong co DEMO_LOG hoac thieu smoke notes

---

## Ghi ket qua

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04
**Warning checks:** (none)

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp6-css-cleanup-build-gate \
    --role validator \
    --status PASS \
    --summary "Phase 4 cleanup/build gate verified" \
    --result-file docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/validation.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/validation.json
```
