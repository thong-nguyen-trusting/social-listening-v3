# Production Deployment

## Goal

Production chi duoc chay tu code da nam tren GitHub.
Server production khong tu build tu working tree local nua.
GitHub se build Docker image len GHCR.
Production server chi pull image theo commit SHA roi restart bang `docker compose`.

## Source of truth

- Production branch: `main`
- Image registry: `ghcr.io/blackbirdzzzz365-gif/social-listening-v3`
- Production server: `e1.chiasegpu.vn`
- App dir tren server: `/home/ubuntu/social-listening-v3`

## Workflows

### 1. CI

File: `.github/workflows/ci.yml`

Runs on:

- pull requests
- pushes to `main`

Checks:

- Python compile for backend
- frontend build
- Docker image build smoke

### 2. Build production image

File: `.github/workflows/build-image.yml`

Runs on:

- push to `main`
- manual dispatch

Output:

- `ghcr.io/blackbirdzzzz365-gif/social-listening-v3:sha-<full_sha>`
- `ghcr.io/blackbirdzzzz365-gif/social-listening-v3:sha-<short_sha>`
- `ghcr.io/blackbirdzzzz365-gif/social-listening-v3:main`

### 3. Deploy production

File: `.github/workflows/deploy-production.yml`

Runs on:

- manual dispatch only

Behavior:

1. Resolve exact commit SHA from `main`
2. SSH vao production server
3. `git checkout --detach <sha>`
4. `docker compose -f docker-compose.production.yml pull`
5. `docker compose -f docker-compose.production.yml up -d --remove-orphans`
6. Health-check `/health`
7. Luu state vao `.deploy/production-state.env`

### 4. Roll back production

File: `.github/workflows/rollback-production.yml`

Runs on:

- manual dispatch only

Behavior:

- rollback ve `PREVIOUS_SHA` da luu
- hoac rollback ve SHA cu the neu truyen vao input

## Server-side files

- `docker-compose.production.yml`
- `scripts/deploy_production.sh`
- `scripts/healthcheck_production.sh`
- `scripts/rollback_production.sh`

State production duoc luu tai:

- `.deploy/deploy.env`
- `.deploy/production-state.env`

## Operator shortcuts

Neu dang login GitHub bang `gh`, co the trigger:

```bash
scripts/trigger_production_deploy.sh
scripts/trigger_production_rollback.sh
scripts/trigger_production_rollback.sh <sha>
```

## Contributor workflow

### Code tu bat cu may nao / account nao

1. Bat dau tu `main`
2. Tao branch moi
3. Code va push len GitHub
4. Tao PR vao `main`
5. Cho CI pass
6. Merge vao `main`

Neu account khong co quyen push truc tiep, dung fork + pull request.

### Deploy production

1. Bao OpenClaw/Codex trigger deploy production tu `main`
2. OpenClaw/Codex se goi workflow `deploy-production.yml`
3. Workflow lay image tu commit SHA moi nhat tren `main`
4. Production server chi pull image do va restart app

## Why this is safer

- Production khong build tu working tree local tren server
- Moi lan deploy deu gan voi 1 SHA ro rang
- Rollback don gian vi co `PREVIOUS_SHA`
- Trigger co the den tu Linux VM, host, hay bat cu device nao co `gh` auth, nhung source van la GitHub
