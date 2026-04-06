---
id: FINDING-002
title: "JWT tokens persist in localStorage with unsafe-inline CSP"
severity: Medium
cwe: CWE-922
status: open
---

## Description

學生與管理員登入成功後都會把 JWT access token 寫入 `localStorage`，而主要頁面同時允許 inline scripts (`'unsafe-inline'`)。這種組合並不代表目前已經存在可利用的 XSS，但它明顯降低了未來 script injection 或第三方 script 失守時的攻擊門檻，因為 token 可被同頁腳本直接讀取。

## Evidence

- **File**: `frontend/login.html:4`
- **File**: `frontend/login.html:39`
- **File**: `frontend/admin-login.html:4`
- **File**: `frontend/admin-login.html:43`
- **File**: `frontend/choose.html:59`
- **File**: `frontend/choose.html:79`
- **File**: `frontend/admin.html:4`
- **File**: `frontend/admin.html:104`
- **File**: `frontend/admin.html:170`
- **File**: `frontend/admin.html:206`
- **Code**:
  ```html
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; ...">
  ```
  ```javascript
  localStorage.setItem('jwt_token', data.access_token);

  headers: {
      'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
  }
  ```
- **Explanation**: token 被儲存在任何同源 JavaScript 都可讀取的 browser storage，且 CSP 明確允許 inline scripts。只要後續出現 DOM-based XSS、被污染的外部 script、或其他 script injection 問題，攻擊者就能直接讀出並重放 bearer token。這不是單一頁面的 isolated 問題，而是登入、送出與管理流程都共用的 token handling pattern。

## Impact

一旦 token 外洩，攻擊者可模擬已登入學生提交選填結果，或以管理員身分存取 `/admin/all`、`/admin/import-students`、`/admin/send-reminders` 等受保護功能。管理員 token 外洩時，影響面會擴及所有學生資料與批次操作。

## Remediation

### Recommendation

把 access token 從 `localStorage` 移到較受控的儲存策略，例如 `HttpOnly`、`Secure`、`SameSite` cookie，並逐步移除 inline scripts，改用外部 script 檔與 nonces / hashes 收緊 CSP。若短期內無法改 storage 策略，至少先禁止 `'unsafe-inline'` 並減少前端可讀的高價值資訊。

### Before

```javascript
localStorage.setItem('jwt_token', data.access_token);
```

```html
<meta http-equiv="Content-Security-Policy"
      content="... script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; ...">
```

### After

```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,
    samesite="Strict",
)
```

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'nonce-<server-generated>';">
```

### References

- [CWE-922](https://cwe.mitre.org/data/definitions/922.html)
- [OWASP Top 10 A07:2021 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)
