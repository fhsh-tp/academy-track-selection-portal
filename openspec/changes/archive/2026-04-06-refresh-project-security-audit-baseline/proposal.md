## Why

目前專案只有 `docs/security/2026-04-05_codex_audit/` 這份 first-pass security baseline，但 repository 內還沒有可持續追蹤的 `.security-audit/` lifecycle workspace，且部分舊 finding 的前提已和目前程式碼不同。若要對整個專案重新做一次完整、安全且可重複的 review，需要先把 scope、methodology、task checklist 與後續 findings/report 的落點正式化。

## What Changes

- 建立以 `owasp-security-audit` 為核心的專案級 audit lifecycle，讓 `.security-audit/` 內能追蹤本輪 full-project review 的 `scope`、`plan`、`tasks`、`findings` 與 `report`。
- 以目前 repository 狀態重新定義 audit boundaries，納入 FastAPI backend、static frontend、JWT/token handling、CSV import、email/PDF flow、Docker/Nginx/deployment config 與 dependency manifests。
- 刷新既有 security baseline 的要求，讓後續 `docs/security/` 發布的 audit 結果必須反映目前程式碼，而不是沿用 2026-04-05 的初始結論。
- 補上可驗證的 threat model、review categories、evidence sources 與 task breakdown，讓後續 `owasp:review` 與 `owasp:report` 能直接接續執行。

## Non-Goals (optional)

- 本 change 不直接修補具體漏洞，也不在 proposal 階段改動 authentication、authorization、CSP、CORS 或 deployment secrets。
- 本 change 不進行 dynamic penetration testing、雲端平台權限稽核或第三方 SaaS 帳號設定盤點。

## Capabilities

### New Capabilities

- `project-security-audit-lifecycle`: 定義 repository 內 OWASP audit workspace 的結構、必要 artifacts、review 類別與追蹤方式，支撐完整專案安全稽核流程。

### Modified Capabilities

- `initial-security-audit-baseline`: 既有 security baseline 的要求需更新為以目前程式碼與最新 audit evidence 為準，並能追溯到正式的 OWASP audit workspace 與 findings/report 輸出。

## Impact

- Affected specs: `project-security-audit-lifecycle`（new）、`initial-security-audit-baseline`（modified）
- Affected code: `.security-audit/active/project-wide-security-audit-2026-04-06/`, `docs/security/`, `backend/main.py`, `backend/security.py`, `backend/database.py`, `backend/mailer.py`, `backend/utils/email.py`, `frontend/login.html`, `frontend/admin-login.html`, `frontend/choose.html`, `frontend/admin.html`, `frontend/static/config.js`, `docker-compose.yml`, `Dockerfile`, `nginx/nginx.conf`, `pyproject.toml`
