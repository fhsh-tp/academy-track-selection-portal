# Initial Audit Report

## Executive Summary

本輪審查共留下 4 項 active finding，其中 1 項為 High、3 項為 Medium。與 2026-04-05 baseline 相比，先前最嚴重的兩個 broken access control 問題已在目前程式碼中補上 server-side gate；同時，過去記錄的 wildcard CORS 也不再成立。現階段風險焦點轉移到 deployment defaults、browser 端 token handling、authentication hardening，以及 error disclosure。

本輪另行執行 locked dependency scan，結果未發現已知公開弱點。這表示風險主要來自專案自身的程式與組態決策，而不是目前鎖定的 Python 套件版本。

## Current Findings Summary

| ID | Title | Severity | Status | Supporting Artifact |
| --- | --- | --- | --- | --- |
| `FINDING-001` | Known default admin password in container defaults | High | Open | [FINDING-001](../../../.security-audit/active/project-wide-security-audit-2026-04-06/findings/FINDING-001.md) |
| `FINDING-002` | JWT tokens persist in localStorage with unsafe-inline CSP | Medium | Open | [FINDING-002](../../../.security-audit/active/project-wide-security-audit-2026-04-06/findings/FINDING-002.md) |
| `FINDING-003` | Import route returns raw backend exception details | Medium | Open | [FINDING-003](../../../.security-audit/active/project-wide-security-audit-2026-04-06/findings/FINDING-003.md) |
| `FINDING-004` | Login endpoints lack brute-force throttling | Medium | Open | [FINDING-004](../../../.security-audit/active/project-wide-security-audit-2026-04-06/findings/FINDING-004.md) |

## Legacy Findings Re-verification

| Legacy Finding | Result |
| --- | --- |
| `2026-04-05/FINDING-001` | Closed in current code |
| `2026-04-05/FINDING-002` | Closed in current code |
| `2026-04-05/FINDING-003` | Retained and rewritten as current `FINDING-002` |
| `2026-04-05/FINDING-004` | Closed in current code |

## Remediation Priorities

1. 先移除 `docker-compose.yml` 中可預測的 `ADMIN_PASSWORD` fallback，避免以已知密碼部署管理端。
2. 規劃 token handling 重構，將 JWT 從 `localStorage` 遷出，並同步收緊 CSP，移除 `'unsafe-inline'`。
3. 在 `/login` 與 `/admin-login` 前加入 rate limiting、failed-attempt tracking，對管理員登入採更嚴格保護。
4. 將 `/admin/import-students` 的 raw exception output 改成通用訊息與 request ID。

## Supporting Reports

- [report-tw.md](../../../.security-audit/active/project-wide-security-audit-2026-04-06/report-tw.md)
- [report-en.md](../../../.security-audit/active/project-wide-security-audit-2026-04-06/report-en.md)
- [methodology-and-scope.md](./methodology-and-scope.md)
- [dependency-vulnerability-scan.md](./dependency-vulnerability-scan.md)
