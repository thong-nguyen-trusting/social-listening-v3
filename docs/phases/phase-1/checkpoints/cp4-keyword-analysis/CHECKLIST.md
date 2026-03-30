# CP4 Validation Checklist — Keyword Analysis

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp4-keyword-analysis/result.json`
**Muc tieu:** Verify keyword analysis flow: topic → AI → 5-category keywords → ProductContext in DB.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp4-keyword-analysis/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP4 — Keyword Analysis",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Topic → keywords 5 categories

```bash
curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Khach hang nghi gi ve TPBank EVO?"}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
kw = d.get('keywords', {})
cats = ['brand','pain_points','sentiment','behavior','comparison']
for c in cats:
    assert c in kw, f'Missing category: {c}'
    assert len(kw[c]) > 0, f'Empty category: {c}'
print(f'PASS — {sum(len(kw[c]) for c in cats)} keywords across 5 categories')
"
```

**Expected:** PASS with keyword counts
**Fail if:** Missing category or empty category

---

### CHECK-02: Diacritics included

```bash
curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Phan hoi ve dich vu giao hang"}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
kw_text = json.dumps(d.get('keywords',{}))
has_diacritic = any(c in kw_text for c in 'àáảãạăắằẳẵặâấầẩẫậ')
has_no_diacritic = any(w.isascii() for w in kw_text.split())
print(f'Diacritics: {has_diacritic}, ASCII: {has_no_diacritic}')
assert has_diacritic, 'No diacritics found'
print('PASS')
"
```

**Expected:** PASS
**Fail if:** No Vietnamese diacritics in output

---

### CHECK-03: Ambiguous topic → clarification

```bash
curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "ban hang"}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
status = d.get('status')
assert status == 'clarification_required', f'Expected clarification, got {status}'
assert d.get('clarifying_questions') and len(d['clarifying_questions']) > 0
print(f'PASS — {len(d[\"clarifying_questions\"])} questions returned')
"
```

**Expected:** PASS with questions
**Fail if:** Returns keywords instead of questions

---

### CHECK-04: PATCH keywords

```bash
# Get context_id from previous call, then patch
CONTEXT_ID=$(curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "Review san pham skincare"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['context_id'])")

curl -s -X PATCH "http://localhost:8000/api/sessions/$CONTEXT_ID/keywords" \
  -H "Content-Type: application/json" \
  -d '{"keywords": {"brand": ["CeraVe", "La Roche-Posay"], "pain_points": ["da nhon"], "sentiment": ["thich"], "behavior": ["ib minh"], "comparison": ["vs"]}}' | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert d.get('status') == 'keywords_ready'
print('PASS')
"
```

**Expected:** PASS, status=keywords_ready
**Fail if:** Error or status incorrect

---

### CHECK-05: ProductContext in DB

```bash
cd backend && sqlite3 app.db "SELECT context_id, status, keyword_json IS NOT NULL as has_kw FROM product_contexts LIMIT 3;"
```

**Expected:** At least 1 row with status=keywords_ready and has_kw=1
**Fail if:** No rows or keyword_json is null

---

### CHECK-06: Prompt caching

```bash
cd backend && grep -r "cache_control" app/infra/ai_client.py | head -3
```

**Expected:** At least 1 line with cache_control ephemeral
**Fail if:** No cache_control found

---

### CHECK-07: KeywordPage UI

```bash
curl -s http://localhost:5173 2>/dev/null | grep -ci "keyword\|topic"
```

**Expected:** >= 1
**Fail if:** 0

---

## Ghi ket qua

```json
{
  "cp": "cp4-keyword-analysis",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp5-plan-generation"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp4-keyword-analysis \
    --role validator \
    --status PASS \
    --summary "Keyword analysis verified — 5 categories, Vietnamese NLP, clarification flow." \
    --result-file docs/phases/phase-1/checkpoints/cp4-keyword-analysis/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp4-keyword-analysis/validation.json
```
