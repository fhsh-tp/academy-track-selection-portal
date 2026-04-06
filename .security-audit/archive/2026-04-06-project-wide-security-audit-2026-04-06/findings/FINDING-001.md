---
id: FINDING-001
title: "Known default admin password in container defaults"
severity: High
cwe: CWE-1392
status: open
---

## Description

`docker-compose.yml` 為 `ADMIN_PASSWORD` 設定了可預測的 fallback 值 `admin_password_you_know_it`。啟動時，`backend/database.py` 會讀取這個環境變數並在資料庫中建立或保留 `admin` 帳號密碼雜湊。這代表只要維護者未在部署時覆寫該變數，系統就會以公開且固定的預設憑證對外提供管理員登入入口。

## Evidence

- **File**: `docker-compose.yml:31`
- **File**: `docker-compose.yml:32`
- **File**: `backend/database.py:61`
- **File**: `backend/database.py:62`
- **File**: `backend/database.py:63`
- **File**: `backend/database.py:64`
- **Code**:
  ```yaml
  # docker-compose.yml
  ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}
  ADMIN_PASSWORD: ${ADMIN_PASSWORD:-admin_password_you_know_it}
  ```
  ```python
  # backend/database.py
  admin_un = os.getenv("ADMIN_USERNAME")
  admin_pw = os.getenv("ADMIN_PASSWORD")
  if admin_pw:
      hashed_pw = get_password_hash(admin_pw)
      cur.execute(
          "INSERT INTO users (student_id, name, password, role) VALUES (%s, '管理員', %s, 'admin') ON CONFLICT DO NOTHING",
          (admin_un, hashed_pw,),
      )
  ```
- **Explanation**: deployment 預設值與帳號 bootstrap 直接串接在一起。當 `ADMIN_PASSWORD` 沒有被顯式設定時，backend 仍會接受固定字串作為真實管理員密碼來源，攻擊者只需知道公開 compose 檔或猜到常見預設值即可嘗試登入管理端。因為這個管理員帳號會被建立在正式登入流程中使用，所以問題不只是示範文件內的字串，而是實際可被套用的 runtime fallback。

## Impact

若系統以預設值啟動，攻擊者可使用已知密碼登入管理員入口，進一步讀取所有學生選填結果、批次覆寫學生帳號資料，並觸發提醒信寄送。這會同時影響資料機密性與完整性，且攻擊面直接暴露在 `/admin-login`。

## Remediation

### Recommendation

移除可預測的 `ADMIN_PASSWORD` fallback，並在啟動時對空值、預設值或過短值採取 fail-closed 行為。若系統必須自動建立管理員帳號，應要求部署流程顯式提供隨機高熵密碼，或改用一次性 bootstrap token。

### Before

```yaml
ADMIN_PASSWORD: ${ADMIN_PASSWORD:-admin_password_you_know_it}
```

### After

```yaml
ADMIN_PASSWORD: ${ADMIN_PASSWORD:?ADMIN_PASSWORD must be set to a unique secret}
```

```python
if not admin_pw or admin_pw in {"admin", "admin_password_you_know_it", "change-me"}:
    raise RuntimeError("Refusing to bootstrap admin account with an unsafe default password")
```

### References

- [CWE-1392](https://cwe.mitre.org/data/definitions/1392.html)
- [OWASP Top 10 A05:2021 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
