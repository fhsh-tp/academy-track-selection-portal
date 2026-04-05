# Academy Track Selection Portal 文件總覽

本目錄提供此專案的第一版正式文件，目標是讓教師維護者、原始學生開發者與後續接手的學生，能在不先通讀全部 source code 的前提下，快速理解系統的用途、流程、結構、資料與營運注意事項。

## 建議閱讀順序

1. [學生導讀版摘要](./student-reading-guide.md)
2. [專案總覽](./project-overview.md)
3. [系統架構](./system-architecture.md)
4. [前後端與模組對照](./backend-frontend-reference.md)
5. [API 與資料模型](./api-and-data-model.md)
6. [部署、營運與維護](./operations-and-maintenance.md)
7. [已知缺口](./known-gaps.md)
8. [文件寫作與用語政策](./writing-policy.md)

## 這份文件集回答什麼問題

- 這個系統的核心目的與行政流程是什麼？
- 學生與管理員各自會走什麼流程？
- FastAPI backend、靜態 frontend、PostgreSQL 與 Brevo 的責任邊界是什麼？
- 目前有哪些 API routes、資料表、environment variables 與外部整合？
- 如果要維護、部署或交接，應先看哪些檔案？
- 目前有哪些功能缺口與營運風險？

## 不包含的內容

- 正式 security audit findings 與 severity 分級
- Production code remediation
- UI screenshots

本輪文件採用「file reference 為主」的做法，而不是 screenshots。涉及 security 的正式 finding，會由獨立 change `create-initial-security-audit-baseline` 建立在 `docs/security/`。

## Source Evidence 原則

本文件集的每個主要章節都盡量附上 source evidence。閱讀文件時，若需要追到實作，請優先回看以下檔案：

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
- `.spectra.yaml`

## 文件地圖

| 文件 | 主要用途 |
| --- | --- |
| [student-reading-guide.md](./student-reading-guide.md) | 提供學生與新接手維護者的快速導讀，整理文件與 security audit 的重點 |
| [project-overview.md](./project-overview.md) | 說明專案目的、使用者角色、主要行政流程與閱讀入口 |
| [system-architecture.md](./system-architecture.md) | 說明系統組件、資料流、trust boundaries 與啟動流程 |
| [backend-frontend-reference.md](./backend-frontend-reference.md) | 對照 backend 模組、frontend 頁面與 routes 的責任分工 |
| [api-and-data-model.md](./api-and-data-model.md) | 整理 API surface、request/response、資料表與 environment variables |
| [operations-and-maintenance.md](./operations-and-maintenance.md) | 說明部署、日常營運、匯入、提醒信與維護建議 |
| [known-gaps.md](./known-gaps.md) | 區分功能缺口與營運風險，方便後續開 change 追蹤 |
| [writing-policy.md](./writing-policy.md) | 定義台灣繁體中文與 English technical terms 的寫法與 file reference 原則 |
