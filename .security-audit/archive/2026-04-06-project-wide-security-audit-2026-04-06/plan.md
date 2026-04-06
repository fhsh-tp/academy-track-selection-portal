## Methodology

本輪採用 OWASP-oriented static code review，基於目前 branch `refactor/security-enhance` 與 commit `c72ebdda6aefc64a59a9a2234d1babc158bcc6c5` 的 repository state 逐類別檢查。方法上以 OWASP Code Review Guide v2 與 OWASP WSTG v4.2 的 category-oriented review 為主軸，先確認目前 attack surface 與 trust boundary，再回頭對照 `docs/security/2026-04-05_codex_audit/` 的 historical findings 是否仍成立、需降級，或應改寫為新的 evidence-backed finding。

本輪不做 runtime exploitation；所有結論都必須能對應到明確 source file、route、config 或資料流。只有當 current code 仍呈現相同風險，或發現新的可證明弱點時，才建立或更新 finding。

## Review Categories

### Authentication

- **Source**: OWASP Code Review Guide v2 Authentication review / OWASP WSTG v4.2 authentication testing guidance
- **Code Patterns**:
  - `backend/main.py` 的 `/login`、`/admin-login`：登入流程、錯誤回應一致性、是否缺少 brute-force protection
  - `backend/security.py`：bcrypt 驗證、JWT 建立、claim 內容與 secret 使用方式
  - `backend/database.py`、`.env.example`：admin bootstrap 與預設帳號密碼風險

### Authorization

- **Source**: OWASP Code Review Guide v2 Authorization review / OWASP WSTG v4.2 access control testing guidance
- **Code Patterns**:
  - `backend/main.py` 的 `/submit`、`/admin/all`、`/admin/import-students`、`/admin/send-reminders`：server-side role 與 identity enforcement
  - `frontend/choose.html`、`frontend/admin.html`：client-controlled `student_id`、`role`、bearer token 使用假設
  - `nginx/nginx.conf`：proxy 路徑與 admin functionality 對外暴露邊界

### Session Management

- **Source**: OWASP Code Review Guide v2 Session Management review / OWASP WSTG v4.2 session management testing guidance
- **Code Patterns**:
  - `frontend/login.html`、`frontend/admin-login.html`、`frontend/choose.html`、`frontend/admin.html`：JWT token 存放、登出流程、跨頁面 reuse
  - `backend/security.py`：token 過期時間、claim 驗證、缺少 revocation / rotation 的影響
  - `backend/main.py`：受保護 routes 對 bearer token 的依賴模式

### Input Validation

- **Source**: OWASP Code Review Guide v2 Input Validation review / OWASP WSTG v4.2 input handling guidance
- **Code Patterns**:
  - `backend/main.py` 的 `/submit`：`dict` payload、`choice` / `email` / `student_class_num` 驗證與錯誤處理
  - `backend/main.py` 的 `/admin/import-students`：CSV encoding、欄位標頭 normalization、row-level validation
  - `import_students.py`：批次匯入 script 的 file assumptions 與欄位處理

### Injection

- **Source**: OWASP Code Review Guide v2 Injection review / OWASP WSTG v4.2 injection testing guidance
- **Code Patterns**:
  - `backend/main.py`、`backend/database.py`、`import_students.py`：SQL query 是否保持參數化、是否存在 user-controlled query fragments
  - `nginx/entrypoint.sh`、`scripts/docker-entrypoint.sh`：shell interpolation 與 env var 注入是否可能擴大 command surface
  - `frontend/admin.html` 匯出 CSV / 上傳流程：輸出與輸入資料是否可能成為二次注入載體

### Cryptography

- **Source**: OWASP Code Review Guide v2 Cryptography review / OWASP WSTG v4.2 cryptography guidance
- **Code Patterns**:
  - `backend/security.py`：`HS256`、`SECRET_KEY`、token 生命週期與 claim 最小化
  - `backend/database.py`、`import_students.py`：password hashing 路徑是否一致且未退化
  - `.env.example`、`docker-compose.yml`：secrets 與 crypto-related env vars 的預設值與說明品質

### Error Handling

- **Source**: OWASP Code Review Guide v2 Error Handling review / OWASP WSTG v4.2 error handling guidance
- **Code Patterns**:
  - `backend/main.py`：`detail=str(e)`、匯入失敗回應、內部錯誤對 client 的暴露
  - `backend/security.py`：auth failure debug prints 與例外吞沒
  - `backend/mailer.py`、`backend/utils/email.py`：寄信與附件處理中的 broad exception handling

### Logging and Monitoring

- **Source**: OWASP Code Review Guide v2 Logging and Monitoring review / OWASP WSTG v4.2 logging guidance
- **Code Patterns**:
  - `backend/main.py`：登入、授權失敗、admin actions、提醒信觸發是否有足夠 audit trail
  - `backend/mailer.py`、`backend/utils/email.py`：是否記錄敏感內容、是否缺少重要 security events
  - `frontend/choose.html`：`console.log` 是否輸出可識別個資或操作痕跡

### Data Protection

- **Source**: OWASP Code Review Guide v2 Data Protection review / OWASP WSTG v4.2 data exposure guidance
- **Code Patterns**:
  - `frontend/login.html`、`frontend/admin-login.html`、`frontend/choose.html`、`frontend/admin.html`：token 與 PII 儲存在 `localStorage`、CSP 與 inline scripts 的組合風險
  - `docker-compose.yml`、`.env.example`、`frontend/static/config.js`：secret handling、default credentials、API base URL 與 network exposure
  - `backend/mailer.py`、`backend/utils/email.py`：email 內容、PDF 附件與 PII 傳輸範圍

### Dependency and Supply Chain

- **Source**: OWASP Code Review Guide v2 secure dependencies guidance / OWASP Top 10 A06:2021 Vulnerable and Outdated Components
- **Code Patterns**:
  - `pyproject.toml`、`uv.lock`：直接相依套件版本是否固定且可審核
  - `uv export` + `pip-audit`：目前 locked dependencies 是否存在已知公開弱點
  - `docker-compose.yml`、`Dockerfile`：runtime image 與 dependency bootstrap 是否引入危險預設值或無法重現的安裝來源
