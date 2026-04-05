# 已知缺口

本文件刻意把已知問題拆成兩類：

- **功能缺口**：使用者會直接感受到「功能不存在、未完成或與畫面不一致」
- **營運風險**：不一定立刻造成畫面錯誤，但會提高部署、維護、資料一致性或行政流程的風險

正式 security finding 不在本文件展開；會由獨立的 `docs/security/` audit 追蹤。

## 功能缺口

### 1. 前端提供修改管理員密碼 UI，但 backend 沒有對應 route

管理員頁面會呼叫 `POST /change-password`，但目前 `backend/main.py` 沒有這個 route。結果是 UI 看起來有此功能，實際上無法完成。

source evidence:

- `frontend/admin.html:217-228`
- `backend/main.py:55-335`

### 2. `DEADLINE_DATE` 目前只被解析，沒有實際套用到提交邏輯

`backend/main.py` 會讀取 `DEADLINE_DATE` 並產生 `deadline_dt`，但目前沒有看到任何 route 以此變數阻擋逾期送出或改填。首頁也只是靜態顯示截止日期。

source evidence:

- `backend/main.py:27-31`
- `backend/main.py:92-143`
- `frontend/index.html`

### 3. 首頁檔案包含重複 HTML 結構

`frontend/index.html` 在同一檔案中包含兩段 `<!DOCTYPE html>` / `<html>` 結構，這不一定立刻導致頁面壞掉，但代表首頁模板曾被重複拼接，後續維護時容易造成誤判。

source evidence:

- `frontend/index.html`

## 營運風險

### 1. `import_students.py` 與後台匯入 route 的行為不一致

專案同時存在：

- 後台 CSV 匯入：`backend/main.py:168-227`
- 獨立匯入 script：`import_students.py:9-39`

兩者的欄位支援、編碼處理與資料欄位覆蓋策略並不相同。如果維護者同時使用兩條路徑，可能造成資料行為不一致。

### 2. `API_BASE_URL` 硬編碼為 Render 網址

`frontend/config.js` 直接把 `API_BASE_URL` 設成 `https://student-choice-sys.onrender.com`。這代表：

- 本機測試不夠直觀
- 切換 staging / production 不方便
- 若網域改變，必須改前端檔案重新部署

source evidence:

- `frontend/config.js:1-5`

### 3. 啟動 scheduler，但目前看不到實際註冊 job

App 啟動時會 `scheduler.start()`，但目前沒有看到 `add_job()` 或其他排程註冊。這表示 scheduler 是已啟用但尚未承擔明確業務責任的元件。

source evidence:

- `backend/main.py:33`
- `backend/main.py:42`

### 4. `ADMIN_PASSWORD` 只在初次 seed 時生效

啟動時若有 `ADMIN_PASSWORD`，系統會嘗試插入 `admin` 使用者，但採用 `ON CONFLICT DO NOTHING`。這代表資料庫一旦已有 `admin`，之後只改 env var 並不會更新既有密碼。

source evidence:

- `backend/database.py:61-65`

### 5. 確認信寄送失敗不會回滾已寫入的選填結果

目前流程是先寫 DB，再產 PDF，再寄 email。若寄信失敗，系統仍會保留資料庫紀錄。這未必是錯誤，但維護者需要清楚知道：資料成功不等於通知成功。

source evidence:

- `backend/main.py:105-143`
- `backend/mailer.py:121-195`

## 建議後續追蹤方式

- 功能缺口：若會直接影響使用者，優先開一般功能或修正 change
- 營運風險：若會影響部署、資料一致性或行政流程，應開 maintenance / ops 類型 change
- Security 問題：集中放入 `docs/security/` 與對應 remediation change
