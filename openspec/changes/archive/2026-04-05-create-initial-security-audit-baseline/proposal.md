## Why

此專案即將上線，但目前尚未建立第一份正式的 security audit。已知高風險問題如果沒有被系統化地記錄 scope、evidence、severity、impact、status 與 remediation priority，後續就容易在討論與交接中失去脈絡，尤其是不應被默默視為 accepted risk 的問題。

## What Changes

- 建立 `docs/security/` 的第一次 security audit，明確定義 review scope、methodology、threat model、reviewed code areas、findings summary 與 remediation priority。
- 以 OWASP 導向的 finding 結構記錄 category、severity、evidence、impact、recommended remediation 與 follow-up status。
- 將 `/submit` 未做 server-side authentication 的 integrity gap 與其他未解高風險問題正式列為 findings，明確標示為待討論或待修補，而不是 accepted risk。
- 規定 `docs/security/` 交付物採台灣慣用繁體中文，technical terms 優先使用 English，嚴格禁止中國大陸用語。

## Non-Goals

- 本變更不直接修補 application code、變更 auth flow 或調整部署設定。
- 本變更不進行 dynamic penetration testing、dependency upgrade 或 infra hardening。
- 本變更不取代後續 remediation change；本變更只負責建立 audit baseline 與 findings 追蹤脈絡。

## Capabilities

### New Capabilities

- `initial-security-audit-baseline`: 建立第一次 security audit 與 findings 追蹤基線，完整記錄 methodology、分類、證據、狀態與 remediation priority。

### Modified Capabilities

(none)

## Impact

- Affected specs: `initial-security-audit-baseline`
- Affected deliverables: `docs/security/`, `openspec/changes/create-initial-security-audit-baseline/`
- Reviewed code surface:
  - `backend/main.py`
  - `backend/security.py`
  - `backend/database.py`
  - `backend/mailer.py`
  - `frontend/login.html`
  - `frontend/admin-login.html`
  - `frontend/choose.html`
  - `frontend/admin.html`
  - `frontend/config.js`
  - `import_students.py`
  - `requirements.txt`
