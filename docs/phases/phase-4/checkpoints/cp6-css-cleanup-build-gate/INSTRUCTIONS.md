# CP6 — CSS Cleanup + Build Gate

**Muc tieu:** Dong refactor Phase 4 bang cleanup CSS va build/smoke verification.
**Requires:** CP5 PASS.

---

## Buoc 0 — Bao bat dau

```bash
curl -s -X POST "http://localhost:3000/api/projects/ai-facebook-social-listening-engagement-v3-phase-4/checkpoints/cp6-css-cleanup-build-gate/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau CP6 — CSS Cleanup + Build Gate",
    "readyForNextTrigger": false
  }'
```

## Buoc 1 — Thu gon `frontend/src/styles.css`

File nay chi duoc giu:

```css
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}
```

Khong them class selectors moi. Khong de `styles.css` tiep tuc lam source of truth cho UI.

## Buoc 2 — Chay build gate

```bash
cd frontend && npm run build
```

## Buoc 3 — Ghi smoke notes

Tao `docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/DEMO_LOG.md` va ghi ngan gon:

- timestamp
- ket qua `npm run build`
- xac nhan hero va checkpoint cards da bi xoa
- xac nhan app header + theme toggle hien dien
- xac nhan pages render trong shell moi

## Buoc 4 — Verify final gate

```bash
wc -l frontend/src/styles.css
rg -n "\\.workflow-card|\\.setup-card|\\.health-panel|\\.theme-card|\\.monitor-step" frontend/src/styles.css
cd frontend && npm run build
```

## Buoc 5 — Viet result.json va gui notification

```bash
uv run python docs/phases/phase-4/checkpoints/notify.py \
    --cp cp6-css-cleanup-build-gate \
    --role implementer \
    --status READY \
    --summary "styles.css da duoc cleanup, build gate pass, va smoke notes da duoc ghi" \
    --result-file docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/result.json

python3 docs/phases/phase-4/checkpoints/post-status.py \
    --result-file docs/phases/phase-4/checkpoints/cp6-css-cleanup-build-gate/result.json
```
