# CP6 Validation Checklist — Monitor Labeling UI

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp6-monitor-labeling-ui/result.json`
**Muc tieu:** Verify UI monitor cho labeling ro rang va khong nhiu.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp6-monitor-labeling-ui/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP6 — Monitor Labeling UI",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Section ton tai

```bash
rg -n "labeling|label job|records_labeled|taxonomy" frontend/src/pages/MonitorPage.tsx
```

**Expected:** Co section labeling rieng
**Fail if:** UI chua co block nay

### CHECK-02: Counts hien thi

```bash
rg -n "records_total|records_labeled|records_fallback|records_failed" frontend/src/pages/MonitorPage.tsx
```

**Expected:** Co render counts
**Fail if:** Thieu count

### CHECK-03: Khong roi crawl stream

```bash
rg -n "EventSource|stream" frontend/src/pages/MonitorPage.tsx
```

**Expected:** Crawl stream van con logic rieng
**Fail if:** Labeling lam mat monitor run

### CHECK-04: Loading/error

```bash
rg -n "loading|error|statusMessage" frontend/src/pages/MonitorPage.tsx
```

**Expected:** Co states ro rang
**Fail if:** UI im lang khi request fail

### CHECK-05: Warning dang labeling

```bash
rg -n "themes may still change|dang labeling|labeling chua xong" frontend/src/pages/MonitorPage.tsx
```

**Expected:** Co warning copy
**Fail if:** User de hieu nham labeling done

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
