# 系統架構

## 技術組成

| 層級 | 技術 / 元件 | 說明 |
| --- | --- | --- |
| Web backend | FastAPI | 提供登入、提交、管理端與靜態頁面 routes |
| Database | PostgreSQL + `psycopg2` | 儲存 `users` 與 `selections` |
| Password / Token | `bcrypt`、JWT (`python-jose`) | password hashing 與 access token |
| Email | Brevo SMTP API | 寄送確認信與提醒信 |
| PDF | ReportLab | 產生班群選擇確認表 PDF |
| Frontend | 靜態 HTML + CSS + 原生 JavaScript | 學生與管理員頁面 |
| Runtime helpers | APScheduler | 啟動 scheduler，但目前未看到註冊 job |

主要 source evidence:

- `requirements.txt`
- `backend/main.py:1-52`
- `backend/security.py:1-52`
- `backend/database.py:1-74`
- `backend/mailer.py:1-195`

## 高階拓樸

```text
瀏覽器
  ├─ 學生頁面: /login -> /choose
  └─ 管理頁面: /admin-login -> /admin
        |
        v
FastAPI app (backend/main.py)
  ├─ authentication / admin routes
  ├─ selection submit route
  ├─ student import route
  ├─ reminder route
  └─ static file routes
        |
        +--> PostgreSQL (users, selections)
        |
        +--> Brevo API (寄信)
        |
        +--> ReportLab (產生 PDF bytes)
```

## 主要組件責任

### App lifecycle 與路由註冊

FastAPI app 在 `lifespan` 中啟動 DB pool、初始化資料表並啟動 scheduler。所有主要 routes 都定義在 `backend/main.py`，包含：

- `/login`
- `/admin-login`
- `/submit`
- `/admin/all`
- `/admin/import-students`
- `/admin/send-reminders`
- 靜態頁面 routes 與 `/static`

source evidence:

- `backend/main.py:36-48`
- `backend/main.py:55-335`

### Database layer

`backend/database.py` 管理 PostgreSQL connection pool 與 schema initialization。啟動時會建立：

- `users` 表
- `selections` 表
- `users.student_class_num` 欄位（若不存在則補上）
- `admin` 帳號（若環境變數 `ADMIN_PASSWORD` 存在且資料庫中尚未有主鍵衝突）

source evidence:

- `backend/database.py:9-25`
- `backend/database.py:42-74`

### Security layer

`backend/security.py` 負責：

- 以 bcrypt hash password
- 驗證 password
- 簽發 JWT access token
- 解析 bearer token 並回傳 `student_id` 與 `role`

source evidence:

- `backend/security.py:15-52`

### Mail / PDF layer

`backend/mailer.py` 同時承擔兩個責任：

- 產生 PDF 確認表
- 呼叫 Brevo API 寄送確認信或提醒信

這個檔案會在 module import 時註冊字型，若字型檔不存在，啟動期就會印出錯誤訊息。

source evidence:

- `backend/mailer.py:14-31`
- `backend/mailer.py:33-118`
- `backend/mailer.py:120-195`

## Trust Boundaries

### Browser 與 backend 之間

Frontend 會把登入取得的 token 與使用者資訊寫進 `localStorage`，之後再帶入 API 呼叫。這代表瀏覽器端的儲存內容屬於 client-controlled data，後端不能因為前端送了某些欄位就直接視為可信。

source evidence:

- `frontend/login.html:38-45`
- `frontend/admin-login.html:38-45`
- `frontend/choose.html:59-81`
- `frontend/admin.html:102-170`

### Backend 與 database 之間

所有資料持久化都經過 PostgreSQL。`users` 保存帳號資訊，`selections` 保存選填結果。對於教務流程來說，database 是數位紀錄來源，但實際行政流程仍有紙本簽核環節。

source evidence:

- `backend/database.py:42-68`
- `backend/main.py:105-116`
- `backend/main.py:152-163`

### Backend 與外部服務之間

寄信能力依賴 Brevo API，且需要 `BREVO_API_KEY` 與 `GMAIL_USER`。如果環境變數缺失，backend 仍可運作，但寄信會失敗。

source evidence:

- `backend/mailer.py:121-127`
- `backend/mailer.py:163-191`

## 啟動流程

1. 建立 FastAPI app。
2. 啟用寬鬆的 CORS middleware。
3. 啟動時執行 `lifespan`：
   - `init_db_pool()`
   - `init_db()`
   - `scheduler.start()`
4. 掛載靜態頁面與 `frontend/` 資源。

source evidence:

- `backend/main.py:36-48`
- `backend/main.py:325-335`

## 與學生維護者最相關的結論

- 核心實作幾乎都集中在 `backend/main.py`、`backend/database.py`、`backend/security.py` 與 `backend/mailer.py`。
- 前端不是 framework project，所以要理解行為時，通常直接看 HTML 檔案內嵌的 JavaScript 即可。
- 目前系統邏輯很集中，交接容易，但也代表單一檔案承擔多個責任，後續擴充時要注意維護成本。
