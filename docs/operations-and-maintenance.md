# 部署、營運與維護

## 啟動前條件

至少需要準備以下項目：

- PostgreSQL database
- `DATABASE_URL`
- `SECRET_KEY`
- `BREVO_API_KEY`
- `GMAIL_USER`
- `ADMIN_PASSWORD`

若未提供 `DEADLINE_DATE`，系統會 fallback 到 `2026-05-04 23:59:59`。

source evidence:

- `backend/main.py:27-31`
- `backend/security.py:10-13`
- `backend/database.py:6-18`
- `backend/database.py:62-65`
- `backend/mailer.py:121-127`

## 啟動時會做的事

當 FastAPI app 啟動時：

1. 建立 PostgreSQL connection pool
2. 初始化資料表
3. 補齊 `student_class_num` 欄位
4. 嘗試建立預設 admin 帳號
5. 啟動 APScheduler

source evidence:

- `backend/main.py:36-45`
- `backend/database.py:42-74`

## 日常營運工作

### 1. 學生名單匯入

管理員可透過後台上傳 CSV。若需要批次處理，也可使用 `import_students.py`，但兩者邏輯並不完全一致，因此建議優先以 web 後台 route 為主。

後台匯入特性：

- 支援欄位名稱中英文別名
- 嘗試處理 Big5 與 UTF-8 BOM
- 缺少 `password` 時會 fallback 成 `sid`

source evidence:

- `backend/main.py:168-227`
- `import_students.py:9-39`

### 2. 選填結果查詢與匯出

管理員頁面會先讀 `/admin/all`，再由瀏覽器端自行組 CSV 下載，不是由 backend 直接回傳檔案。

source evidence:

- `frontend/admin.html:138-154`
- `backend/main.py:145-166`

### 3. 寄送未選填提醒信

管理員從後台手動觸發提醒信。系統目前沒有看到 scheduler job 註冊，因此提醒信不是自動排程，而是人工操作。

source evidence:

- `backend/main.py:33`
- `backend/main.py:42`
- `backend/main.py:230-324`

### 4. PDF 與確認信

學生送出後，系統會同步：

- upsert `selections`
- 呼叫 ReportLab 產生 PDF bytes
- 呼叫 Brevo API 寄信

若寄信失敗，系統會回覆「郵件寄送失敗，但資料已存檔」，表示 DB 寫入與寄信目前不是 transaction-bound 的同一個單位。

source evidence:

- `backend/main.py:105-143`
- `backend/mailer.py:33-195`

## 維護建議

### 調整登入或授權

請同時檢查：

- `backend/security.py`
- `backend/main.py`
- `frontend/login.html`
- `frontend/admin-login.html`
- `frontend/admin.html`
- `frontend/choose.html`

原因是目前 token 的建立、儲存與使用分散在這些檔案。

### 調整資料模型

請先檢查：

- `backend/database.py`
- `backend/main.py`
- `frontend/admin.html`
- `frontend/choose.html`

原因是資料欄位名稱會同時影響 DB schema、API 回傳與 frontend `localStorage` key。

### 調整 email 或 PDF

請先檢查：

- `backend/mailer.py`
- `backend/main.py`
- `frontend/TW-Kai-98_1.ttf`
- `frontend/TW-Kai-Ext-B-98_1.ttf`

## 建議的維護檢查清單

每次修改後至少確認：

1. 學生登入仍可成功寫入 `localStorage`
2. 管理員登入仍可讀取 `/admin/all`
3. 選填送出仍可寫入 `selections`
4. 匯入 CSV 仍可正確處理中文欄位與編碼
5. 寄信所需 env vars 是否都在 deployment 環境中
6. 文件是否需要同步更新

## 後續文件更新原則

- 優先更新本目錄文件，再更新對應 Spectra change 或新 change
- 所有重要說明盡量附上 source file reference
- 若是 security finding，不要只寫在一般文件；請放到 `docs/security/`
