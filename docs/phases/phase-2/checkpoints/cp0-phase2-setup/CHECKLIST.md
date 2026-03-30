# CP0 Validation Checklist — Phase 2 Setup & Contracts

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp0-phase2-setup/result.json`
**Muc tieu:** Verify Phase 2 co workspace checkpoint rieng va dashboard project moi.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp0-phase2-setup/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP0 — Phase 2 Setup & Contracts",
    "readyForNextTrigger": false
  }'
```

## Danh sach kiem tra

### CHECK-01: Checkpoint workspace ton tai

```bash
find docs/phases/phase-2/checkpoints -maxdepth 1 -type f | sort
```

**Expected:** Co `README.md`, `config.json`, `notify.py`, `post-status.py`
**Fail if:** Thieu bat ky file nao

### CHECK-02: Project slug dung

```bash
cat docs/phases/phase-2/checkpoints/config.json
```

**Expected:** `project_slug` = `social-listening-v3-phase-2`
**Fail if:** slug khac hoac de trong

### CHECK-03: Phase metadata

```bash
cat .phase.json
```

**Expected:** phase-2 ton tai va `checkpoints` = 9
**Fail if:** checkpoint count sai

### CHECK-04: Dashboard project

```bash
curl -s http://localhost:3000/api/projects/social-listening-v3-phase-2
```

**Expected:** project ton tai va co 9 checkpoints
**Fail if:** 404 hoac `checkpoints=[]`

### CHECK-05: Docs contract

```bash
rg -n "label_jobs|content_labels|read-time" docs/phases/phase-2/architecture.md docs/phases/phase-2/user-stories.md
```

**Expected:** Co contract kien truc Phase 2
**Fail if:** docs chua noi ro boundaries

## Ghi ket qua

Tao `docs/phases/phase-2/checkpoints/cp0-phase2-setup/validation.json` va post len dashboard bang `post-status.py`.
