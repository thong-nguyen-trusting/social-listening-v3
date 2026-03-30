# CP0 — Phase 4 Setup

**Muc tieu:** Khoi tao workspace checkpoint va metadata dashboard cho Phase 4.
**Requires:** Docs `docs/phases/phase-4/README.md` va `docs/phases/phase-4/architecture.md` da khoa scope.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp0-phase4-setup/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP0 — Phase 4 Setup",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Tao checkpoint workspace

- Tao `docs/phases/phase-4/checkpoints/`
- Copy `notify.py` va `post-status.py` tu `docs/phases/phase-3/checkpoints/`
- Tao `config.example.json` va `config.json` voi `project_slug=ai-facebook-social-listening-engagement-v3-phase-4`

```bash
mkdir -p docs/phases/phase-4/checkpoints
cp docs/phases/phase-3/checkpoints/notify.py docs/phases/phase-4/checkpoints/notify.py
cp docs/phases/phase-3/checkpoints/post-status.py docs/phases/phase-4/checkpoints/post-status.py
```

## Buoc 2 — Tao checkpoint docs skeleton

- Viet `docs/phases/phase-4/checkpoints/README.md`
- Tao 7 folders CP va 3 files `README.md`, `INSTRUCTIONS.md`, `CHECKLIST.md` cho moi CP
- Breakdown phai theo architecture: setup -> foundation -> shell/primitives -> page migrations -> cleanup

## Buoc 3 — Cap nhat `.phase.json`

- Chuyen `current` sang `phase-4`
- Danh dau `phase-4.status = active`
- Set `phase-4.started = 2026-03-29`
- Set `phase-4.checkpoints = 7`

## Buoc 4 — Verify structure

```bash
find docs/phases/phase-4/checkpoints -maxdepth 2 -type f | sort
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('.phase.json').read_text())
assert data["current"] == "phase-4"
assert data["phases"]["phase-4"]["checkpoints"] == 7
print("OK")
PY
```

## Buoc 5 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp0-phase4-setup \
    --role implementer \
    --status READY \
    --summary "Phase 4 checkpoint workspace, config, scripts, va phase metadata da san sang" \
    --result-file docs/phases/phase-4/checkpoints/cp0-phase4-setup/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp0-phase4-setup/result.json
```
