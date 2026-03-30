# CP5 Validation Checklist — Filtered Theme API

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp5-filtered-theme-api/result.json`
**Muc tieu:** Verify theme API da dung labels va filter policy.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp5-filtered-theme-api/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP5 — Filtered Theme API",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: End-user only

```bash
curl -s "http://localhost:8000/api/runs/<run_id>/themes?audience_filter=end_user_only"
```

**Expected:** Tra response hop le voi themes
**Fail if:** API fail hoac bo qua filter

### CHECK-02: Include seller changes counts

```bash
curl -s "http://localhost:8000/api/runs/<run_id>/themes?audience_filter=include_seller"
```

**Expected:** `posts_included`/`posts_excluded` khac voi `end_user_only`
**Fail if:** Counts giong nhau du seller labels ton tai

### CHECK-03: Excluded breakdown

```bash
curl -s "http://localhost:8000/api/runs/<run_id>/themes?audience_filter=end_user_only" | jq
```

**Expected:** Co `excluded_by_label_count` va `excluded_breakdown`
**Fail if:** Thieu field

### CHECK-04: Read-time policy

```bash
sqlite3 backend/app.db "select distinct is_excluded, exclude_reason from crawled_posts;"
```

**Expected:** Khong phu thuoc vao 1 permanent theme exclusion duy nhat
**Fail if:** Solution van hard-mark records theo 1 policy co dinh

### CHECK-05: Response metadata

```bash
curl -s "http://localhost:8000/api/runs/<run_id>/themes?audience_filter=end_user_only" | jq '.audience_filter,.taxonomy_version'
```

**Expected:** Echo dung filter va version
**Fail if:** UI khong the biet policy nao dang duoc dung

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
