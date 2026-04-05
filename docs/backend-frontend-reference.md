# 前後端與模組對照

本文件用來回答一個很實際的維護問題：如果你想改某個畫面、某個 API、某個流程，應該先看哪個檔案？

## Backend 模組對照

| 檔案 | 主要責任 | 重點位置 |
| --- | --- | --- |
| `backend/main.py` | FastAPI app、routes、提交、管理端功能、靜態頁面掛載 | `55-335` |
| `backend/security.py` | bcrypt password hashing、JWT 建立與 bearer token 解析 | `15-52` |
| `backend/database.py` | PostgreSQL pool、schema initialization、admin seed | `9-74` |
| `backend/mailer.py` | PDF generation、Brevo email sending | `33-195` |
| `import_students.py` | 額外的匯入 script，直接從 `students.csv` 匯入資料 | `1-39` |

## Frontend 頁面對照

| 檔案 | 使用者 | 主要責任 | 重點位置 |
| --- | --- | --- | --- |
| `frontend/index.html` | 所有人 | 首頁、開始登入入口、管理員入口 | 整份檔案 |
| `frontend/login.html` | 學生 | 學生登入、token 與學生資料寫入 `localStorage` | `20-67` |
| `frontend/choose.html` | 學生 | 選擇班群、送出 payload | `32-103` |
| `frontend/admin-login.html` | 管理員 | 管理員登入 | `20-63` |
| `frontend/admin.html` | 管理員 | 載入結果、匯出 CSV、匯入學生名單、寄提醒信 | `94-231` |
| `frontend/config.js` | 前後台共用 | 設定 `API_BASE_URL` | `1-5` |

## Route 對照表

| Route | Method | 用途 | 前端入口 | 後端授權檢查 |
| --- | --- | --- | --- | --- |
| `/login` | `POST` | 學生登入 | `frontend/login.html` | 無 |
| `/admin-login` | `POST` | 管理員登入 | `frontend/admin-login.html` | 以 `role == admin` 驗證 |
| `/submit` | `POST` | 送出班群選填 | `frontend/choose.html` | Route 本身未宣告 `Depends(get_current_user)` |
| `/admin/all` | `GET` | 讀取所有學生與選填結果 | `frontend/admin.html` | 有，且限制 `role == admin` |
| `/admin/import-students` | `POST` | 匯入學生名單 CSV | `frontend/admin.html` | Route 本身未宣告 `Depends(get_current_user)` |
| `/admin/send-reminders` | `POST` | 寄送未選填提醒信 | `frontend/admin.html` | 有，且限制 `role == admin` |
| `/` | `GET` / `HEAD` | 首頁 | 直接進站 | 無 |
| `/login` | `GET` | 學生登入頁 | 首頁按鈕 | 無 |
| `/choose` | `GET` | 學生選填頁 | 登入成功後導向 | 無 |
| `/admin` | `GET` | 管理員控制台頁面 | 管理員登入成功後導向 | 無，頁面本身依賴前端檢查 |
| `/admin-login` | `GET` | 管理員登入頁 | 首頁右上角按鈕 | 無 |

source evidence:

- `backend/main.py:55-166`
- `backend/main.py:168-335`
- `frontend/login.html:30-55`
- `frontend/choose.html:74-82`
- `frontend/admin.html:100-228`

## 學生流程對照

### 登入

- Frontend 送 `student_id`、`password` 到 `/login`
- Backend 回傳 `access_token`、`role`、`name`、`email`、`student_id`、`student_class_num`
- Frontend 寫入 `localStorage`

對照檔案：

- `frontend/login.html:30-45`
- `backend/main.py:55-75`

### 選填

- Frontend 從 `localStorage` 取出 `userName`、`userEmail`、`userId`、`user_class_num`
- Frontend 組成 `payload`
- Backend 以 `student_id` upsert 到 `selections`
- Backend 產 PDF 並寄 email

對照檔案：

- `frontend/choose.html:59-81`
- `backend/main.py:92-143`
- `backend/mailer.py:33-195`

## 管理員流程對照

### 查詢與匯出

- 管理員頁面一載入就呼叫 `/admin/all`
- 匯出 CSV 也是先抓 `/admin/all` 的結果，再在瀏覽器端組成 `data:text/csv`

對照檔案：

- `frontend/admin.html:94-154`
- `backend/main.py:145-166`

### 匯入學生名單

- 瀏覽器把 CSV 透過 `FormData` 上傳
- Backend 解析編碼、欄位標頭、每列資料，並做 upsert

對照檔案：

- `frontend/admin.html:156-183`
- `backend/main.py:168-227`

### 寄提醒信

- 前端先確認操作，再呼叫 `/admin/send-reminders`
- Backend 查詢尚未選填且有 email 的學生，逐筆寄信，並在每封之間 `sleep(1.2)` 秒

對照檔案：

- `frontend/admin.html:185-215`
- `backend/main.py:230-324`

## 快速除錯建議

| 看到的問題 | 建議先看哪裡 |
| --- | --- |
| 登入失敗 | `frontend/login.html`、`frontend/admin-login.html`、`backend/main.py`、`backend/security.py` |
| 選填送出失敗 | `frontend/choose.html`、`backend/main.py`、`backend/mailer.py` |
| 看不到學生資料 | `frontend/admin.html`、`backend/main.py`、`backend/database.py` |
| CSV 匯入失敗 | `frontend/admin.html`、`backend/main.py`、`import_students.py` |
| 確認信 / 提醒信沒寄出 | `backend/mailer.py`、`backend/main.py` |
