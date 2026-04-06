# Methodology 與 Scope

## Audit Target

- Project: `academy-track-selection-portal`
- Repository path: `/Users/phoenix/dev/edu-projects/academy-track-selection-portal`
- Review type: static code review
- Review date: `2026-04-05`

## Review Goal

建立此專案第一次正式 security baseline，辨識目前最重要的攻擊面、trust boundaries 與可追蹤 findings，讓後續討論與 remediation 不再依賴口頭記憶。

## Included Boundaries

本輪 review 納入：

- `backend/main.py`
- `backend/security.py`
- `backend/database.py`
- `backend/mailer.py`
- `frontend/login.html`
- `frontend/admin-login.html`
- `frontend/choose.html`
- `frontend/admin.html`
- `frontend/config.js`
- `import_students.py`
- `requirements.txt`

## Excluded Boundaries

本輪 review 未納入：

- `frontend/style.css`
  - 原因：視覺樣式不是本輪 security review 重點
- 字型檔 `frontend/TW-Kai-98_1.ttf`、`frontend/TW-Kai-Ext-B-98_1.ttf`
  - 原因：二進位資源不在本輪 source review 範圍
- deployment 平台設定（例如 Render dashboard 上的 secrets 與權限）
  - 原因：本輪僅能看到 repository 內容，無法直接檢視雲端平台設定

## Technology Stack

| 領域 | 技術 |
| --- | --- |
| Backend | FastAPI |
| Database | PostgreSQL + `psycopg2` |
| Authentication | JWT + `python-jose` |
| Password hashing | `bcrypt` |
| Frontend | 靜態 HTML / CSS / 原生 JavaScript |
| Email integration | Brevo API |
| PDF generation | ReportLab |

source evidence:

- `requirements.txt`
- `backend/main.py:1-52`
- `backend/security.py:1-52`
- `backend/database.py:1-74`
- `backend/mailer.py:1-195`

## Threat Model

### Threat Actors

- 一般學生使用者
- 已登入但不受信任的 client 端操作者
- 知道 API endpoint 的未授權外部使用者
- 後續維護者在不清楚 trust boundaries 的情況下進一步放大風險

### Primary Attack Surfaces

- `/login`
- `/admin-login`
- `/submit`
- `/admin/all`
- `/admin/import-students`
- `/admin/send-reminders`
- browser `localStorage`
- 與 Brevo API 的整合

### Key Trust Boundaries

- browser 與 backend 之間：所有 client 傳入欄位都應視為不可信
- backend 與 database 之間：資料庫紀錄會影響管理端查詢與行政操作
- backend 與外部寄信服務之間：寄信成功與否會影響通知是否到達

source evidence:

- `frontend/login.html:38-45`
- `frontend/choose.html:59-81`
- `frontend/admin.html:102-226`
- `backend/main.py:92-324`
- `backend/mailer.py:121-195`

## Methodology

本輪採用 OWASP-oriented static review，重點檢查以下類別：

### Authentication

- 檢查 password hashing 與 token issuance 流程
- 檢查 token 解析與 role-based gate 是否真的落在 server side

對應檔案：

- `backend/security.py`
- `backend/main.py`
- `frontend/login.html`
- `frontend/admin-login.html`

### Authorization / Broken Access Control

- 檢查管理端 routes 是否真的有 server-side protection
- 檢查前端帶 token 是否會造成假性安全感
- 檢查 client-controlled payload 是否被當成可信來源

對應檔案：

- `backend/main.py`
- `frontend/choose.html`
- `frontend/admin.html`

### Session / Token Handling

- 檢查 token 儲存位置
- 檢查 CSP / script policy 是否放大 token exposure 風險

對應檔案：

- `frontend/login.html`
- `frontend/admin-login.html`
- `frontend/admin.html`
- `frontend/choose.html`

### Input / File Handling

- 檢查 CSV upload 與 import 路徑
- 檢查資料列是否可能被未授權呼叫覆寫

對應檔案：

- `backend/main.py`
- `import_students.py`

### Configuration / Security Headers

- 檢查 CORS、CSP、environment variable 使用方式與預設值影響

對應檔案：

- `backend/main.py`
- `frontend/*.html`
- `frontend/config.js`

## Reviewed Areas Summary

| Area | 結論摘要 |
| --- | --- |
| Authentication | password hashing 與 JWT 存在，但 server-side enforcement 不一致 |
| Authorization | 存在高風險 gap，尤其是 `/submit` 與 `/admin/import-students` |
| Token handling | `localStorage` 搭配 inline scripts 放大 token exposure 風險 |
| File import | CSV import 可覆寫使用者資料，且 route 授權不一致 |
| Config | CORS 過寬、`API_BASE_URL` 硬編碼，增加營運與安全風險 |

## Limitations

- 本輪未做 runtime 驗證
- 本輪未對 Brevo 帳號設定與平台 secrets 做獨立稽核
- 本輪未對 dependency CVE 做完整掃描
- 本輪 focus 在 first-pass baseline，不代表已窮盡所有弱點
