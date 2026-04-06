# 資訊安全稽核報告

## 執行摘要

本次針對 **academy-track-selection-portal** 的程式碼資訊安全審查於 **2026-04-06** 執行，審查基準為 branch **`refactor/security-enhance`** 與 commit **`c72ebdda6aefc64a59a9a2234d1babc158bcc6c5`**。審查範圍涵蓋 FastAPI backend、靜態 frontend、驗證與授權流程、CSV 匯入路徑、郵件寄送邏輯、部署組態，以及已鎖定的 Python 相依套件。共識別 **4** 項仍然成立的 active finding：**0** 項 Critical、**1** 項 High、**3** 項 Medium、**0** 項 Low。

整體風險為 **仍需處理，但比 2026-04-05 baseline 收斂**。先前報告中的 3 項問題已無法在目前程式碼重現：未授權 `/submit` 寫入、未授權學生匯入路由，以及 wildcard CORS 設定。現階段最重要的風險集中在可部署的預設管理員密碼、瀏覽器可讀的 JWT storage 搭配寬鬆 script 執行面、缺少登入節流，以及匯入流程把 backend 例外細節直接回傳給前端。正面觀察則包括：已審查的 SQL 寫入皆使用參數化查詢，且 locked dependency scan 在本次審查時 **未發現已知公開弱點**。

## 審查範圍

### 2.1 審查標的

| 項目 | 內容 |
|---|---|
| 應用程式名稱 | academy-track-selection-portal |
| 版本 / Commit | `refactor/security-enhance` / `c72ebdda6aefc64a59a9a2234d1babc158bcc6c5` |
| Repository | `/Users/phoenix/dev/fhsh-projects/academy-track-selection-portal` |
| 環境 | Repository static review |
| 審查期間 | 2026-04-06 至 2026-04-06 |
| Audit Name | `project-wide-security-audit-2026-04-06` |

### 2.2 範圍界定

**範圍內：**

- `backend/main.py`、`backend/security.py`、`backend/database.py`、`backend/mailer.py`、`backend/utils/email.py`
- `frontend/login.html`、`frontend/admin-login.html`、`frontend/choose.html`、`frontend/admin.html`、`frontend/index.html`、`frontend/static/config.js`
- `nginx/nginx.conf`、`nginx/entrypoint.sh`、`Dockerfile`、`docker-compose.yml`、`scripts/docker-entrypoint.sh`
- `import_students.py`、`pyproject.toml`、`uv.lock`、`.env.example`
- `docs/security/2026-04-05_codex_audit/` 作為歷史比對基線

**範圍外：**

- Runtime exploitation 或 dynamic penetration testing
- Cloudflare、SMTP provider、host OS 等 deployment console 設定
- 真實 `.env` secrets
- 二進位字型資產與非安全相關 CSS 樣式

### 2.3 技術架構

| 層級 | 技術 |
|---|---|
| 程式語言 | Python 3.12+、HTML、JavaScript |
| 框架 | FastAPI、Pydantic、Nginx |
| 資料庫 | PostgreSQL + `psycopg2` |
| 驗證 | JWT (`python-jose`)、bearer token flow、`bcrypt` |
| 郵件 / PDF | `aiosmtplib`、ReportLab |
| 套件管理 | `uv`、`pyproject.toml`、`uv.lock` |
| 部署 | Docker、Docker Compose、Cloudflare Tunnel |

### 2.4 適用標準

- OWASP Top 10（2021）
- OWASP Web Security Testing Guide v4.2
- OWASP Code Review Guide v2
- CWE/SANS Top 25

## 審查方法論

本次審查採用以 OWASP 類別為核心的人工 source review。審查類別包含 authentication、authorization、session management、input validation、injection、cryptography、error handling、logging and monitoring、data protection，以及 dependency / supply-chain risk。所有 finding 都以目前程式碼路徑中的 user-controlled input 與 trust boundary 為基礎，回填成具體 file-level evidence。

### 3.1 舊基線重新驗證

2026-04-05 的舊報告只作為歷史輸入，不直接沿用。重新驗證結果如下：

- 舊 `FINDING-001`（未授權 `/submit`）在目前程式碼中已 **closed**，因為 `/submit` 現在要求 `Depends(get_current_user)`，並在 `backend/main.py:130-137` 比對 token 與 `student_id`。
- 舊 `FINDING-002`（未授權學生匯入）在目前程式碼中已 **closed**，因為 `/admin/import-students` 現在要求驗證與 `role == admin`，位置在 `backend/main.py:213-216`。
- 舊 `FINDING-003`（client-side token exposure）在目前程式碼中 **仍成立，但已改寫** 為本輪 `FINDING-002`。
- 舊 `FINDING-004`（wildcard CORS）在目前程式碼中已 **closed**，因為 `backend/main.py:44-55` 改為以 allow-list 建構 origins，而不是 `["*"]`。

### 3.2 Dependency 弱點掃描

本輪額外執行了 locked dependency scan，方法是使用 `uv export --format requirements-txt --no-hashes` 搭配 `pip-audit --no-deps --disable-pip -f json`。掃描結果顯示目前鎖定的 Python 相依套件 **未發現已知公開弱點**。工具無法替 editable local project entry（`-e -`）推導版本，因此該項未納入 CVE 比對。

## 弱點發現摘要

### 4.1 風險分布

| 嚴重性 | 數量 |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 0 |
| **總計** | **4** |

### 4.2 發現索引

| ID | 標題 | 嚴重性 | CWE | 狀態 |
|---|---|---|---|---|
| FINDING-001 | Known default admin password in container defaults | High | CWE-1392 | Open |
| FINDING-002 | JWT tokens persist in localStorage with unsafe-inline CSP | Medium | CWE-922 | Open |
| FINDING-003 | Import route returns raw backend exception details | Medium | CWE-209 | Open |
| FINDING-004 | Login endpoints lack brute-force throttling | Medium | CWE-307 | Open |

## 詳細弱點報告

### FINDING-001: Known default admin password in container defaults

| 屬性 | 值 |
|---|---|
| **ID** | FINDING-001 |
| **嚴重性** | High |
| **CWE** | CWE-1392 |
| **OWASP Top 10** | A05:2021 Security Misconfiguration |
| **位置** | `docker-compose.yml:31-32`、`backend/database.py:61-64` |
| **狀態** | Open |

#### 弱點描述

backend container 為 `ADMIN_PASSWORD` 定義了可預測的 fallback 值，而資料庫初始化程式會直接拿這個值來建立或保留管理員帳號密碼。若部署時忘記覆寫環境變數，系統就可能以已知密碼啟動管理員登入面。

#### 證據

- `docker-compose.yml:31` 設定 `ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}`
- `docker-compose.yml:32` 設定 `ADMIN_PASSWORD: ${ADMIN_PASSWORD:-admin_password_you_know_it}`
- `backend/database.py:61-64` 在啟動時讀取該值並建立 admin password hash

#### 影響

攻擊者一旦知道預設密碼，就可透過 `/admin-login` 取得管理權限，讀取全部學生資料、覆寫帳號內容，並觸發管理功能。

#### 修復建議

移除可預測的 fallback，並在 `ADMIN_PASSWORD` 缺失或等於弱預設值時 fail closed。部署流程應明確提供高熵 secret，或改用一次性 bootstrap 流程。

#### 參考資料

- [CWE-1392](https://cwe.mitre.org/data/definitions/1392.html)
- [OWASP Top 10 A05:2021 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

### FINDING-002: JWT tokens persist in localStorage with unsafe-inline CSP

| 屬性 | 值 |
|---|---|
| **ID** | FINDING-002 |
| **嚴重性** | Medium |
| **CWE** | CWE-922 |
| **OWASP Top 10** | A07:2021 Identification and Authentication Failures |
| **位置** | `frontend/login.html:4,39`、`frontend/admin-login.html:4,43`、`frontend/choose.html:59,79`、`frontend/admin.html:4,104,170,206` |
| **狀態** | Open |

#### 弱點描述

系統把 bearer token 寫入 `localStorage`，後續再由前端 JavaScript 讀出加入 `Authorization` header。同時頁面 CSP 允許 `'unsafe-inline'`，使任何可執行的同頁腳本都更容易讀取並重放 token。

#### 證據

- `frontend/login.html:39-44`、`frontend/admin-login.html:43-44` 把 token 寫入 `localStorage`
- `frontend/choose.html:79`、`frontend/admin.html:104,170,206` 從 `localStorage` 取回 token
- `frontend/login.html:4`、`frontend/admin-login.html:4`、`frontend/choose.html:4`、`frontend/admin.html:4` 都允許 `'unsafe-inline'`

#### 影響

若未來出現 XSS 或其他 script injection，攻擊者可直接竊取學生或管理員 token。管理員 token 外洩時，影響面會擴及整個後台資料與批次操作能力。

#### 修復建議

改用 `HttpOnly` cookie 或其他 server-controlled token storage，並移除 `'unsafe-inline'`，改採 nonce/hash-based CSP 與外部 script 檔。

#### 參考資料

- [CWE-922](https://cwe.mitre.org/data/definitions/922.html)
- [OWASP Top 10 A07:2021 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

### FINDING-003: Import route returns raw backend exception details

| 屬性 | 值 |
|---|---|
| **ID** | FINDING-003 |
| **嚴重性** | Medium |
| **CWE** | CWE-209 |
| **OWASP Top 10** | A05:2021 Security Misconfiguration |
| **位置** | `backend/main.py:269-273`、`frontend/admin.html:178-179` |
| **狀態** | Open |

#### 弱點描述

CSV 匯入路由在發生例外時，直接把 backend 的 `str(e)` 當成 HTTP 500 `detail` 回傳，前端再原樣顯示。這會把內部 schema 與錯誤處理細節暴露給已登入管理員。

#### 證據

- `backend/main.py:273` 直接回傳 `detail=str(e)`
- `frontend/admin.html:178-179` 直接顯示 `err.detail`

#### 影響

這不是直接的權限突破，但會增加後續探測與 payload 調整的資訊量，也讓 production-facing UI 顯示不受控的 backend 內部訊息。

#### 修復建議

對 client 回傳通用錯誤訊息，把原始 exception 留在 server-side log，並搭配 request ID 或 job ID 供維護者追蹤。

#### 參考資料

- [CWE-209](https://cwe.mitre.org/data/definitions/209.html)
- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)

### FINDING-004: Login endpoints lack brute-force throttling

| 屬性 | 值 |
|---|---|
| **ID** | FINDING-004 |
| **嚴重性** | Medium |
| **CWE** | CWE-307 |
| **OWASP Top 10** | A07:2021 Identification and Authentication Failures |
| **位置** | `backend/main.py:89-128` |
| **狀態** | Open |

#### 弱點描述

學生與管理員登入路徑都會直接驗證 password hash，但程式碼中沒有任何 failed-attempt counter、固定延遲、lockout 或 IP-based throttling。這讓密碼猜測的防線完全依賴使用者密碼強度。

#### 證據

- `backend/main.py:89-101` 的 `/login` 沒有 rate-control
- `backend/main.py:112-127` 的 `/admin-login` 也沒有 rate-control

#### 影響

弱密碼的學生帳號可被批次嘗試，管理員帳號一旦被暴力破解成功，將直接暴露管理端的全部功能與資料。

#### 修復建議

在 authentication boundary 加入 per-account 與 per-IP 節流、失敗次數追蹤，以及更嚴格的管理員登入保護策略，例如 lockout 或 MFA。

#### 參考資料

- [CWE-307](https://cwe.mitre.org/data/definitions/307.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 修復優先順序

| 優先序 | Finding ID | 標題 | 嚴重性 | 預估工作量 | 備註 |
|---:|---|---|---|---|---|
| 1 | FINDING-001 | Known default admin password in container defaults | High | Low | 下次部署前先移除危險 fallback |
| 2 | FINDING-002 | JWT tokens persist in localStorage with unsafe-inline CSP | Medium | High | 需協調 backend / frontend 驗證與 CSP 設計 |
| 3 | FINDING-004 | Login endpoints lack brute-force throttling | Medium | Medium | 在 auth boundary 加入節流與失敗追蹤 |
| 4 | FINDING-003 | Import route returns raw backend exception details | Medium | Low | 改成通用錯誤訊息與 request ID |

## 附錄

### A. 參考資料

- [OWASP Top 10（2021）](https://owasp.org/Top10/)
- [OWASP Web Security Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Code Review Guide v2](https://owasp.org/www-project-code-review-guide/)
- [CWE — Common Weakness Enumeration](https://cwe.mitre.org/)

### B. 使用工具

| 工具 | 用途 |
|---|---|
| 人工 source review | 主要程式碼審查流程 |
| `owasp-audit` CLI | Audit lifecycle、finding 驗證與 report 驗證 |
| `pip-audit`（經由 `uvx`） | Locked dependency vulnerability scan |

### C. Dependency Scan 結果

- Command pattern：`uv export --format requirements-txt --no-hashes` + `pip-audit -r <exported-file> --no-deps --disable-pip -f json`
- Result：2026-04-06 當下，locked Python dependency set 未發現已知公開弱點
- Limitation：editable local project entry（`-e -`）無法被工具映射到 package version，因此未納入 CVE 比對

_報告撰寫人：Codex_
_日期：2026-04-06_
_分類：Internal_
