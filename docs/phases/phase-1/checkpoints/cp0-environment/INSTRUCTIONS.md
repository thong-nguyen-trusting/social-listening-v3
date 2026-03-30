# CP0 — Environment Setup

**Muc tieu:** Cai dat dev environment de backend + frontend + Camoufox chay duoc tren may local.
**Requires:** macOS hoac Windows, Python 3.12+, Node.js 18+

---

## Buoc 0 — Bao bat dau (bat buoc, chay truoc tien)

```bash
curl -s -X POST "http://localhost:3000/api/projects/social-listening-v3/checkpoints/cp0-environment/status" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "implementer",
    "status": "IN_PROGRESS",
    "summary": "Bat dau implement CP0 — Environment Setup",
    "readyForNextTrigger": false
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print('status:', d.get('ok'))"
```

---

## Buoc 1 — Backend Python setup

```bash
mkdir -p backend/app/api backend/app/services backend/app/infra backend/app/models backend/app/schemas backend/app/skills
mkdir -p backend/alembic backend/tests
```

Tao `backend/requirements.txt`:
```
fastapi==0.115.*
uvicorn[standard]==0.34.*
sqlalchemy==2.0.*
alembic==1.14.*
anthropic==0.52.*
camoufox==0.4.*
pydantic==2.11.*
python-dotenv==1.1.*
```

Tao `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Social Listening v3", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

Cai dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Buoc 2 — Camoufox binary

```bash
python -m camoufox fetch
```

Verify:
```bash
python -c "from camoufox.async_api import AsyncCamoufox; print('Camoufox OK')"
```

## Buoc 3 — Alembic init

```bash
cd backend
alembic init alembic
```

Sua `alembic.ini`:
```ini
sqlalchemy.url = sqlite:///%(here)s/app.db
```

Sua `alembic/env.py` de import models (se them model o CP1).

## Buoc 4 — Frontend React + Vite

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

Verify: `npm run dev` → localhost:5173 hien React app.

## Buoc 5 — .gitignore

Tao `.gitignore` o project root:
```
# Python
backend/venv/
__pycache__/
*.pyc
*.db

# Node
frontend/node_modules/
frontend/dist/

# Environment
.env
.env.local

# Browser profile (sensitive — contains FB session)
browser_profile/
~/.social-listening/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

## Buoc 6 — Viet result.json va gui notification

```json
{
  "cp": "cp0-environment",
  "role": "implementer",
  "status": "READY",
  "timestamp": "<ISO8601>",
  "summary": "Environment setup complete. Python 3.12, FastAPI, Camoufox, React+Vite, Alembic all verified.",
  "artifacts": [
    {"file": "backend/requirements.txt", "action": "created"},
    {"file": "backend/app/main.py", "action": "created"},
    {"file": "frontend/package.json", "action": "created"},
    {"file": "alembic.ini", "action": "created"},
    {"file": ".gitignore", "action": "created"}
  ],
  "issues": [],
  "notes": "Camoufox binary ~100MB, downloaded to cache dir"
}
```

```bash
uv run python docs/phases/phase-1/checkpoints/notify.py \
    --cp cp0-environment \
    --role implementer \
    --status READY \
    --summary "Environment setup complete." \
    --result-file docs/phases/phase-1/checkpoints/cp0-environment/result.json

python3 docs/phases/phase-1/checkpoints/post-status.py \
    --result-file docs/phases/phase-1/checkpoints/cp0-environment/result.json
```
