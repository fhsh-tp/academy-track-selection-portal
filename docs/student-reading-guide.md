# 學生導讀版：專案文件與初次 Security Audit 摘要

本文件是給原始學生開發者與後續接手學生看的導讀版摘要。它的目的不是取代完整文件，而是幫你先抓到這個專案目前最重要的脈絡：

1. 這個系統現在做了什麼
2. 哪些文件已經整理完成
3. 目前最需要注意的技術與行政風險是什麼
4. 接下來若要繼續維護，應該先討論哪些事情

## 先看結論

這個專案目前已經完成兩大類文件基線：

- 一般專案文件：說明系統用途、流程、架構、API、資料模型、部署與已知缺口
- 初次 security audit：整理目前 source code 中最重要的 security 風險、證據、影響與後續建議

換句話說，現在這個 repository 不再只是「有程式碼」，而是已經有第一版正式的知識整理與風險基線。

## 建議閱讀順序

如果你是第一次接手，建議照這個順序讀：

1. [專案總覽](./project-overview.md)
2. [系統架構](./system-architecture.md)
3. [前後端與模組對照](./backend-frontend-reference.md)
4. [API 與資料模型](./api-and-data-model.md)
5. [部署、營運與維護](./operations-and-maintenance.md)
6. [已知缺口](./known-gaps.md)
7. [初次 Security Audit Report](./security/initial-audit-report.md)
8. `docs/security/findings/` 底下的個別 finding

## 一般專案文件目前整理了什麼

### 1. 系統目的與行政流程

這個系統的核心目的是協助高一升高二學生完成班群選填，並支援：

- 學生登入與送出班群
- 系統寄送確認信與 PDF
- 管理員查詢、匯入學生資料、寄送提醒信

但要注意，這個系統**不是**完全取代紙本流程。從目前設計來看，紙本簽名與教務處收件仍然是行政流程中的重要一環。

主要文件：

- [project-overview.md](./project-overview.md)

### 2. 架構與責任分工

目前系統是單體式架構：

- backend：FastAPI
- frontend：靜態 HTML + 原生 JavaScript
- database：PostgreSQL
- email：Brevo API
- PDF：ReportLab

核心邏輯主要集中在少數檔案：

- `backend/main.py`
- `backend/security.py`
- `backend/database.py`
- `backend/mailer.py`
- `frontend/login.html`
- `frontend/choose.html`
- `frontend/admin.html`

主要文件：

- [system-architecture.md](./system-architecture.md)
- [backend-frontend-reference.md](./backend-frontend-reference.md)

### 3. API、資料表與 env vars

文件已整理：

- 主要 routes
- `users` / `selections` 資料表
- `DATABASE_URL`、`SECRET_KEY`、`ADMIN_PASSWORD`、`BREVO_API_KEY`、`GMAIL_USER`、`DEADLINE_DATE`

主要文件：

- [api-and-data-model.md](./api-and-data-model.md)

### 4. 部署與日常維護

文件已整理：

- 啟動時會做什麼
- 學生名單匯入與提醒信流程
- 維護時應先看哪些檔案
- 每次調整後應檢查哪些事情

主要文件：

- [operations-and-maintenance.md](./operations-and-maintenance.md)

### 5. 已知缺口

這部分已刻意拆成兩類：

- **功能缺口**
- **營運風險**

例如：

- 管理員頁面有「修改密碼」UI，但 backend 沒有對應 route
- `DEADLINE_DATE` 有讀進來，但尚未真正套用在提交限制
- `API_BASE_URL` 硬編碼
- `import_students.py` 與後台匯入 route 行為不一致

主要文件：

- [known-gaps.md](./known-gaps.md)

## 初次 Security Audit 目前整理了什麼

這次 first-pass audit 的重點不是「全部修掉」，而是先把最重要的風險正式記錄下來，讓之後討論 remediation 時有共同基準。

主要文件：

- [Security Audit 總覽](./security/README.md)
- [初次 Security Audit Report](./security/initial-audit-report.md)
- [Methodology 與 Scope](./security/methodology-and-scope.md)

## 目前最重要的 4 筆 finding

### FINDING-001：`/submit` 未做 server-side authentication 綁定

這是目前最值得先理解的風險。

問題不是前端有沒有帶 token，而是 backend 的 `/submit` route 沒有把 token 當成真正的 server-side 信任判斷依據。這會讓數位紀錄的完整性受到影響。

目前決策不是立刻開 remediation change，而是：

- 先把這件事正式記錄
- 先補**行政比對機制**
- 再由教師維護者與原始學生開發者討論後續是否改 auth flow

文件：

- [FINDING-001-submit-integrity-gap.md](./security/findings/FINDING-001-submit-integrity-gap.md)

### FINDING-002：`/admin/import-students` 缺少 server-side authorization

這條 route 可以批次覆寫學生帳號資料，但 route 本身沒有 admin-only gate。它的風險甚至比單筆選填更高，因為一旦被濫用，影響會擴散到登入、寄信與資料管理。

文件：

- [FINDING-002-unauthenticated-student-import.md](./security/findings/FINDING-002-unauthenticated-student-import.md)

### FINDING-003：token exposure 風險

登入後 token 會被寫進 `localStorage`，同時頁面允許 inline scripts。這代表只要未來出現 script injection 類型問題，token 被濫用的成本就會降低。

文件：

- [FINDING-003-client-side-token-exposure.md](./security/findings/FINDING-003-client-side-token-exposure.md)

### FINDING-004：CORS 過寬

這不是目前最急的問題，但它代表系統的信任邊界比實際需求更寬，後續若再增加更多管理功能，風險會放大。

文件：

- [FINDING-004-overly-permissive-cors.md](./security/findings/FINDING-004-overly-permissive-cors.md)

## 為什麼 `/submit` 目前先談行政比對機制？

這是這輪討論中很重要的共識。

短期來看，直接大改 authentication flow 不一定是最現實的第一步；但如果什麼都不做，教務處仍可能被錯誤的數位資料誤導。因此目前先建議補：

- 紙本與系統匯出名單的逐筆比對
- 差異紀錄
- 明確定義紙本與數位紀錄不一致時，以何者為準

這可以降低行政誤判，但不能消除技術風險。也就是說：

- 它是短期止血
- 不是長期最終解法

對應文件：

- [initial-audit-report.md](./security/initial-audit-report.md)
- [FINDING-001-submit-integrity-gap.md](./security/findings/FINDING-001-submit-integrity-gap.md)

## 如果你是原始學生開發者，建議你優先思考的問題

1. 哪些 route 現在只是「前端看起來有登入」，但 backend 其實沒有真正做 server-side gate？
2. `/submit` 若未來要補強，最小改動會是什麼？
3. `/admin/import-students` 為什麼會漏掉 admin-only protection？
4. 目前 token 放在 `localStorage`，未來若頁面功能變多，風險會不會更高？
5. 哪些 known gaps 是功能缺口，哪些是營運風險，哪些其實應該升級成 security finding？

## 如果你要繼續往下做

最合理的下一步通常會是以下其中一種：

- 先 archive 目前兩個完成的 Spectra changes
- 針對某一筆 high-severity finding 開 remediation change
- 先把行政比對機制寫成明確流程文件或 change proposal
- 回頭補某些功能缺口，例如不存在的 `/change-password`

## 這份摘要的定位

這份文件不是完整規格書，而是：

- 幫你快速進入狀況
- 告訴你現在哪些文件已經寫好
- 告訴你現在最需要重視的風險在哪裡

如果你要真正動手改程式，請不要只停在這份摘要；至少再回去讀：

- [system-architecture.md](./system-architecture.md)
- [api-and-data-model.md](./api-and-data-model.md)
- [security/initial-audit-report.md](./security/initial-audit-report.md)
