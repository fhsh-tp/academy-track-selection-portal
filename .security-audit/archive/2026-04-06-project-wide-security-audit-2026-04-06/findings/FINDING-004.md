---
id: FINDING-004
title: "Login endpoints lack brute-force throttling"
severity: Medium
cwe: CWE-307
status: open
---

## Description

`/login` 與 `/admin-login` 會直接驗證資料庫中的 password hash，失敗時立即回傳錯誤，但程式碼中沒有任何 failed-attempt tracking、延遲、lockout 或 rate limiting。這表示攻擊者可以持續對學生或管理員帳號做密碼猜測，而 backend 目前不會主動節流。

## Evidence

- **File**: `backend/main.py:89`
- **File**: `backend/main.py:100`
- **File**: `backend/main.py:112`
- **File**: `backend/main.py:125`
- **Code**:
  ```python
  @app.post("/login")
  async def login(data: LoginData):
      ...
      if not user or not verify_password(data.password, user['password']):
          raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

  @app.post("/admin-login")
  async def admin_login(data: LoginData):
      ...
      if not verify_password(data.password, user['password']):
          raise HTTPException(status_code=401, detail="帳號密碼錯誤")
  ```
- **Explanation**: 這兩條路徑都位於 network-reachable authentication boundary，卻沒有任何 request-rate control。只要攻擊者知道或猜到學號格式與管理員帳號名稱，就能連續嘗試大量密碼組合，風險會隨密碼品質與帳號清單可得性而上升。尤其管理員登入與一般登入都沒有分流的保護策略，表示高價值帳號也暴露在相同的暴力嘗試面前，而且目前程式碼中看不到任何 failed-attempt counter、固定延遲、temporary lockout 或異常告警。

## Impact

若學生或管理員使用弱密碼，攻擊者可透過自動化嘗試取得有效帳號。管理員帳號一旦被撞庫或暴力破解成功，將直接暴露所有學生資料與管理功能；一般學生帳號被接管則會影響個人選填紀錄與通知流程。

## Remediation

### Recommendation

在 authentication boundary 前加入速率限制與失敗次數追蹤，至少按來源 IP 與帳號識別做節流；對管理員登入再加上更嚴格的 lockout 或多因子驗證。若短期內無法引入完整帳號保護，也應先加入固定延遲與告警記錄。

### Before

```python
if not user or not verify_password(data.password, user['password']):
    raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
```

### After

```python
if limiter.too_many_attempts(key=f"login:{client_ip}:{data.student_id}"):
    raise HTTPException(status_code=429, detail="登入嘗試過多，請稍後再試")

if not user or not verify_password(data.password, user["password"]):
    limiter.record_failure(key=f"login:{client_ip}:{data.student_id}")
    raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
```

### References

- [CWE-307](https://cwe.mitre.org/data/definitions/307.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
