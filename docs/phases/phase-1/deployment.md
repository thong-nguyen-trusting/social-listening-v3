# Deployment Guide — Phase 1: Docker + noVNC

## AI Facebook Social Listening & Engagement v3

**Phase:** 1 — Safe Core Loop
**Method:** Docker Compose (single container + noVNC for browser access)
**Updated:** 2026-03-28

---

## 1. Tong quan

```
User's Machine
┌──────────────────────────────────────────────────┐
│  Docker Container                                │
│  ┌────────────────────────────────────────────┐  │
│  │  Xvfb :99 (virtual display 1280x720)      │  │
│  │       │                                     │  │
│  │  ┌────▼─────┐    ┌──────────────────────┐  │  │
│  │  │ Camoufox │    │ x11vnc → websockify  │  │  │
│  │  │ (Firefox │    │     → noVNC          │──┼──┼── :6080 (Browser viewer)
│  │  │ patched) │    └──────────────────────┘  │  │
│  │  └────┬─────┘                               │  │
│  │       │                                     │  │
│  │  ┌────▼─────────────────────────────────┐  │  │
│  │  │  FastAPI Application                  │  │  │
│  │  │  ├── API routes (:8000/api/*)        │──┼──┼── :8000 (App UI + API)
│  │  │  ├── Static React files (:8000/*)    │  │  │
│  │  │  └── SQLite DB (/app/data/app.db)    │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  Volumes:                                         │
│  ├── browser_profile → FB session cookies         │
│  └── sqlite_data     → DB persist                 │
└──────────────────────────────────────────────────┘
```

**User trai nghiem:**

1. `docker compose up` — khoi dong app
2. Mo `http://localhost:8000` — giao dien app
3. Mo `http://localhost:6080/vnc.html` — thay browser Camoufox → dang nhap Facebook
4. Quay lai `localhost:8000` — dung app binh thuong

---

## 2. Yeu cau he thong

| Yeu cau | Minimum | Khuyen nghi |
|---------|---------|-------------|
| Docker Engine | 24.0+ | Latest stable |
| Docker Compose | v2.20+ | Latest stable |
| RAM | 2 GB free | 4 GB free |
| Disk | 2 GB free | 5 GB free (Camoufox binary ~100MB, image ~800MB) |
| Network | Internet access | Cho Claude API + Facebook |
| OS | Linux, macOS, Windows (WSL2) | macOS / Linux |

---

## 3. Cau truc file

```
social-listening-v3/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── entrypoint.sh
├── nginx.conf              # (optional) reverse proxy
├── backend/
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
└── frontend/
    ├── src/
    └── package.json
```

---

## 4. File chi tiet

### 4.1 — .env.example

```bash
# === BAT BUOC ===
ANTHROPIC_API_KEY=sk-ant-api03-...

# Secret key cho HMAC hash (tao bang: python3 -c "import secrets; print(secrets.token_hex(32))")
OPAQUE_ID_SECRET=your-random-secret-here

# === TUY CHON ===
# noVNC password (de trong = khong password)
VNC_PASSWORD=

# Port mapping
APP_PORT=8000
VNC_PORT=6080

# Camoufox
CAMOUFOX_HEADLESS=false

# ntfy notification (optional)
NTFY_TOPIC=
```

### 4.2 — Dockerfile

```dockerfile
# ============================================================
# Stage 1: Build frontend
# ============================================================
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit
COPY frontend/ ./
RUN npm run build
# Output: /build/dist/

# ============================================================
# Stage 2: Runtime
# ============================================================
FROM python:3.12-slim

LABEL maintainer="social-listening-v3"
LABEL description="AI Facebook Social Listening — Phase 1"

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Virtual display
    xvfb \
    # VNC server
    x11vnc \
    # noVNC web client
    novnc \
    websockify \
    # Camoufox/Firefox dependencies
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    # Utilities
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Fetch Camoufox patched Firefox binary
RUN python -m camoufox fetch

# ---- Application code ----
COPY backend/ ./

# ---- Frontend static files ----
COPY --from=frontend-builder /build/dist/ /app/static/

# ---- Alembic config ----
COPY alembic.ini ./

# ---- Entrypoint ----
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ---- Data directories ----
RUN mkdir -p /data /root/.social-listening/browser_profile

# ---- Environment defaults ----
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///data/app.db

EXPOSE 8000 6080

ENTRYPOINT ["/entrypoint.sh"]
```

### 4.3 — entrypoint.sh

```bash
#!/bin/bash
set -e

echo "========================================"
echo " Social Listening v3 — Starting..."
echo "========================================"

# ---- 1. Virtual display ----
echo "[1/5] Starting virtual display (Xvfb)..."
Xvfb :99 -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 1

# Verify Xvfb is running
if ! kill -0 $XVFB_PID 2>/dev/null; then
    echo "ERROR: Xvfb failed to start"
    exit 1
fi
echo "  Xvfb running on :99"

# ---- 2. VNC server ----
echo "[2/5] Starting VNC server..."
VNC_ARGS="-display :99 -forever -shared -rfbport 5900"
if [ -n "$VNC_PASSWORD" ]; then
    mkdir -p /root/.vnc
    x11vnc -storepasswd "$VNC_PASSWORD" /root/.vnc/passwd
    VNC_ARGS="$VNC_ARGS -rfbauth /root/.vnc/passwd"
else
    VNC_ARGS="$VNC_ARGS -nopw"
fi
x11vnc $VNC_ARGS &
sleep 1
echo "  VNC server running on :5900"

# ---- 3. noVNC web client ----
echo "[3/5] Starting noVNC web client..."
NOVNC_PATH=$(find / -name "vnc.html" -path "*/novnc/*" 2>/dev/null | head -1 | xargs dirname)
if [ -z "$NOVNC_PATH" ]; then
    NOVNC_PATH="/usr/share/novnc"
fi
websockify --web "$NOVNC_PATH" 6080 localhost:5900 &
sleep 1
echo "  noVNC available at http://localhost:6080/vnc.html"

# ---- 4. Database migration ----
echo "[4/5] Running database migrations..."
cd /app
alembic upgrade head
echo "  Database ready"

# ---- 5. FastAPI application ----
echo "[5/5] Starting application server..."
echo ""
echo "========================================"
echo " READY!"
echo ""
echo " App UI:     http://localhost:8000"
echo " Browser:    http://localhost:6080/vnc.html"
echo "========================================"
echo ""

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info
```

### 4.4 — docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: social-listening-v3
    ports:
      - "${APP_PORT:-8000}:8000"    # App UI + API
      - "${VNC_PORT:-6080}:6080"    # noVNC browser viewer
    volumes:
      # FB session cookies — persist qua container restart
      - browser_profile:/root/.social-listening/browser_profile
      # SQLite database — persist qua container restart
      - sqlite_data:/data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPAQUE_ID_SECRET=${OPAQUE_ID_SECRET}
      - VNC_PASSWORD=${VNC_PASSWORD:-}
      - DISPLAY=:99
    env_file:
      - .env
    restart: unless-stopped
    # Health check — verify ca app lan Xvfb
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s

volumes:
  browser_profile:
    name: slv3-browser-profile
  sqlite_data:
    name: slv3-sqlite-data
```

---

## 5. Huong dan trien khai

### 5.1 — Lan dau tien

```bash
# 1. Clone project
git clone <repo-url> social-listening-v3
cd social-listening-v3

# 2. Tao .env tu example
cp .env.example .env

# 3. Dien ANTHROPIC_API_KEY
#    Lay tai: https://console.anthropic.com/settings/keys
nano .env

# 4. Tao OPAQUE_ID_SECRET (chay 1 lan)
python3 -c "import secrets; print(f'OPAQUE_ID_SECRET={secrets.token_hex(32)}')" >> .env

# 5. Build va start
docker compose up --build -d

# 6. Xem logs
docker compose logs -f app
# Doi den khi thay:
#   READY!
#   App UI:     http://localhost:8000
#   Browser:    http://localhost:6080/vnc.html

# 7. Dang nhap Facebook
# Mo http://localhost:6080/vnc.html trong browser
# Thay cua so Camoufox → dang nhap Facebook binh thuong
# QUAN TRONG: Tool KHONG doc mat khau — chi reuse cookies tu browser profile

# 8. Dung app
# Mo http://localhost:8000
# Session status se hien "Da ket noi"
```

### 5.2 — Cac lan sau

```bash
# Start (session FB van con tu lan truoc)
docker compose up -d

# Stop (giu data)
docker compose down

# Xem logs
docker compose logs -f app

# Restart
docker compose restart app
```

### 5.3 — Cap nhat phien ban moi

```bash
git pull origin main
docker compose up --build -d
# Alembic migration chay tu dong trong entrypoint
```

### 5.4 — Xoa sach de lam lai

```bash
# Xoa container + volumes (MAT SESSION FB + DB)
docker compose down -v

# Build lai tu dau
docker compose up --build -d
```

---

## 6. Xu ly su co

### 6.1 — noVNC khong hien thi

```bash
# Kiem tra Xvfb
docker exec social-listening-v3 ps aux | grep Xvfb

# Kiem tra x11vnc
docker exec social-listening-v3 ps aux | grep x11vnc

# Restart container
docker compose restart app
```

### 6.2 — Camoufox khong mo duoc trong container

```bash
# Kiem tra dependencies
docker exec social-listening-v3 ldd $(python -c "import camoufox; print(camoufox.__path__[0])")/firefox/firefox | grep "not found"

# Neu co "not found" → thieu system library
# Them vao Dockerfile apt-get install
```

### 6.3 — Facebook session het han

```bash
# Mo lai noVNC
# http://localhost:6080/vnc.html
# Dang nhap lai trong cua so browser
# App tu dong detect → chuyen session_status = VALID
```

### 6.4 — Database bi loi

```bash
# Backup truoc
docker cp social-listening-v3:/data/app.db ./backup-app.db

# Reset DB (mat data, giu session)
docker exec social-listening-v3 bash -c "cd /app && alembic downgrade base && alembic upgrade head"

# Reset hoan toan
docker compose down -v
docker compose up -d
```

### 6.5 — Container khong start

```bash
# Xem loi
docker compose logs app | tail -50

# Chay manual de debug
docker compose run --rm app bash
# Trong container:
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
python -c "from camoufox.async_api import AsyncCamoufox; print('OK')"
```

---

## 7. Bao mat

### 7.1 — Nhung gi KHONG duoc lam

| Hanh dong | Ly do |
|-----------|-------|
| Push .env len git | Chua API key va secret |
| Expose port 6080 ra internet | noVNC hien thi browser Facebook cua ban |
| Share Docker volume `browser_profile` | Chua session cookies Facebook |
| Chay container voi `--network=host` tren server cong cong | Lo cac port noi bo |

### 7.2 — .dockerignore

```
.env
.env.local
*.db
backend/venv/
frontend/node_modules/
frontend/dist/
__pycache__/
.git/
docs/
*.md
.architecture/
```

### 7.3 — Neu can deploy tren server (khong khuyen nghi Phase 1)

Neu bat buoc phai chay tren server tu xa:

```bash
# 1. Dung SSH tunnel thay vi expose port
ssh -L 8000:localhost:8000 -L 6080:localhost:6080 user@server

# 2. Hoac dung VNC password
echo "VNC_PASSWORD=your-strong-password" >> .env

# 3. KHONG BAO GIO expose 6080 ra public internet
```

---

## 8. Performance tuning

### 8.1 — Giam image size

```dockerfile
# Dung trong Dockerfile neu can giam size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    pip cache purge
```

| Component | Size |
|-----------|------|
| python:3.12-slim base | ~150 MB |
| System deps (Xvfb, VNC, libs) | ~200 MB |
| Python packages | ~150 MB |
| Camoufox binary (Firefox patched) | ~100 MB |
| Frontend build | ~5 MB |
| **Total image** | **~600-800 MB** |

### 8.2 — Resource limits

```yaml
# Trong docker-compose.yml, them vao service app:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

### 8.3 — SQLite WAL mode (concurrent read)

```python
# Them vao backend/app/main.py on startup:
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
```

---

## 9. Checklist truoc khi demo

```
[ ] .env da co ANTHROPIC_API_KEY
[ ] .env da co OPAQUE_ID_SECRET
[ ] docker compose up --build thanh cong
[ ] http://localhost:8000/health tra ve {"status":"ok"}
[ ] http://localhost:6080/vnc.html hien thi desktop
[ ] Dang nhap Facebook thanh cong trong noVNC
[ ] App hien thi "Da ket noi" (session_status = VALID)
[ ] Chay 1 flow: topic → keywords → plan → approve → run → themes
[ ] Account van HEALTHY sau khi chay
[ ] docker compose down roi up lai → session van con (khong can login lai)
```

---

## 10. So sanh voi chay truc tiep (khong Docker)

| Tieu chi | Docker + noVNC | Chay truc tiep |
|----------|---------------|----------------|
| Setup | `docker compose up` | Python + Node + Camoufox thu cong |
| Reproducible | Co (Dockerfile) | Phu thuoc moi truong may |
| FB login | Qua noVNC (web browser) | Qua Camoufox window truc tiep |
| UX login | Cham hon 1 chut (qua VNC) | Nhanh hon (native window) |
| Isolation | Hoan toan | Khong |
| Deploy cho nguoi khac | Copy + docker compose up | Huong dan cai tung thu |
| Debug | docker exec + logs | Truc tiep tren may |
| Khuyen nghi | **Demo, share cho team** | **Dev hang ngay** |
