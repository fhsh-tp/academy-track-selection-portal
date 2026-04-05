# 專案總覽

## 專案目標

本系統用來支援「高一升高二普通班學生選擇班群」作業。學生在網站登入後選填班群，系統會：

1. 將選填結果寫入資料庫
2. 產生 PDF 確認表
3. 寄送確認 email 給學生

之後學生仍須列印紙本、完成簽名並繳交。從系統設計來看，網站負責加速資料收集與通知，紙本流程仍然是行政作業的重要一環。

## 使用者角色

### 學生

- 以學號與密碼登入
- 進入選填頁面
- 選擇一個班群並送出
- 收到附 PDF 的確認 email
- 列印、簽名、繳交紙本

主要 source evidence:

- `frontend/login.html`
- `frontend/choose.html`
- `backend/main.py`
- `backend/mailer.py`

### 管理員

- 由獨立的 `/admin-login` 入口登入
- 檢視所有學生與選填結果
- 匯出 CSV
- 匯入學生名單
- 寄送未選填提醒信

主要 source evidence:

- `frontend/admin-login.html`
- `frontend/admin.html`
- `backend/main.py`

## 主要流程

### 學生選填流程

1. 學生在登入頁送出學號與密碼。
2. Backend 查詢 `users` 資料表，驗證 bcrypt password，成功後簽發 JWT access token。
3. Frontend 將 token 與學生資訊寫入 `localStorage`。
4. 學生在選填頁選擇班群並送出。
5. Backend 寫入 `selections` 資料表，產生 PDF，並經由 Brevo API 寄送確認 email。

對應檔案與位置：

- `backend/main.py:55-75`
- `backend/main.py:92-143`
- `backend/security.py:15-52`
- `frontend/login.html:20-67`
- `frontend/choose.html:32-103`
- `backend/mailer.py:33-195`

### 管理員營運流程

1. 管理員在 `/admin-login` 登入。
2. 管理員頁面啟動後，呼叫 `/admin/all` 讀取學生與選填結果。
3. 若要匯入學生名單，前端上傳 CSV 給 `/admin/import-students`。
4. 若要催填，前端呼叫 `/admin/send-reminders`，backend 逐筆寄送提醒信。

對應檔案與位置：

- `backend/main.py:77-90`
- `backend/main.py:145-166`
- `backend/main.py:168-227`
- `backend/main.py:230-324`
- `frontend/admin-login.html:20-63`
- `frontend/admin.html:94-231`

## 這個系統目前不是什麼

- 不是 SPA framework project；前端是靜態 HTML 搭配原生 JavaScript。
- 不是多服務 microservices 架構；主要 backend 在單一 FastAPI app。
- 不是完整的 workflow engine；目前行政流程仍仰賴人工紙本簽核與教務處收件。

## 建議下一步閱讀

- 想看整體組件與 trust boundaries：讀 [系統架構](./system-architecture.md)
- 想快速找某個頁面或 route 對應哪個檔案：讀 [前後端與模組對照](./backend-frontend-reference.md)
- 想看 API / DB / env var：讀 [API 與資料模型](./api-and-data-model.md)
- 想知道目前還缺什麼、風險在哪：讀 [已知缺口](./known-gaps.md)
