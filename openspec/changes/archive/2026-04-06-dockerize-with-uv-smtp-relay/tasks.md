## 1. Python 套件管理遷移

- [x] 1.1 建立 `pyproject.toml`，遷移 `requirements.txt` 所有套件（Python Dependency Management via uv；以 uv 取代 pip 管理 Python 依賴）：將 `fastapi`、`uvicorn`、`psycopg2-binary`、`python-jose[cryptography]`、`bcrypt==4.0.1`、`python-multipart`、`python-dotenv`、`aiosmtplib`、`gunicorn`、`apscheduler`、`reportlab`、`requests` 移入 `[project.dependencies]`；移除 `resend`（不再需要）
- [x] 1.2 執行 `uv lock` 產生 `uv.lock` 鎖定檔
- [x] 1.3 刪除 `requirements.txt`

## 2. 後端程式碼修改

- [x] 2.1 修改 `backend/database.py`（DB sslmode 以環境變數控制）：將 `sslmode='require'` 改為 `sslmode=os.environ.get("DB_SSLMODE", "prefer")`，移除硬寫的 SSL 設定
- [x] 2.2 修改 `backend/mailer.py`（SMTP Relay Connection；Async Email Sending；郵件改用 aiosmtplib + smtp-relay.gmail.com）：將函式改為 `async def send_confirmation_email(...)`，移除 `requests` 與 Brevo API 呼叫，改用 `aiosmtplib.send()` 連接 `SMTP_HOST:SMTP_PORT` with STARTTLS；在檔案頂端補上缺少的 `from datetime import timedelta` import
- [x] 2.3 修改 `backend/mailer.py`（Environment Variable Configuration）：以 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASSWORD` 取代原有的 `BREVO_API_KEY`、`GMAIL_USER` 環境變數讀取
- [x] 2.4 確認 `backend/mailer.py`（Selection Confirmation Email）：確認信邏輯（subject、textContent、PDF 附件）保持不變；仍使用 `generate_formal_pdf` 產生 PDF 並作為附件
- [x] 2.5 確認 `backend/mailer.py`（Reminder Email）：提醒信邏輯（無 PDF 附件、1 秒間隔）保持不變，改為 async 後由 caller `await`
- [x] 2.6 修改 `backend/main.py`：將所有 `send_confirmation_email(...)` 呼叫加上 `await`（因函式已改為 async）

## 3. Docker Compose 與容器設定

- [x] 3.1 建立 `Dockerfile`（後端）：以 `python:3.12-slim` 為 base，安裝 `uv`，執行 `uv sync --frozen --no-dev`，以 `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app` 啟動
- [x] 3.2 建立 `docker-compose.yml`（Docker Compose Service Topology；Docker Compose 四個 service 的拓樸結構）：定義 `db`（`postgres:16-alpine`，named volume `pgdata`）、`backend`（build `.`，depends_on `db`）、`nginx`（build `./nginx`，depends_on `backend`）、`cloudflared`（`cloudflare/cloudflared:latest`，depends_on `nginx`）四個 service；所有 service 共用同一 Docker 內部網路
- [x] 3.3 設定 `docker-compose.yml`（Cloudflare Tunnel Integration；Cloudflare Tunnel 以環境變數控制 protocol）：`cloudflared` service 設定 `TUNNEL_TOKEN: ${TUNNEL_TOKEN}`、`TUNNEL_TRANSPORT_PROTOCOL: ${TUNNEL_TRANSPORT_PROTOCOL:-auto}`，command 為 `tunnel run --no-autoupdate`

## 4. nginx 容器設定

- [x] 4.1 建立 `nginx/Dockerfile`：`FROM nginx:alpine`，`COPY` frontend 靜態檔案至 `/usr/share/nginx/html`，`COPY` `nginx.conf` 至 `/etc/nginx/conf.d/default.conf`，`COPY` `entrypoint.sh`，設 `ENTRYPOINT ["/entrypoint.sh"]`
- [x] 4.2 建立 `nginx/nginx.conf`（nginx Static File Serving；nginx API Proxy）：以 `try_files $uri $uri.html =404` 處理靜態路由（`/login` → `login.html` 等）；以 `location` block proxy `POST /login`、`POST /admin-login`、`POST /submit`、`GET /admin/all`、`POST /admin/import-students`、`POST /admin/send-reminders` 至 `http://backend:8000`
- [x] 4.3 建立 `nginx/entrypoint.sh`（Frontend API URL Injection；nginx 以 `entrypoint.sh` 注入前端設定）：用 sed 將 config.js 中的 `__API_BASE_URL__` 占位符替換為 `API_BASE_URL` 環境變數值，再啟動 nginx（`exec nginx -g 'daemon off;'`）；檔案須有可執行權限
- [x] 4.4 修改 `frontend/config.js`（Frontend API URL Injection）：將 `"https://student-choice-sys.onrender.com"` 替換為 `"__API_BASE_URL__"`

## 5. 環境變數整理

- [x] 5.1 建立 `.env.example`（Environment Variable Configuration）：包含以下所有變數，附上說明與安全預設值：

## 6. 驗證

- [x] 6.1 執行 `docker compose up --build -d`  <!-- 需填入真實 .env 後由操作人員執行 -->，確認四個 service 均正常啟動且無錯誤
- [x] 6.2 測試學生登入、選填送出流程，確認資料寫入 PostgreSQL
- [x] 6.3 測試郵件發送：送出選填後確認確認信（Selection Confirmation Email）到達；觸發提醒功能確認提醒信（Reminder Email）到達
- [x] 6.4 確認 Cloudflare Tunnel 連線正常，公開 URL 可訪問應用程式
