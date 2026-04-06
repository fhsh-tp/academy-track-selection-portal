## Audit Target

- **Project**: `academy-track-selection-portal`
- **Repository**: `/Users/phoenix/dev/fhsh-projects/academy-track-selection-portal`
- **Version/Commit**: branch `refactor/security-enhance`, commit `c72ebdda6aefc64a59a9a2234d1babc158bcc6c5`

## Boundaries

### Included

- `backend/main.py`：FastAPI route handlers、CORS 設定、認證/授權 gate、CSV upload 與提醒信流程
- `backend/security.py`：bcrypt password hashing、JWT token 建立與 bearer token 解析
- `backend/database.py`：資料庫 schema 初始化、admin bootstrap、connection pool
- `backend/mailer.py`：PDF 產生、寄信內容組裝、SMTP 呼叫入口
- `backend/utils/email.py`：SMTP message 建構、附件處理、錯誤回傳
- `frontend/login.html`：學生登入、token 與使用者資料儲存
- `frontend/admin-login.html`：管理員登入與 token 儲存
- `frontend/choose.html`：學生選填提交 payload 與 bearer token 使用
- `frontend/admin.html`：管理後台資料讀取、CSV upload、提醒信與 change-password UI
- `frontend/index.html`：公開入口頁與 browser 端 CSP 基線
- `frontend/static/config.js`：API base URL 注入點
- `nginx/nginx.conf`：clean URL、靜態頁與 API proxy 邊界
- `nginx/entrypoint.sh`：前端 runtime config 注入流程
- `Dockerfile`：backend container build 與 runtime 啟動方式
- `docker-compose.yml`：network、service exposure、env var 與 secrets wiring
- `scripts/docker-entrypoint.sh`：development / production 啟動流程
- `import_students.py`：獨立批次匯入 script 與資料庫寫入行為
- `pyproject.toml`、`uv.lock`：依賴宣告與鎖定版本
- `.env.example`：部署所需 secrets、預設值與安全性說明
- `docs/security/2026-04-05_codex_audit/`：作為舊 baseline 與 finding 狀態比對的 historical input

### Excluded

- `.env`：本機或部署環境的真實 secrets，不屬於可分享的 repository baseline
- `.venv/`：第三方安裝套件，改由 `pyproject.toml` 與 `uv.lock` 代表依賴面
- `frontend/static/style.css`：樣式層資產，除非直接影響安全控制，否則不作為本輪 source review 主體
- `frontend/TW-Kai-98_1.ttf`、`frontend/TW-Kai-Ext-B-98_1.ttf`、`backend/static/TW-Kai-98_1.ttf`、`backend/static/TW-Kai-Ext-B-98_1.ttf`：二進位字型檔，不屬於程式邏輯檢查範圍
- `openspec/`、`.spectra/`、`.claude/`、`.agents/`：規格與工作流 metadata，不是 production attack surface；僅在需要追溯決策時參考
- 雲端平台控制台設定（例如 Cloudflare、SMTP provider、主機層 firewall）：repository 外部資產，本輪無直接存取權

## Technology Stack

- Backend：Python 3.12+、FastAPI、Pydantic
- Frontend：靜態 HTML、原生 JavaScript、CSS，由 Nginx 提供
- Data layer：PostgreSQL、`psycopg2`
- Authentication：JWT（`python-jose`）、OAuth2 bearer flow、`bcrypt`
- Email / documents：`aiosmtplib`、ReportLab PDF 產生
- Deployment：Docker、Docker Compose、Nginx、`uv` 鎖定依賴
- Operations input：`.env.example`、Cloudflare Tunnel token、SMTP credentials

## Threat Model

- **Threat Actors**:
  - 未授權的外部使用者，能直接命中公開 Nginx / backend endpoint
  - 一般學生使用者，持有自己的 token 與可控制的 browser storage
  - 管理員使用者，可觸發 CSV import、資料匯出與提醒信流程
  - 維護者或操作人員，可能因 env var、proxy 或 deployment 預設值而引入 misconfiguration
- **Attack Surfaces**:
  - `/login`、`/admin-login`、`/submit`
  - `/admin/all`、`/admin/import-students`、`/admin/send-reminders`
  - browser `localStorage`、inline scripts 與 CSP
  - CSV upload / batch import flow
  - Nginx proxy routing、Docker Compose service exposure、runtime env var injection
  - SMTP email 與 PDF 附件流程
- **Trust Boundaries**:
  - Browser / static frontend 與 Nginx 之間
  - Nginx reverse proxy 與 FastAPI backend 之間
  - FastAPI backend 與 PostgreSQL 之間
  - FastAPI backend 與 SMTP relay / email recipients 之間
  - Repository-tracked config (`.env.example`, Docker files) 與實際 deployment secrets 之間

## Applicable Standards

- OWASP Code Review Guide v2：Authentication、Authorization、Session Management、Input Validation、Injection、Cryptography、Error Handling、Logging and Monitoring、Data Protection
- OWASP WSTG v4.2：Web authentication / access control / session / input handling / configuration review practices
- OWASP Top 10 2021 mapping：A01 Broken Access Control、A02 Cryptographic Failures、A03 Injection、A05 Security Misconfiguration、A07 Identification and Authentication Failures、A09 Security Logging and Monitoring Failures

## Constraints

- 本輪為 static source code review，不包含 live environment exploitation 或 dynamic penetration testing
- 本輪無法直接驗證 Cloudflare、SMTP provider、host OS 或 container runtime 的實際控制台設定
- 本輪不檢查 `.env` 真值與 production secrets 輪替狀態，只檢查 repository 內的 secret-handling patterns
- 2026-04-05 的既有 audit 文件只作為 comparison baseline，不能直接視為目前程式碼的最終結論
