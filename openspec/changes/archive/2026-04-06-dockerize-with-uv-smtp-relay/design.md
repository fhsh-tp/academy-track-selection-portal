## Context

目前專案直接在主機上以 `python -m uvicorn` 或 `gunicorn` 執行，依賴 `requirements.txt` 管理套件，郵件透過 Brevo REST API 發送，前端靜態檔案由 FastAPI 的 `StaticFiles` 直接 serve。此架構難以在新機器上重現，且混用第三方 SaaS（Brevo、Render）與本機元件，部署流程不透明。

本次變更引入 Docker Compose 作為標準部署單元，所有執行期依賴（PostgreSQL、nginx、cloudflared）均以容器管理，並切換至 Google Workspace SMTP Relay。

## Goals / Non-Goals

**Goals:**

- 建立可用 `docker compose up` 一鍵啟動的完整服務堆疊
- 前端由 nginx 獨立 serve，API 請求 proxy 至 backend
- 郵件服務自托管，不依賴第三方 API
- 所有機密與設定集中在 `.env`，提供完整的 `.env.example`
- 透過 Cloudflare Tunnel 對外暴露服務，不需在路由器開 port

**Non-Goals:**

- 不建立 Kubernetes / Helm 部署方案
- 不修改 API 介面、業務邏輯或資料庫 schema
- 不實作 HTTPS 終止（由 Cloudflare 邊緣節點處理）
- 不建立 CI/CD pipeline 或自動化測試流程
- 不支援水平擴展（multi-instance backend）

## Decisions

### 以 uv 取代 pip 管理 Python 依賴

使用 `pyproject.toml` + `uv.lock` 取代 `requirements.txt`。

**理由**：uv 提供確定性的 lock file、比 pip 快 10–100 倍、支援 Python 版本管理，且 Dockerfile 中 `uv sync --frozen --no-dev` 保證每次建置使用完全相同的依賴版本。

**替代方案**：Poetry（較重、Dockerfile 整合複雜）、pip-compile（仍基於 pip 生態）。

---

### Docker Compose 四個 service 的拓樸結構

```
cloudflared ──▶ nginx ──▶ backend ──▶ db
```

- `db`：`postgres:16-alpine`，資料持久化至 named volume `pgdata`
- `backend`：自建 image，以 Gunicorn 啟動 FastAPI
- `nginx`：自建 image（基於 `nginx:alpine`），serve 靜態檔案並 proxy `/login`（POST）、`/admin-login`（POST）、`/submit`、`/admin/*` 至 `backend:8000`
- `cloudflared`：`cloudflare/cloudflared:latest`，以 `TUNNEL_TOKEN` 連至 Cloudflare Zero Trust

`nginx` 僅在 Docker 內網對 `backend` 通訊，不對外暴露 port（production 模式）；本地開發可在 compose override 中另開 `ports`。

**理由**：nginx 比 FastAPI `StaticFiles` 在靜態檔案服務上效能更好，且職責分離使 backend 只需處理 API 邏輯。

---

### nginx 以 `entrypoint.sh` 注入前端設定

`frontend/config.js` 中的 hardcoded URL 改為占位符 `__API_BASE_URL__`。nginx container 的 `entrypoint.sh` 啟動時執行：

```sh
sed -i "s|__API_BASE_URL__|${API_BASE_URL:-}|g" /usr/share/nginx/html/config.js
exec nginx -g 'daemon off;'
```

**理由**：不引入前端建置工具（Vite/Webpack），維持現有純靜態架構；`envsubst` 需要 `gettext` 套件而 `sed` 已內建，較簡潔。

當 `API_BASE_URL` 為空字串（預設）時，前端使用相對路徑，nginx 同域 proxy 讓 CORS 問題自然消失。

---

### 郵件改用 aiosmtplib + smtp-relay.gmail.com

以 `aiosmtplib` 直接呼叫 Google Workspace SMTP Relay（`smtp-relay.gmail.com:587`，STARTTLS），取代 Brevo REST API。

**理由**：`aiosmtplib` 已在現有 `requirements.txt` 中（但未使用），切換後移除 `requests`（郵件用途）與 `resend` 兩個外部 HTTP API 依賴；SMTP Relay 允許每日 10,000 個收件者（vs Brevo 免費方案限制）；學校已有 Google Workspace，不需額外帳號。

**前置條件**：Google Admin Console 需先在 Routing → SMTP Relay Service 啟用 SMTP Auth，並允許來自應用程式的連線。

**替代方案**：繼續使用 Brevo（需維護 API key）；使用 `smtp.gmail.com`（每日 500 封限制，需 App Password 或 OAuth2）。

---

### DB sslmode 以環境變數控制

`database.py` 原本硬寫 `sslmode='require'`，改為讀取 `DB_SSLMODE` 環境變數（預設 `prefer`）。

**理由**：Docker 內部 PostgreSQL 不支援 SSL，硬寫 `require` 會導致連線失敗；生產環境（Render 或外部 managed DB）可設 `DB_SSLMODE=require`。

---

### Cloudflare Tunnel 以環境變數控制 protocol

`cloudflared` service 讀取 `TUNNEL_TRANSPORT_PROTOCOL`（預設 `auto`）。`auto` 模式優先使用 QUIC（UDP），UDP 不通時自動降回 HTTP/2（TCP 443）。

**理由**：不同網路環境對 UDP 的支援程度不一，`auto` 提供最大相容性而無需手動切換。

## Risks / Trade-offs

- **[Risk] SMTP Relay 需要 Google Admin Console 設定** → 在 `.env.example` 與文件中明確標注前置步驟；未設定前，郵件功能不可用但其他功能正常。

- **[Risk] nginx 靜態路由與 FastAPI 路由重複** → nginx 以 `try_files $uri $uri.html =404` 處理 HTML 路由（`/login` → `login.html`），POST 與 `/admin/*` API 路由統一 proxy 至 backend，避免衝突。

- **[Trade-off] 多一個 nginx image 增加建置複雜度** → 換來靜態檔案服務效能提升與 SPA-ready 的路由架構，長遠來說值得。

- **[Risk] `sed` 替換 config.js 在 container 啟動時修改檔案** → 若 nginx image 是唯讀 filesystem，`sed -i` 會失敗。解法：確保 nginx image 的 html 目錄可寫（`nginx:alpine` 預設可寫），或改用 `envsubst` 輸出至新檔案。

## Migration Plan

1. 在本地建立 `.env`（參考 `.env.example`），填入真實值
2. 在 Google Admin Console 啟用 SMTP Relay Service（允許 SMTP Auth）
3. 在 Cloudflare Zero Trust 建立 Tunnel，取得 `TUNNEL_TOKEN`，設定路由指向 `nginx:80`
4. 執行 `docker compose up --build -d`
5. 確認四個 service 均為 `healthy`
6. 測試登入、選填、郵件發送、管理員功能
7. 舊的主機部署服務停止（`Render` 服務可下線）

**回滾策略**：Docker Compose 部署失敗時，Render 上的舊版服務仍在線，DNS 指回原 Render URL 即可立即回滾。
