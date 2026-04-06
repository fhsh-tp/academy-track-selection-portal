---
id: FINDING-003
title: "Import route returns raw backend exception details"
severity: Medium
cwe: CWE-209
status: open
---

## Description

`/admin/import-students` 在例外處理中直接把 `str(e)` 放進 HTTP 500 回應的 `detail` 欄位。這條 route 雖然需要管理員權限，但一旦資料庫錯誤、欄位異常或編碼處理拋出內部訊息，client 端就能直接收到 backend 內部錯誤內容。

## Evidence

- **File**: `backend/main.py:269`
- **File**: `backend/main.py:273`
- **File**: `frontend/admin.html:178`
- **File**: `frontend/admin.html:179`
- **Code**:
  ```python
  except Exception as e:
      if conn:
          conn.rollback()
      print(f"❌ 匯入失敗: {str(e)}", flush=True)
      raise HTTPException(status_code=500, detail=str(e))
  ```
  ```javascript
  const err = await res.json();
  Swal.fire({ icon: 'error', title: '失敗', text: err.detail });
  ```
- **Explanation**: backend 內部例外字串可能包含資料庫欄位名稱、SQL constraint 名稱、檔案編碼細節或其他 implementation-specific 資訊。前端再把 `err.detail` 原樣顯示，會把這些訊息直接暴露給已登入管理員，增加後續攻擊或系統探測的資訊量。這類訊息通常不足以單獨入侵系統，但常被用來縮小攻擊面與加速 exploit tuning。

## Impact

這個問題本身不太可能單獨造成系統入侵，但它會洩漏內部 schema 或錯誤處理細節，讓後續攻擊者更容易針對 CSV import 流程做精準測試與 payload 調整。也會讓 production-facing UI 出現不受控的 backend 例外訊息。

## Remediation

### Recommendation

對 client 回傳通用錯誤訊息，並把詳細例外寫入受控的 server-side log。若需要追蹤事件，應使用 request ID 或匯入 job ID 讓操作人員可回查，而不是直接把原始例外傳給瀏覽器。

### Before

```python
raise HTTPException(status_code=500, detail=str(e))
```

### After

```python
request_id = uuid.uuid4().hex
logger.exception("Student import failed", extra={"request_id": request_id})
raise HTTPException(status_code=500, detail=f"學生匯入失敗，請聯絡管理員並提供事件編號 {request_id}")
```

### References

- [CWE-209](https://cwe.mitre.org/data/definitions/209.html)
- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
