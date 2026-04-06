# FINDING-003 Client-side token exposure via `localStorage` and inline scripts

## Metadata

- Status: Open
- Severity: Medium
- Category: OWASP A07 Identification and Authentication Failures / Token Exposure
- Affected Areas:
  - `frontend/login.html`
  - `frontend/admin-login.html`
  - `frontend/admin.html`
  - `frontend/choose.html`

## Summary

登入成功後，學生與管理員的 JWT token 都被寫入 `localStorage`。同時，HTML 頁面使用 inline scripts，CSP 也允許 `'unsafe-inline'`。這種組合會提高未來一旦出現 script injection 類型問題時，token 被讀取與濫用的風險。

## Business / Administrative Impact

- 若 token 外洩，攻擊者可模擬已登入使用者操作受保護 endpoint
- 管理員 token 若外洩，影響面高於一般學生 token

## Source Evidence

- `frontend/login.html:38-45`
- `frontend/admin-login.html:43-45`
- `frontend/login.html:4`
- `frontend/admin-login.html:4`
- `frontend/admin.html:4`
- `frontend/choose.html:4`

## Risk Analysis

本 finding 並不表示系統已經存在可利用的 XSS；它記錄的是一種脆弱性放大條件。只要未來某個頁面出現 script injection，`localStorage` 內的 token 就很容易成為二次利用目標。

## Recommended Remediation

### 短期

- 在維護文件中明確標示 token 放在 `localStorage` 的風險
- 盡量避免新增更多 inline scripts

### 中期

- 評估是否改用更受控的 token storage 策略
- 收緊 CSP，逐步移除 `'unsafe-inline'`

## Follow-up Owner

- 教師維護者
- 原始學生開發者
