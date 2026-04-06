## Authentication

- [x] Review `backend/main.py` `/login` 與 `/admin-login` 的認證流程，確認是否缺少 brute-force protection、帳號枚舉差異或不一致的錯誤訊息。 → FINDING-004
- [x] Review `backend/security.py`、`backend/database.py` 與 `.env.example`，確認 JWT secret bootstrap、bcrypt 使用方式與預設 admin credentials 風險。 → FINDING-001

## Authorization

- [x] Review `backend/main.py` `/submit`、`/admin/all`、`/admin/import-students`、`/admin/send-reminders` 的 server-side role 與 identity checks，確認是否仍存在 horizontal 或 vertical privilege escalation。
- [x] Review `frontend/choose.html`、`frontend/admin.html` 與 `nginx/nginx.conf`，確認前端或 proxy 是否放大了 client-side authorization assumptions。

## Session Management

- [x] Review `frontend/login.html`、`frontend/admin-login.html`、`frontend/choose.html`、`frontend/admin.html` 的 token storage、登出流程與跨頁 reuse，確認是否存在 session fixation-like 或 token persistence 風險。 → FINDING-002
- [x] Review `backend/security.py` 與 `backend/main.py` 的 token expiry、claim validation 與受保護 route 使用模式，確認是否缺少 revocation、rotation 或敏感操作再驗證。

## Input Validation

- [x] Review `backend/main.py` `/submit` 的 request payload handling，確認 `choice`、`email`、`student_class_num` 與 `submit_time` 是否有足夠 server-side validation。
- [x] Review `backend/main.py` `/admin/import-students` 與 `import_students.py`，確認 CSV encoding、欄位標頭、空值與異常列處理是否能阻擋惡意或畸形輸入。 → FINDING-003

## Injection

- [x] Review `backend/main.py`、`backend/database.py` 與 `import_students.py` 的 SQL 呼叫，確認是否所有 user-controlled data 都經過參數化而非動態 query 拼接。
- [x] Review `nginx/entrypoint.sh`、`scripts/docker-entrypoint.sh` 與 `frontend/admin.html` 的 shell / CSV data flow，確認是否存在 command injection、template injection 或 spreadsheet formula injection 風險。

## Cryptography

- [x] Review `backend/security.py` 的 `HS256` token 建立、`SECRET_KEY` 依賴與 claim 內容，確認是否符合目前應用所需的最小安全基線。
- [x] Review `backend/database.py`、`import_students.py`、`.env.example` 與 `docker-compose.yml`，確認 password hashing 與 crypto-related defaults 沒有退化成弱設定或易誤用配置。 → FINDING-001

## Error Handling

- [x] Review `backend/main.py` 的匯入、提醒信與一般 API error paths，確認是否把內部 exception detail 直接暴露給 client。 → FINDING-003
- [x] Review `backend/security.py`、`backend/mailer.py` 與 `backend/utils/email.py` 的 broad exception handling，確認是否吞沒安全相關失敗或留下不一致狀態。

## Logging and Monitoring

- [x] Review `backend/main.py` 的登入、授權失敗、admin actions 與提醒信流程，確認是否缺少可稽核的 security event logs。
- [x] Review `backend/mailer.py`、`backend/utils/email.py` 與 `frontend/choose.html`，確認 logs 或 console output 是否洩漏 token、PII 或過度詳細的操作內容。

## Data Protection

- [x] Review `frontend/login.html`、`frontend/admin-login.html`、`frontend/choose.html` 與 `frontend/admin.html`，確認 `localStorage`、inline scripts 與 CSP 的組合是否暴露 token 或個資。 → FINDING-002
- [x] Review `docker-compose.yml`、`frontend/static/config.js`、`.env.example`、`backend/mailer.py` 與 `backend/utils/email.py`，確認 secrets、PII、email attachments 與 network exposure 的保護邊界是否足夠。 → FINDING-001

## Dependency and Supply Chain

- [x] Review `pyproject.toml`、`uv.lock` 與 `Dockerfile`，確認 dependency pinning、build 來源與可重現性沒有額外引入 supply-chain 風險。
- [x] Run a locked dependency vulnerability scan against the current Python dependency set, record the command and result, and decide whether any vulnerability finding is required. → No known vulnerabilities found
