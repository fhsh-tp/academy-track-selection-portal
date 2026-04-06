# 2026-04-06 Security Audit Baseline

本目錄收錄 2026-04-06 針對目前專案程式碼狀態完成的 security audit baseline。這一版延續 `docs/security/<date>_codex_audit/` 命名，作為對維護者與利害關係人的 published summary；實際 working artifacts 與完整 finding lifecycle 則維持在 `.security-audit/active/project-wide-security-audit-2026-04-06/`。

## 建議閱讀順序

1. [initial-audit-report.md](./initial-audit-report.md)
2. [methodology-and-scope.md](./methodology-and-scope.md)
3. [dependency-vulnerability-scan.md](./dependency-vulnerability-scan.md)

## Published Artifacts

| 檔案 | 用途 |
| --- | --- |
| [initial-audit-report.md](./initial-audit-report.md) | 執行摘要、finding 摘要、舊 finding 重新驗證結果、修復優先順序 |
| [methodology-and-scope.md](./methodology-and-scope.md) | 說明本輪範圍、threat model、review 類別與 supporting evidence |
| [dependency-vulnerability-scan.md](./dependency-vulnerability-scan.md) | 記錄 locked dependency scan 的命令、限制與結果 |

## Supporting OWASP Audit Artifacts

- [scope.md](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/scope.md)
- [plan.md](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/plan.md)
- [tasks.md](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/tasks.md)
- [report-en.md](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/report-en.md)
- [report-tw.md](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/report-tw.md)
- [FINDING-001](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/findings/FINDING-001.md)
- [FINDING-002](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/findings/FINDING-002.md)
- [FINDING-003](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/findings/FINDING-003.md)
- [FINDING-004](../../../.security-audit/archive/project-wide-security-audit-2026-04-06/findings/FINDING-004.md)

## 與 2026-04-05 baseline 的關係

上一版 baseline 位於 [../2026-04-05_codex_audit](../2026-04-05_codex_audit)。本輪不是直接沿用舊結論，而是對目前 branch / commit 重新 review；因此這一版同時包含：

- 已關閉的舊 finding 重新驗證結果
- 仍成立但需要改寫的 finding
- 新增的 deployment / error-handling / auth hardening finding
