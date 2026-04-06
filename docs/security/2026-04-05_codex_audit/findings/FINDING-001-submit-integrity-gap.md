# FINDING-001 Unauthenticated `/submit` integrity gap

## Metadata

- Status: Deferred for discussion
- Severity: High
- Category: OWASP A01 Broken Access Control / Data Integrity
- Affected Areas:
  - `backend/main.py`
  - `frontend/choose.html`

## Summary

`/submit` route 會接受來自 client 的 `student_id`、`name`、`email`、`student_class_num` 與 `choice`，並直接把 `student_id` 與 `choice` 寫入 `selections`。雖然 frontend 會附帶 `Authorization` header，但 route 本身沒有宣告 `Depends(get_current_user)`，也沒有比對 token 中的使用者與 payload 中的 `student_id` 是否一致。

## Business / Administrative Impact

- 任何知道 endpoint 與 payload 格式的人，都可能寫入或覆蓋任意學生的數位選填結果
- 管理端匯出結果可能與學生實際紙本不一致
- 確認信可能寄到錯誤或被偽造的目標，造成學生與家長誤解
- 教務處若只看系統名單，可能做出錯誤行政判斷

## Source Evidence

- `backend/main.py:92-143`
- `backend/main.py:105-116`
- `frontend/choose.html:62-82`
- `frontend/choose.html:59-70`

## Risk Analysis

這個問題的核心不在於「有沒有 token」，而在於後端沒有把 token 當作 server-side trust decision 的依據。即使前端有登入流程，只要 route 自身不驗證，client-controlled payload 仍然可以改寫資料。

考量目前行政流程仍有紙本簽名與收件，這個 finding 不代表最終班群決定一定會被直接竄改成功；但它確實會破壞數位紀錄的可信度，並增加行政誤判、錯誤通知與後續對帳成本。

## Recommended Remediation

### 短期

先建立行政比對機制，而不是假設數位紀錄已可信：

- 在教務處收件流程中，逐筆比對紙本與系統匯出名單
- 以學號、班級座號、姓名、班群與收件狀態為最小比對欄位
- 建立差異處理紀錄，標示誰確認、何時確認、最後以何者為準

### 中期

- 在 `/submit` 補上 `Depends(get_current_user)`
- 改由 server side 從 token 決定 `student_id`
- 不再信任 client 送來的 `name`、`email`、`student_class_num` 作為權威來源

## Follow-up Owner

- 教師維護者
- 原始學生開發者
