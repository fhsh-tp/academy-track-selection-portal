# FINDING-004 Overly permissive CORS configuration

## Metadata

- Status: Open
- Severity: Medium
- Category: OWASP A05 Security Misconfiguration
- Affected Areas:
  - `backend/main.py`

## Summary

FastAPI app 目前以 `allow_origins=["*"]`、`allow_credentials=True`、`allow_methods=["*"]`、`allow_headers=["*"]` 啟用 CORS middleware。這種設定過於寬鬆，容易放大跨來源請求的風險與維護判斷複雜度。

## Business / Administrative Impact

- 增加未來前端整合或第三方頁面誤用 API 的風險
- 降低維護者對「哪些來源本來就應該可呼叫」的可見度

## Source Evidence

- `backend/main.py:47-48`

## Risk Analysis

這個 finding 本身未必直接導致可利用漏洞，但它會讓系統的信任邊界比實際需求更寬。當專案之後新增更多管理功能或 token handling 邏輯時，這種 Security Misconfiguration 的成本會上升。

## Recommended Remediation

### 短期

- 在文件中明確記錄目前允許所有來源的事實與理由
- 盤點實際需要的 frontend origins

### 中期

- 將 `allow_origins` 收斂到實際使用的網站來源
- 重新評估 `allow_credentials=True` 是否必要

## Follow-up Owner

- 教師維護者
- 原始學生開發者
