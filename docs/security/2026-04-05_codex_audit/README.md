# Security Audit 總覽

本目錄收錄此專案的第一次正式 security audit。目的不是立刻修補所有問題，而是把目前已辨識的風險、證據、影響、優先順序與後續討論方向完整記錄下來，讓教師維護者與原始學生開發者能在同一個基準上討論。

## 建議閱讀順序

1. [初次 security audit report](./initial-audit-report.md)
2. [Methodology 與 Scope](./methodology-and-scope.md)
3. [Finding Template](./finding-template.md)
4. `findings/` 目錄下的個別 finding

## 目錄內容

| 檔案 | 用途 |
| --- | --- |
| [initial-audit-report.md](./initial-audit-report.md) | Executive summary、severity 分布、主要風險與優先處理建議 |
| [methodology-and-scope.md](./methodology-and-scope.md) | 說明 audit boundaries、reviewed code areas、threat model 與方法 |
| [finding-template.md](./finding-template.md) | 定義後續 finding 應維持的欄位格式 |
| `findings/FINDING-001-submit-integrity-gap.md` | `/submit` 未做 server-side authentication 的高風險 integrity 問題 |
| `findings/FINDING-002-unauthenticated-student-import.md` | `/admin/import-students` 缺少 server-side authorization 的高風險問題 |
| `findings/FINDING-003-client-side-token-exposure.md` | `localStorage` token 與 inline script surface 帶來的 token exposure 風險 |
| `findings/FINDING-004-overly-permissive-cors.md` | 過寬 CORS 設定造成的攻擊面放大 |

## 本輪 audit 的邊界

- 以 static code review 為主
- 未進行 dynamic penetration testing
- 未進行 dependency vulnerability scanning
- 未對外部服務帳號權限做獨立稽核

## 用語與狀態約定

- 一般說明採台灣慣用繁體中文
- technical terms 優先保留 English
- 狀態欄位目前使用：
  - `Open`
  - `Deferred for discussion`
  - `Closed`

## 與一般文件的關係

若要先理解系統如何運作，再回來看 security finding，建議先讀：

- [專案總覽](../project-overview.md)
- [系統架構](../system-architecture.md)
- [API 與資料模型](../api-and-data-model.md)
- [已知缺口](../known-gaps.md)
