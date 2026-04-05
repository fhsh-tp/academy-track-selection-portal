# API 與資料模型

## API Surface

### `POST /login`

用途：學生登入

Request body:

```json
{
  "student_id": "11400000",
  "password": "plaintext-password"
}
```

成功回傳欄位：

- `access_token`
- `role`
- `name`
- `email`
- `student_id`
- `student_class_num`

source evidence:

- `backend/main.py:55-75`
- `frontend/login.html:30-55`

### `POST /admin-login`

用途：管理員登入

Request body:

```json
{
  "student_id": "admin",
  "password": "plaintext-password"
}
```

成功回傳欄位：

- `access_token`
- `role`

source evidence:

- `backend/main.py:77-90`
- `frontend/admin-login.html:30-55`

### `POST /submit`

用途：學生提交班群選擇，並觸發 PDF 與確認信

目前 payload 欄位包含：

- `choice`
- `name`
- `student_id`
- `email`
- `student_class_num`
- `submit_time`

成功回傳：

- `status`
- `message`

source evidence:

- `frontend/choose.html:62-82`
- `backend/main.py:92-143`

### `GET /admin/all`

用途：回傳所有學生與選填結果，供管理頁面列表與 CSV 匯出使用

回傳欄位包含：

- `student_id`
- `name`
- `email`
- `student_class_num`
- `choice`
- `updated_at`

source evidence:

- `backend/main.py:145-166`
- `frontend/admin.html:100-154`

### `POST /admin/import-students`

用途：匯入學生名單 CSV，更新或新增學生帳號資料

輸入形式：

- `multipart/form-data`
- 欄位名稱：`file`

Backend 會嘗試支援：

- `big5-hkscs`
- `utf-8-sig`

CSV 欄位名稱支援中英文別名，例如：

- `name` / `姓名`
- `student_id` / `學號`
- `password` / `密碼`
- `student_class_num` / `class_num` / `班級座號`
- `email` / `電子信箱`

source evidence:

- `backend/main.py:168-227`
- `frontend/admin.html:156-183`

### `POST /admin/send-reminders`

用途：寄送尚未選填學生的提醒信

執行步驟：

1. 查詢 `selections` 沒有對應紀錄的學生
2. 過濾 `email` 為空值的學生
3. 逐筆寄送提醒信
4. 每封信之間等待 1.2 秒

source evidence:

- `backend/main.py:230-324`
- `frontend/admin.html:185-215`

## 資料模型

### `users`

欄位：

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `student_id` | `TEXT PRIMARY KEY` | 學號或管理員帳號 |
| `name` | `TEXT NOT NULL` | 姓名 |
| `password` | `TEXT NOT NULL` | bcrypt hash 後的 password |
| `role` | `TEXT` | 預設 `student`，管理員為 `admin` |
| `email` | `TEXT` | email |
| `student_class_num` | `TEXT` | 班級座號，啟動時若缺欄位會自動補上 |

source evidence:

- `backend/database.py:46-59`

### `selections`

欄位：

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `student_id` | `TEXT PRIMARY KEY` | 外鍵，對應 `users.student_id` |
| `choice` | `INTEGER NOT NULL` | 班群代碼 |
| `updated_at` | `TIMESTAMP` | 更新時間 |

source evidence:

- `backend/database.py:47-48`

### 班群代碼

| 代碼 | 顯示文字 |
| --- | --- |
| `1` | 文法商（數 A 課程路徑） |
| `2` | 文法商（數 B 課程路徑） |
| `3` | 理工資 |
| `4` | 生醫農 |

source evidence:

- `backend/main.py:34`
- `backend/main.py:130-131`
- `frontend/admin.html:87-92`
- `frontend/choose.html:14-17`

## Environment Variables

| 變數 | 用途 | 讀取位置 |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL 連線字串 | `backend/database.py:6`, `import_students.py:7` |
| `SECRET_KEY` | JWT signing key | `backend/security.py:11` |
| `ADMIN_PASSWORD` | 啟動時建立預設 admin 帳號 | `backend/database.py:62-65` |
| `BREVO_API_KEY` | Brevo API 金鑰 | `backend/mailer.py:122` |
| `GMAIL_USER` | 發信者 email | `backend/mailer.py:123` |
| `DEADLINE_DATE` | 截止時間設定值 | `backend/main.py:27-31` |

## 外部整合

### Brevo

- API endpoint：`https://api.brevo.com/v3/smtp/email`
- 用於確認信與提醒信

source evidence:

- `backend/mailer.py:163-184`

### ReportLab

- 用來產生 PDF 確認表
- 依賴 `frontend/TW-Kai-98_1.ttf` 與 `frontend/TW-Kai-Ext-B-98_1.ttf`

source evidence:

- `backend/mailer.py:14-31`
- `backend/mailer.py:33-118`

## 維護時最常用的對照關係

- 想改 request / response 欄位：先看 `backend/main.py` 與對應前端頁面
- 想改 DB schema：先看 `backend/database.py`
- 想改 token / password 行為：先看 `backend/security.py`
- 想改 email 或 PDF 樣式：先看 `backend/mailer.py`
