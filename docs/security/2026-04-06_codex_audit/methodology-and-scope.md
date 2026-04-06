# Methodology 與 Scope

## Audit Target

- Project: `academy-track-selection-portal`
- Repository path: `/Users/phoenix/dev/fhsh-projects/academy-track-selection-portal`
- Branch / Commit: `refactor/security-enhance` / `c72ebdda6aefc64a59a9a2234d1babc158bcc6c5`
- Audit workspace: [`project-wide-security-audit-2026-04-06`](../../../.security-audit/active/project-wide-security-audit-2026-04-06/)
- Review type: static source code review + locked dependency scan
- Review date: `2026-04-06`

## Review Goal

建立目前程式碼狀態的 security baseline，並把 active audit 與 published summary 明確分離：`.security-audit/` 追蹤進行中與可歸檔的 working artifacts，`docs/security/2026-04-06_codex_audit/` 則提供穩定閱讀入口。

## Included Boundaries

- `backend/main.py`
- `backend/security.py`
- `backend/database.py`
- `backend/mailer.py`
- `backend/utils/email.py`
- `frontend/login.html`
- `frontend/admin-login.html`
- `frontend/choose.html`
- `frontend/admin.html`
- `frontend/index.html`
- `frontend/static/config.js`
- `nginx/nginx.conf`
- `nginx/entrypoint.sh`
- `Dockerfile`
- `docker-compose.yml`
- `scripts/docker-entrypoint.sh`
- `import_students.py`
- `pyproject.toml`
- `uv.lock`
- `.env.example`

## Excluded Boundaries

- `.env` 真實 secrets
- 雲端平台 / SMTP provider / Cloudflare console 設定
- dynamic penetration testing
- 二進位字型檔與非安全主題的樣式資產

## Threat Model

### Threat Actors

- 未授權外部使用者
- 一般學生使用者
- 管理員使用者
- 維護者 / 部署操作者

### Primary Attack Surfaces

- `/login`
- `/admin-login`
- `/submit`
- `/admin/all`
- `/admin/import-students`
- `/admin/send-reminders`
- browser `localStorage`
- deployment defaults in `docker-compose.yml`

### Key Trust Boundaries

- Browser 與 frontend script runtime
- Nginx reverse proxy 與 FastAPI backend
- FastAPI backend 與 PostgreSQL
- FastAPI backend 與 SMTP relay
- repository-tracked config 與真實 deployment secrets

## Methodology

本輪使用 OWASP Code Review Guide v2 與 OWASP WSTG v4.2 作為主要方法論，按類別檢查：

- Authentication
- Authorization
- Session Management
- Input Validation
- Injection
- Cryptography
- Error Handling
- Logging and Monitoring
- Data Protection
- Dependency and Supply Chain

額外補充一輪 locked dependency scan，命令與結果整理在 [dependency-vulnerability-scan.md](./dependency-vulnerability-scan.md)。

## Legacy Findings Re-verification

| 2026-04-05 Finding | Current Status | Notes |
| --- | --- | --- |
| `FINDING-001` `/submit` integrity gap | Closed | `/submit` 現在要求驗證並比對 token 與 `student_id` |
| `FINDING-002` unauthenticated import | Closed | `/admin/import-students` 現在要求驗證與 admin role |
| `FINDING-003` client-side token exposure | Retained / rewritten | 在本輪改寫為新的 `FINDING-002` |
| `FINDING-004` wildcard CORS | Closed | origins 現在改為 allow-list，而非 `*` |

## Supporting Artifacts

- [scope.md](../../../.security-audit/active/project-wide-security-audit-2026-04-06/scope.md)
- [plan.md](../../../.security-audit/active/project-wide-security-audit-2026-04-06/plan.md)
- [tasks.md](../../../.security-audit/active/project-wide-security-audit-2026-04-06/tasks.md)
