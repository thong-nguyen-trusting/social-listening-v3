# CP0 — Phase 3 Environment Setup

**Mục tiêu:** Chuẩn bị foundation cho Phase 3 — settings, shared utils, migration, skeleton service.
**Requires:** Phase 2 code present in codebase.

---

## Bước 1 — Tạo `text_utils.py`

File: `backend/app/infra/text_utils.py`

Extract `_strip_diacritics` từ `ai_client.py` thành shared utility. Thêm `tokenize_vn` và `token_overlap_score`.

```python
import re

_DIACRITICS_MAP = str.maketrans({
    "à": "a", "á": "a", "ả": "a", "ã": "a", "ạ": "a",
    "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
    "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
    "đ": "d",
    "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
    "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
    "ì": "i", "í": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
    "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
    "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
    "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
    "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
    "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
    "ỳ": "y", "ý": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
    # uppercase variants...
})

def strip_diacritics(text: str) -> str: ...
def tokenize_vn(text: str) -> set[str]: ...
def token_overlap_score(text_a: str, text_b: str) -> float: ...
```

## Bước 2 — Tạo skeleton `pipeline_intelligence.py`

File: `backend/app/services/pipeline_intelligence.py`

```python
from app.infrastructure.config import Settings

class PipelineIntelligence:
    def __init__(self, settings: Settings) -> None:
        self._group_relevance_threshold = settings.group_relevance_threshold
        self._group_quality_threshold = settings.group_quality_threshold
        self._enabled = settings.pipeline_intelligence_enabled
```

## Bước 3 — Thêm settings vào config.py

Thêm vào class `Settings`:

```python
group_relevance_threshold: float = 0.15
group_quality_threshold: float = 0.70
priority_budget_high: float = 0.60
priority_budget_medium: float = 0.30
priority_budget_low: float = 0.10
pipeline_intelligence_enabled: bool = True
```

## Bước 4 — Thêm HEURISTIC_LABELED vào taxonomy

File: `backend/app/domain/label_taxonomy.py`

Thêm `"HEURISTIC_LABELED"` vào `LABEL_RECORD_STATUSES` tuple.

## Bước 5 — Tạo migration 007

File: `backend/alembic/versions/007_add_heuristic_labeled_status.py`

Pattern giống migration 005/006 — `batch_alter_table("crawled_posts", recreate="always")`, drop old constraint, create new with `HEURISTIC_LABELED` added.

## Bước 6 — Verify syntax

```bash
python -c "import ast; ast.parse(open('backend/app/infra/text_utils.py').read()); print('OK')"
python -c "import ast; ast.parse(open('backend/app/services/pipeline_intelligence.py').read()); print('OK')"
```

## Bước 7 — Viết result.json và gửi notification

```bash
uv run python docs/phases/phase-3/checkpoints/notify.py \
    --cp cp0-phase3-setup \
    --role implementer \
    --status READY \
    --summary "Phase 3 foundation: text_utils, skeleton PipelineIntelligence, settings, migration 007" \
    --result-file docs/phases/phase-3/checkpoints/cp0-phase3-setup/result.json

python3 docs/phases/phase-3/checkpoints/post-status.py \
    --result-file docs/phases/phase-3/checkpoints/cp0-phase3-setup/result.json
```
