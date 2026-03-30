# CP8 Validation Checklist — Theme Analysis

**Danh cho:** Validator Agent
**Doc truoc:** `docs/phases/phase-1/checkpoints/cp8-theme-analysis/result.json`
**Muc tieu:** Verify theme classification, sentiment labels, spam filter, PII masking, UI display.

---

## Buoc 0 — Bao bat dau validate

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp8-theme-analysis/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "validator",
    "status": "VALIDATING",
    "summary": "Bat dau validate CP8 — Theme Analysis",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

### CHECK-01: Theme API response

```bash
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys; d=json.load(sys.stdin)
assert 'themes' in d and len(d['themes']) > 0, 'No themes'
for t in d['themes']:
    for f in ['theme_id','label','dominant_sentiment','post_count','sample_quotes']:
        assert f in t, f'Missing field: {f}'
print(f'PASS — {len(d[\"themes\"])} themes, {d[\"posts_crawled\"]} posts')
"
```

**Expected:** PASS with theme count
**Fail if:** Missing fields or 0 themes

---

### CHECK-02: Theme labels in taxonomy

```bash
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys; d=json.load(sys.stdin)
valid = {'pain_point','positive_feedback','question','comparison','other'}
for t in d['themes']:
    assert t['label'] in valid, f'Invalid label: {t[\"label\"]}'
print('PASS')
"
```

**Expected:** PASS
**Fail if:** Label outside taxonomy

---

### CHECK-03: Sentiment labels

```bash
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys; d=json.load(sys.stdin)
valid = {'positive','negative','neutral'}
for t in d['themes']:
    assert t['dominant_sentiment'] in valid, f'Invalid sentiment: {t[\"dominant_sentiment\"]}'
print(f'PASS — sentiments: {[t[\"dominant_sentiment\"] for t in d[\"themes\"]]}')
"
```

**Expected:** PASS
**Fail if:** Sentiment outside valid set

---

### CHECK-04: Spam exclusion

```bash
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys; d=json.load(sys.stdin)
print(f'posts_excluded: {d.get(\"posts_excluded\", \"MISSING\")}')
assert 'posts_excluded' in d
print('PASS')
"
```

**Expected:** posts_excluded field exists (value >= 0)
**Fail if:** Field missing

---

### CHECK-05: PII masked quotes

```bash
curl -s "http://localhost:8000/api/runs/$RUN_ID/themes" | python3 -c "
import json, sys, re
d=json.load(sys.stdin)
for t in d['themes']:
    for q in t['sample_quotes']:
        assert not re.search(r'0\d{9,10}', q), f'Phone number found in quote: {q[:50]}'
        assert not re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', q), f'Email found in quote: {q[:50]}'
print('PASS — no PII in quotes')
"
```

**Expected:** PASS
**Fail if:** Raw phone or email in quotes

---

### CHECK-06: Low post count warning

```bash
# Create a run with few posts, or check code for warning logic
grep -r "10.*post\|warning\|dai dien" backend/app/services/insight.py | head -3
```

**Expected:** Warning logic present for < 10 posts
**Fail if:** No warning logic

---

### CHECK-07: ThemesPage UI

```bash
grep -ri "theme\|sentiment\|quote\|pain_point\|positive" frontend/src/pages/ThemesPage.tsx | head -5
```

**Expected:** >= 1 match
**Fail if:** File missing or no relevant content

---

## Ghi ket qua

```json
{
  "cp": "cp8-theme-analysis",
  "role": "validator",
  "status": "PASS | FAIL | PARTIAL",
  "timestamp": "<ISO8601>",
  "summary": "<1-2 cau>",
  "checks": [...],
  "issues": [],
  "ready_for_next_cp": true,
  "next_cp": "cp9-smoke-test"
}
```

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05
**Warning checks:** CHECK-06, CHECK-07

## Gui notification

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp8-theme-analysis \
    --role validator \
    --status PASS \
    --summary "Theme analysis verified — first visible value." \
    --result-file docs/phases/phase-1/checkpoints/cp8-theme-analysis/validation.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp8-theme-analysis/validation.json
```
