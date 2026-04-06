# 初次 Security Audit Report

## Executive Summary

本次 review 顯示，專案已具備基本的 password hashing 與 JWT token 機制，但 server-side authorization 落點不一致，導致至少兩條高風險路徑仍可被未授權呼叫。最重要的風險不是單一程式錯字，而是「前端帶了 token，不代表後端真的有驗證」這個 trust boundary 被多處誤用。

整體來看，本次 first-pass audit 建議把後續工作拆成兩條線：

1. 先建立清楚的行政比對機制與例外處理流程，降低資料被錯填、誤匯入或錯誤通知時的行政衝擊
2. 再由教師維護者與原始學生開發者討論是否進一步做 server-side remediation

依照目前 source evidence，本輪共記錄 4 筆 finding。

## Severity Summary

| Severity | 數量 | 說明 |
| --- | --- | --- |
| High | 2 | 未授權資料寫入與帳號資料覆寫 |
| Medium | 2 | token exposure 與過寬 CORS 增加攻擊面 |
| Low | 0 | 本輪未單獨列 Low finding |

## Findings Summary

| ID | Title | Severity | Status | 重點 |
| --- | --- | --- | --- | --- |
| `FINDING-001` | Unauthenticated `/submit` integrity gap | High | Deferred for discussion | 可寫入任意學生選填結果，需先補行政比對機制 |
| `FINDING-002` | Unauthenticated student import route | High | Open | `/admin/import-students` 缺少 server-side authorization |
| `FINDING-003` | Client-side token exposure via `localStorage` and inline scripts | Medium | Open | token 放在 `localStorage`，且 CSP 允許 inline scripts |
| `FINDING-004` | Overly permissive CORS configuration | Medium | Open | `allow_origins=["*"]` 與 `allow_credentials=True` 過寬 |

個別 finding 檔案：

- [FINDING-001-submit-integrity-gap.md](./findings/FINDING-001-submit-integrity-gap.md)
- [FINDING-002-unauthenticated-student-import.md](./findings/FINDING-002-unauthenticated-student-import.md)
- [FINDING-003-client-side-token-exposure.md](./findings/FINDING-003-client-side-token-exposure.md)
- [FINDING-004-overly-permissive-cors.md](./findings/FINDING-004-overly-permissive-cors.md)

## Primary Risk Narrative

### 1. Broken Access Control 是本系統目前最重要的風險

`/submit` 與 `/admin/import-students` 這兩條路徑都涉及資料寫入，但 route 本身沒有一致地以 `Depends(get_current_user)` 作為 server-side gate。這代表系統表面上有登入機制，實際上仍有高風險寫入面未被完整保護。

source evidence:

- `backend/main.py:92-143`
- `backend/main.py:168-227`
- `backend/main.py:145-147`
- `backend/main.py:230-233`

### 2. Browser 端 token handling 放大了前端受攻擊時的影響面

學生與管理員登入後，token 都被存進 `localStorage`。同時，HTML 頁面使用 inline scripts，CSP 也允許 `'unsafe-inline'`。只要未來出現 script injection 類型的問題，token 被讀出的風險就會升高。

source evidence:

- `frontend/login.html:38-45`
- `frontend/admin-login.html:43-45`
- `frontend/login.html:4`
- `frontend/admin.html:4`
- `frontend/choose.html:4`

## Immediate Recommendation

### 不先開 remediation change

依使用者指示，本輪先不直接開 remediation change，而是先建立正式 baseline 與風險分析。

### `/submit` 優先措施：先補行政比對機制

對 `FINDING-001`，短期建議不是立刻大改 authentication flow，而是先建立行政比對機制，例如：

- 教務處收紙本時，建立紙本與 database 匯出名單的逐筆比對清單
- 對比欄位至少包含學號、班級座號、姓名、班群、收件狀態
- 若發現紙本與系統記錄不一致，明確定義以何者為 authoritative source
- 保留差異紀錄，供後續追查是否屬於誤填、代填或系統行為問題

### 行政比對機制的風險分析

行政比對機制能降低以下風險：

- 管理端匯出名單誤導行政判斷
- 學生實際紙本與系統紀錄不一致時無法追查
- 教師誤以為 email 確認信代表資料已可信

但它**不能**消除以下風險：

- 未授權呼叫仍可改寫數位紀錄
- 寄出的確認信仍可能誤導學生或家長
- 管理端在紙本收齊前仍可能看到不可信的數位資料

因此，行政比對機制是短期止血，不是長期 remediation 終點。

## Follow-up Recommendation

建議後續與原始學生開發者討論：

1. 是否為 `/submit` 補上真正的 server-side authentication 與 `student_id` 綁定
2. 是否為 `/admin/import-students` 補上 admin-only gate
3. 是否改寫 token handling 與 CSP policy
4. 是否把 high-severity findings 各自拆成 remediation changes
