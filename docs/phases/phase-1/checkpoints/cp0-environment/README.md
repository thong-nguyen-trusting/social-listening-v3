# CP0 — Environment Setup

**Code:** cp0-environment
**Order:** 0
**Depends On:** —
**Estimated Effort:** 0.5 ngay

## Muc tieu

Cai dat toan bo dev environment: Python 3.12, FastAPI, SQLite, Camoufox, React+Vite, Alembic. Sau CP nay, developer co the start backend server va frontend dev server thanh cong.

## Artifacts du kien

| File/Path | Action | Mo ta |
|-----------|--------|-------|
| backend/requirements.txt | created | Python dependencies |
| backend/app/main.py | created | FastAPI entry point (hello world) |
| frontend/package.json | created | React + Vite dependencies |
| frontend/src/App.tsx | created | React hello world |
| alembic.ini | created | Alembic config tro vao SQLite |
| backend/alembic/ | created | Alembic migration directory |
| .gitignore | created | Ignore venv, node_modules, .env, browser_profile |

## Checklist Validator

| ID | Mo ta | Blocker |
|----|-------|---------|
| CHECK-01 | `python --version` tra ve 3.12+ | yes |
| CHECK-02 | `pip install -r backend/requirements.txt` thanh cong, bao gom fastapi, uvicorn, sqlalchemy, anthropic, camoufox | yes |
| CHECK-03 | `python -m camoufox fetch` download duoc patched Firefox binary | yes |
| CHECK-04 | `uvicorn backend.app.main:app --port 8000` start duoc, GET /health tra ve 200 | yes |
| CHECK-05 | `cd frontend && npm install && npm run dev` start duoc, truy cap localhost:5173 thay React app | yes |
| CHECK-06 | `alembic current` chay duoc khong loi (chua co migration nao) | yes |
| CHECK-07 | .gitignore ton tai va chua: venv, node_modules, .env, browser_profile, *.db | no |
