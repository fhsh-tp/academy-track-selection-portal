## Why

此專案即將上線，但目前缺少正式的 `docs/` 文件，系統知識主要散落在 source code 與少數開發者記憶中。若不先建立一套可交接、可追溯、適合學生與後續維護者閱讀的文件基線，專案上線後的維護成本與理解門檻都會偏高。

## What Changes

- 建立 `docs/` 的文件資訊架構與閱讀順序，讓讀者能從專案總覽一路讀到 subsystem 與營運細節。
- 撰寫專案目的、角色與主要流程、system architecture、backend / frontend 分工、API 與資料模型、environment variables、部署與營運流程、已知缺口與維護指引。
- 在 proposal、design、spec、tasks 與後續 `docs/` deliverables 中明確定義文件語言政策：一般敘述採台灣慣用繁體中文，technical terms 優先使用 English，嚴格禁止中國大陸用語；Spectra spec 維持 English normative language。
- 要求所有重要敘述都能對回具體 source evidence，例如 routes、source files、environment variables 與 trust boundaries。

## Non-Goals

- 本變更不包含 `docs/security/` 的正式 security audit 與 findings 清單；該工作由獨立 change 處理。
- 本變更不直接修補 application code、調整 production behavior 或修改紙本行政流程。
- 本變更不進行 dynamic testing、dependency upgrade 或 external service 替換。

## Capabilities

### New Capabilities

- `project-documentation-baseline`: 建立可交接、可追溯的專案文件集合，完整說明系統結構、流程、資料與營運資訊。
- `documentation-language-policy`: 建立本次文件輸出的語言與術語規範，確保台灣繁體中文與 English technical terms 的一致性。

### Modified Capabilities

(none)

## Impact

- Affected specs: `project-documentation-baseline`, `documentation-language-policy`
- Affected deliverables: `docs/`, `openspec/changes/establish-project-documentation-baseline/`
- Reviewed code surface:
  - `backend/main.py`
  - `backend/security.py`
  - `backend/database.py`
  - `backend/mailer.py`
  - `frontend/index.html`
  - `frontend/login.html`
  - `frontend/admin-login.html`
  - `frontend/choose.html`
  - `frontend/admin.html`
  - `frontend/config.js`
  - `import_students.py`
  - `requirements.txt`
