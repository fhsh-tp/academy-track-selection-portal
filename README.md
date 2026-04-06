# Academy Track Selection Portal　學制選組系統

> 高一升高二班群選填平台

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-ECL--2.0-green)](./LICENSE)

---

## 目錄

- [專案說明](#專案說明)
- [功能特色](#功能特色)
- [系統架構](#系統架構)
- [技術棧](#技術棧)
- [快速開始](#快速開始)
- [環境變數設定](#環境變數設定)
- [專案結構](#專案結構)
- [文件](#文件)
- [貢獻](#貢獻)

---

## 專案說明

本系統用於支援高一升高二普通班學生進行班群選填作業。學生登入後選擇志願班群，系統自動將結果寫入資料庫、產生 PDF 確認表，並寄送確認 email 給學生。管理員可透過後台儀表板匯入名單、查詢進度、匯出 CSV，以及對尚未選填的學生寄送提醒信。

**目前選填班群選項：**

| 代碼 | 班群名稱 |
|:---:|--------|
| 1 | 文法商（數A課程路徑） |
| 2 | 文法商（數B課程路徑） |
| 3 | 理工資 |
| 4 | 生醫農 |

---

## 功能特色

**學生端**
- 學號 + 密碼登入，JWT 授權保護
- 單一班群選填，支援截止日期顯示
- 選填完成後自動產生 PDF 確認表並以 email 附件寄出
- 曾選填者重新登入可查看已填選項

**管理員端**
- 獨立管理後台（`/admin-login`）
- 檢視所有學生選填狀態，含未選填人數統計
- 一鍵匯出 CSV（支援 Excel 開啟）
- CSV 批次匯入學生名單（支援 Big5 與 UTF-8 編碼）
- 一鍵寄送催填提醒信給尚未選填的學生

---

## 系統架構

```
                ┌─────────────────────┐
  Browser ───▶  │   Nginx (Reverse    │
                │   Proxy / Static)   │
                └─────────┬───────────┘
                          │
                ┌─────────▼───────────┐
                │   FastAPI Backend   │
                │   (Port 8000)       │
                └─────────┬───────────┘
                          │
                ┌─────────▼───────────┐
                │   PostgreSQL 16     │
                └─────────────────────┘

                Cloudflare Tunnel（可選）
                DBGate GUI（可選）
```

詳細說明請參閱 [`docs/system-architecture.md`](./docs/system-architecture.md)。

---

## 技術棧

| 層級 | 技術 |
|-----|------|
| Backend | Python 3.12+、FastAPI、Gunicorn |
| 資料庫 | PostgreSQL 16 |
| 驗證 | JWT（python-jose）、bcrypt |
| 郵件 | aiosmtplib + Google Workspace SMTP Relay |
| PDF 產生 | ReportLab（含 TW-Kai 字型） |
| 前端 | 靜態 HTML5 + Vanilla JavaScript |
| 容器化 | Docker、Docker Compose |
| Reverse Proxy | Nginx |
| Package 管理 | [uv](https://docs.astral.sh/uv/) |

---

## 快速開始

### 先決條件

- [Docker](https://docs.docker.com/get-docker/) 26+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+

### 1. 複製專案

```bash
git clone https://github.com/fhsh-projects/academy-track-selection-portal.git
cd academy-track-selection-portal
```

### 2. 建立環境變數

```bash
cp .env.example .env
```

開啟 `.env`，至少填入以下必要欄位（詳見[環境變數設定](#環境變數設定)）：

```dotenv
SECRET_KEY=<至少 32 字元的隨機字串>
ADMIN_PASSWORD=<管理員密碼>
DEADLINE_DATE=2026-05-04 23:59:59+0800
```

### 3. 啟動服務

```bash
docker compose up -d
```

服務啟動後：

| 服務 | URL |
|------|-----|
| 學生入口 | http://localhost |
| 管理後台 | http://localhost/admin-login |
| API 文件 | http://localhost/docs |

### 4. 匯入學生名單

準備 CSV 檔案（欄位：`student_id,name,email,student_class_num`），在管理後台 > 匯入學生名單上傳。

> **注意：** CSV 支援 UTF-8（含 BOM）與 Big5 編碼，第一列須為標頭行。

### 可選：啟用 DBGate（資料庫 GUI）

```bash
docker compose --profile dbgate up -d
```

開啟 http://localhost:8080 即可使用 DBGate 管理資料庫。

### 可選：啟用 Cloudflare Tunnel

在 `.env` 設定 `TUNNEL_TOKEN` 後：

```bash
docker compose --profile tunnel up -d
```

### 本機開發（不使用 Docker）

需先安裝 [uv](https://docs.astral.sh/uv/)：

```bash
# 安裝相依套件
uv sync

# 啟動開發伺服器（支援 hot reload）
uv run fastapi dev backend/main.py
```

---

## 環境變數設定

完整範本請參閱 [`.env.example`](./.env.example)。

| 變數 | 必填 | 說明 |
|------|:----:|------|
| `DATABASE_URL` | ✓ | PostgreSQL 連線字串 |
| `DB_SSLMODE` | ✓ | SSL 模式（`prefer` / `require`） |
| `SECRET_KEY` | ✓ | JWT 簽名金鑰（至少 32 字元） |
| `ADMIN_USERNAME` | ✓ | 管理員帳號 |
| `ADMIN_PASSWORD` | ✓ | 管理員密碼 |
| `DEADLINE_DATE` | ✓ | 選填截止時間（`YYYY-MM-DD HH:MM:SS+0800`） |
| `SMTP_HOST` | ✓ | SMTP 伺服器位址 |
| `SMTP_PORT` | ✓ | SMTP 埠號（通常為 `587`） |
| `SMTP_USER` | ✓ | SMTP 登入帳號 |
| `SMTP_PASSWORD` | ✓ | SMTP 密碼或 App Password |
| `SMTP_FROM_NAME` |  | 寄件者顯示名稱 |
| `FASTAPI_APP_ENVIRONMENT` |  | `prod` 或留空（開發模式） |
| `PROD_DOMAIN` |  | 正式域名，用於 CORS 設定 |
| `API_BASE_URL` |  | 前端 API 基礎 URL（同域 proxy 可留空） |
| `TUNNEL_TOKEN` |  | Cloudflare Tunnel Token |
| `TUNNEL_TRANSPORT_PROTOCOL` |  | Tunnel 傳輸協定（`auto` / `quic` / `http2`） |

---

## 專案結構

```
academy-track-selection-portal/
├── backend/                    # FastAPI 應用程式
│   ├── main.py                 # 所有 API routes
│   ├── database.py             # PostgreSQL 連線池與 schema 初始化
│   ├── security.py             # JWT 與 bcrypt 處理
│   ├── mailer.py               # PDF 產生與 SMTP 郵件發送
│   ├── static/                 # TW-Kai 字型（PDF 用）
│   └── utils/
│       ├── email.py            # Email 範本格式化
│       └── dependencies.py     # FastAPI 相依性工具
├── frontend/                   # 靜態頁面
│   ├── index.html              # 首頁
│   ├── login.html              # 學生登入
│   ├── choose.html             # 班群選填
│   ├── admin-login.html        # 管理員登入
│   ├── admin.html              # 管理後台
│   └── static/
│       ├── config.js           # API_BASE_URL 設定
│       └── style.css           # 全域樣式
├── docs/                       # 技術文件
├── nginx/                      # Nginx 設定
├── scripts/
│   ├── docker-entrypoint.sh    # Docker 啟動腳本
│   └── buildx.sh               # 多平台 Docker 建置腳本
├── import_students.py          # 獨立執行的 CSV 匯入腳本
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── .env.example
```

---

## 文件

詳細技術文件位於 [`docs/`](./docs/) 目錄：

| 文件 | 說明 |
|------|------|
| [專案總覽](./docs/project-overview.md) | 目標、使用者角色、主要流程 |
| [系統架構](./docs/system-architecture.md) | 組件圖、Trust Boundary、啟動流程 |
| [API 與資料模型](./docs/api-and-data-model.md) | 所有 API routes、Request/Response、DB schema |
| [前後端模組對照](./docs/backend-frontend-reference.md) | 頁面 ↔ Route ↔ 模組對應關係 |
| [營運與維護](./docs/operations-and-maintenance.md) | 部署 Checklist、日常維護、故障排除 |
| [已知缺口](./docs/known-gaps.md) | 功能缺口與潛在風險彙整 |
| [新手閱讀指南](./docs/student-reading-guide.md) | 接手維護的快速入門 |

---

## 貢獻

本專案由復興高中學生開發與維護。若你是接手的學弟妹，請先閱讀[新手閱讀指南](./docs/student-reading-guide.md)。

1. Fork 本 Repository
2. 建立 Feature Branch：`git checkout -b feat/your-feature`
3. Commit 你的變更
4. 開 Pull Request，並在描述中說明變更原因

---

**臺北市立復興高級中學**　© 2026　[ECL-2.0 License](./LICENSE)
