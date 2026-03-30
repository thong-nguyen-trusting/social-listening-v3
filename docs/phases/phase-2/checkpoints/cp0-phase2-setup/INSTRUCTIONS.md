# CP0 — Phase 2 Setup & Contracts

**Muc tieu:** Dung workspace, scripts, config, va dashboard project rieng cho Phase 2.
**Requires:** Phase 1 docs da co, dashboard local co the truy cap tai `http://localhost:3000`

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3-phase-2/checkpoints/cp0-phase2-setup/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP0 — Phase 2 Setup & Contracts",
    "readyForNextTrigger": false
  }'
```

Neu project/chkpoint chua import, bo qua buoc nay va tiep tuc.

## Buoc 1 — Chot checkpoint structure

- Tao `docs/phases/phase-2/checkpoints/`
- Dat ten CP va dependency nhu checkpoint README cua phase-2
- Copy `notify.py`, `post-status.py`, `config.example.json`, `config.json` tu phase-1 sang phase-2

## Buoc 2 — Chot config dashboard

- Doi `project_slug` trong `docs/phases/phase-2/checkpoints/config*.json` thanh `social-listening-v3-phase-2`
- Cap nhat `.phase.json` de phase-2 co `checkpoints: 9`
- Dam bao docs Phase 2 nhac ro lifecycle rieng cua labeling

## Buoc 3 — Import dashboard project

- Tao project moi `AI Facebook Social Listening v3 — Phase 2`
- Import 9 checkpoints vao dashboard project do
- Verify `GET /api/projects/social-listening-v3-phase-2` tra ve 9 checkpoints

## Buoc 4 — Viet result.json va gui status

Tao `docs/phases/phase-2/checkpoints/cp0-phase2-setup/result.json`:

```json
{
  "cp": "cp0-phase2-setup",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Phase 2 checkpoint workspace va dashboard project da san sang.",
  "artifacts": [
    {"file": "docs/phases/phase-2/checkpoints/README.md", "action": "created"},
    {"file": "docs/phases/phase-2/checkpoints/config.json", "action": "created"}
  ],
  "issues": [],
  "notes": "Project dashboard moi dung slug social-listening-v3-phase-2."
}
```

```bash
uv run python docs/phases/phase-2/checkpoints/notify.py \
  --cp cp0-phase2-setup \
  --role implementer \
  --status READY \
  --summary "Phase 2 checkpoint workspace va dashboard project da san sang." \
  --result-file docs/phases/phase-2/checkpoints/cp0-phase2-setup/result.json

python3 docs/phases/phase-2/checkpoints/post-status.py \
  --result-file docs/phases/phase-2/checkpoints/cp0-phase2-setup/result.json
```
