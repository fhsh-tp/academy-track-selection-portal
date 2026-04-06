# FINDING-002 Unauthenticated student import route

## Metadata

- Status: Open
- Severity: High
- Category: OWASP A01 Broken Access Control
- Affected Areas:
  - `backend/main.py`
  - `frontend/admin.html`

## Summary

`/admin/import-students` 這個 route 會接受 CSV 檔案並 upsert `users` 資料表中的學生資料與 password，但 route 本身沒有宣告 `Depends(get_current_user)`，也沒有做 `role == admin` 的 server-side gate。

## Business / Administrative Impact

- 未授權呼叫可能新增或覆寫學生帳號資料
- 可能重設學生 password、email 與班級座號
- 一旦資料被污染，後續登入、通知與行政流程都會受到影響

## Source Evidence

- `backend/main.py:168-227`
- `backend/main.py:201-214`
- `frontend/admin.html:166-170`

## Risk Analysis

這是一條高風險的資料寫入面，因為它不只是改單一欄位，而是可批次覆寫多名學生的敏感帳號資料。相較於 `FINDING-001`，這條 route 的攻擊面更偏向管理功能濫用，且一旦被利用，後續影響會擴散到登入、寄信與名單管理。

## Recommended Remediation

### 短期

- 在營運流程上限制只有特定維護者可執行學生匯入
- 保存每次 CSV 匯入檔案與匯入時間，方便事後比對

### 中期

- 為 `/admin/import-students` 加上 `Depends(get_current_user)`
- 在 route 內強制檢查 `role == admin`
- 若可能，再加入匯入操作 log

## Follow-up Owner

- 教師維護者
- 原始學生開發者
