## Why

專案目前使用裸 `requirements.txt` 管理套件、直接在主機上執行，且郵件服務依賴 Brevo 第三方 REST API，難以在不同環境中重現與部署。本次變更目標是建立可重現、容器化的部署方式，並將郵件服務切換至學校 Google Workspace 的 SMTP Relay。

## What Changes

- **套件管理**：以 `pyproject.toml` + `uv.lock` 取代 `requirements.txt`，使用 `uv` 管理 Python 依賴
- **容器化部署**：建立 `docker-compose.yml`，包含四個 service：
  - `db`：PostgreSQL 16（取代外部 Render 資料庫）
  - `backend`：FastAPI + Gunicorn（使用 uv 建置）
  - `nginx`：serve 前端靜態檔案並 proxy API 請求至 backend
  - `cloudflared`：Cloudflare Tunnel，對外暴露服務
- **郵件服務**：以 `aiosmtplib` 透過 `smtp-relay.gmail.com:587`（STARTTLS）取代 Brevo REST API 呼叫
- **環境變數整理**：移除 `BREVO_API_KEY`、`GMAIL_USER`；新增 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASSWORD`；新增 `TUNNEL_TOKEN`、`TUNNEL_TRANSPORT_PROTOCOL`；以 `DB_SSLMODE` 取代硬寫的 `sslmode='require'`
- **建立 `.env.example`**：記錄所有必要環境變數，Docker Compose 提供安全的預設值
- **`frontend/config.js`**：將硬寫的 Render URL 改為占位符 `__API_BASE_URL__`，由 nginx `entrypoint.sh` 啟動時透過 `sed` 替換

## Non-Goals

- 不導入 HTTPS/TLS termination（由 Cloudflare Tunnel 處理）
- 不修改任何業務邏輯、API 介面或資料庫 schema
- 不更換前端技術棧（仍維持純靜態 HTML/CSS/JS）
- 不建立 CI/CD pipeline

## Capabilities

### New Capabilities

- `container-deployment`：Docker Compose 容器化部署，包含 nginx（靜態檔案 + proxy）、backend、PostgreSQL、Cloudflare Tunnel 四個 service，以及 uv 套件管理與 `.env.example` 環境變數規範
- `smtp-mail-delivery`：使用 Google Workspace SMTP Relay（`smtp-relay.gmail.com`）透過 `aiosmtplib` 非同步發送確認信與提醒信，取代原有 Brevo REST API 整合

### Modified Capabilities

（無）

## Impact

- **新增檔案**：`Dockerfile`、`docker-compose.yml`、`nginx/nginx.conf`、`nginx/entrypoint.sh`、`nginx/Dockerfile`、`.env.example`、`pyproject.toml`
- **修改檔案**：`backend/mailer.py`（Brevo → aiosmtplib）、`backend/database.py`（`sslmode` 改為環境變數）、`frontend/config.js`（URL 改為占位符）
- **移除檔案**：`requirements.txt`
- **依賴異動**：移除 `resend`、`requests`（郵件用途）；啟用已存在於依賴清單的 `aiosmtplib`
