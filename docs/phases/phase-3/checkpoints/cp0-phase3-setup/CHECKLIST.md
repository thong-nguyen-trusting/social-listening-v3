# CP0 Validation Checklist — Phase 3 Environment Setup

**Dành cho:** Validator Agent
**Đọc trước:** `docs/phases/phase-3/checkpoints/cp0-phase3-setup/result.json`
**Mục tiêu:** Verify foundation files tồn tại, import được, và migration chạy thành công.

---

### CHECK-01: text_utils.py import được

```bash
cd backend && python -c "from app.infra.text_utils import strip_diacritics, tokenize_vn, token_overlap_score; print('OK')"
```

**Expected:** `OK`
**Fail if:** ImportError hoặc ModuleNotFoundError

---

### CHECK-02: strip_diacritics hoạt động đúng

```bash
cd backend && python -c "from app.infra.text_utils import strip_diacritics; assert strip_diacritics('mỹ phẩm') == 'my pham', f'Got: {strip_diacritics(\"mỹ phẩm\")}'; print('OK')"
```

**Expected:** `OK`
**Fail if:** assertion error

---

### CHECK-03: token_overlap_score hoạt động

```bash
cd backend && python -c "from app.infra.text_utils import token_overlap_score; score = token_overlap_score('mỹ phẩm thiên nhiên', 'REVIEW MỸ PHẨM SKINCARE'); print(f'score={score:.2f}'); assert score > 0.3, f'Score too low: {score}'"
```

**Expected:** score > 0.3
**Fail if:** score <= 0.3 hoặc error

---

### CHECK-04: PipelineIntelligence import được

```bash
cd backend && python -c "from app.services.pipeline_intelligence import PipelineIntelligence; print('OK')"
```

**Expected:** `OK`
**Fail if:** ImportError

---

### CHECK-05: Settings có Phase 3 fields

```bash
cd backend && python -c "
from app.infrastructure.config import Settings
s = Settings()
assert hasattr(s, 'pipeline_intelligence_enabled'), 'missing pipeline_intelligence_enabled'
assert hasattr(s, 'group_relevance_threshold'), 'missing group_relevance_threshold'
assert hasattr(s, 'group_quality_threshold'), 'missing group_quality_threshold'
print(f'enabled={s.pipeline_intelligence_enabled} grp_threshold={s.group_relevance_threshold} quality={s.group_quality_threshold}')
print('OK')
"
```

**Expected:** `OK` with default values printed
**Fail if:** AttributeError

---

### CHECK-06: HEURISTIC_LABELED in taxonomy

```bash
cd backend && python -c "from app.domain.label_taxonomy import LABEL_RECORD_STATUSES; assert 'HEURISTIC_LABELED' in LABEL_RECORD_STATUSES, f'Not found in {LABEL_RECORD_STATUSES}'; print('OK')"
```

**Expected:** `OK`
**Fail if:** assertion error

---

### CHECK-07: Migration 007 applies cleanly

```bash
docker exec social-listening-v3 alembic upgrade head 2>&1 | tail -5
```

**Expected:** No errors, migration applied or already at head
**Fail if:** Error in migration

---

## Ghi kết quả

Tạo `docs/phases/phase-3/checkpoints/cp0-phase3-setup/validation.json`

**Blocker checks:** CHECK-01, CHECK-02, CHECK-03, CHECK-04, CHECK-05, CHECK-06, CHECK-07
**Warning checks:** (none)

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp0-phase3-setup \
    --role validator \
    --status PASS \
    --summary "Phase 3 foundation verified" \
    --result-file docs/phases/phase-3/checkpoints/cp0-phase3-setup/validation.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp0-phase3-setup/validation.json
```
