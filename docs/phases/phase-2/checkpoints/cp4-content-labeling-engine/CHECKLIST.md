# CP4 Validation Checklist — Content Labeling Engine

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp4-content-labeling-engine/result.json`
**Muc tieu:** Verify engine labeling hoat dong va persist dung.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp4-content-labeling-engine/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP4 — Content Labeling Engine",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Persist labels

```bash
sqlite3 backend/app.db "select count(*) from content_labels;"
```

**Expected:** Count > 0 sau khi chay labeling
**Fail if:** Khong persist label

### CHECK-02: Comment independence

```bash
sqlite3 backend/app.db "select post_id, author_role from content_labels join crawled_posts using(post_id) where record_type='COMMENT' limit 5;"
```

**Expected:** Comment labels ton tai rieng
**Fail if:** Comment bi bo qua hoac forced inherit

### CHECK-03: Fallback path

```bash
sqlite3 backend/app.db "select count(*) from content_labels where label_source='fallback';"
```

**Expected:** Fallback path co the ton tai va khong crash
**Fail if:** AI fail lam job dung hoan toan

### CHECK-04: Current label pointer

```bash
sqlite3 backend/app.db "select count(*) from crawled_posts where current_label_id is not null;"
```

**Expected:** Co rows duoc cap nhat
**Fail if:** Pointer rong

### CHECK-05: Batch behavior

```bash
rg -n "batch|records_per_call|chunk" backend/app/services/content_labeling.py backend/app/infra/ai_client.py
```

**Expected:** Co batch strategy
**Fail if:** Code goi model tung record

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
