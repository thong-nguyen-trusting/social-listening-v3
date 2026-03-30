# CP2 Validation Checklist — Taxonomy + Prompt Contract

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-2/checkpoints/cp2-taxonomy-prompt/result.json`
**Muc tieu:** Verify contract cho labeling da on dinh va testable.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp2-taxonomy-prompt/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP2 — Taxonomy + Prompt Contract",
    "readyForNextTrigger": false
  }'
```

### CHECK-01: Prompt file

```bash
test -f backend/app/skills/content_labeling.md && rg -n "JSON|author_role|label_confidence|label_reason" backend/app/skills/content_labeling.md
```

**Expected:** Prompt ton tai va co required fields
**Fail if:** Thieu field

### CHECK-02: Taxonomy constants

```bash
python3 - <<'PY'
from pathlib import Path
print(Path("backend/app/domain/label_taxonomy.py").read_text())
PY
```

**Expected:** Co day du values theo docs
**Fail if:** Khong khop phase-2 architecture

### CHECK-03: Heuristic signals

```bash
rg -n "ib|inbox|official|mình dùng|cho em hỏi|admin" backend/app/services/labeling_heuristics.py
```

**Expected:** Co markers cho nhieu nhom
**Fail if:** Heuristic qua so sai

### CHECK-04: Fallback rules

```bash
rg -n "unknown|medium|fallback" backend/app/skills/content_labeling.md backend/app/domain/label_taxonomy.py
```

**Expected:** Safe fallback duoc define
**Fail if:** Khong co fallback

### CHECK-05: Schema sample

```bash
python3 - <<'PY'
import json
sample = {
  "records":[{"post_id":"p1","author_role":"end_user","content_intent":"question","commerciality_level":"low","user_feedback_relevance":"high","label_confidence":0.91,"label_reason":"question from user","label_source":"ai"}]
}
json.dumps(sample)
print("OK")
PY
```

**Expected:** OK
**Fail if:** Contract mau khong hop le

## Ghi ket qua

Tao `validation.json` va post len dashboard bang `post-status.py`.
