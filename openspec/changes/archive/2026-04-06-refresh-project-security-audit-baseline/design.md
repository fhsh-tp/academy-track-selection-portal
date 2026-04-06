## Context

專案目前已有 `docs/security/2026-04-05_codex_audit/` 作為 first-pass audit baseline，但這批文件是一次性輸出，沒有對應的 lifecycle workspace，也缺少可持續追蹤的 `scope`、`plan`、`tasks`、`findings` 與 archive 狀態。另一方面，repository 目前的實際程式碼已包含 FastAPI backend、PostgreSQL、JWT authentication、CSV import、SMTP/PDF 流程、static frontend、Nginx 反向代理與 Docker deployment files，review 範圍比舊 baseline 文件更廣，且部分舊 finding 的前提已經改變。

本 change 的設計目標不是直接修補漏洞，而是建立一個以 current repository state 為準的安全稽核骨架，讓後續 `owasp:review`、`owasp:report` 與 `docs/security/` 發布工作能用一致的資料來源往下走。

## Goals / Non-Goals

**Goals:**

- 在 repository 內建立正式的 OWASP audit lifecycle，讓進行中的 audit 不再散落在臨時文件或口頭結論中。
- 以目前 branch / commit 的實際 attack surface 為準，重新定義 audit boundaries、threat model、review categories 與 actionable tasks。
- 讓 `docs/security/` 的 published baseline 能追溯到對應的 OWASP audit artifacts，而不是只保留一次性的初始報告。
- 保留與 2026-04-05 baseline 的關聯，但把它降級為 historical input，而不是最新 truth source。

**Non-Goals:**

- 不在本 change 內修補 route authorization、token storage、CSP、CORS、SMTP 設定或 deployment secrets。
- 不把 dynamic testing、平台權限盤點或第三方 SaaS 帳號審核納入本輪 deliverables。
- 不把 `.security-audit/` 內容自動公開成 production-facing 文件；published report 仍由 `docs/security/` 承擔。

## Decisions

### Use the OWASP audit workspace as the source of truth for in-progress review state

進行中的 audit 以 `.security-audit/active/project-wide-security-audit-2026-04-06/` 為唯一 truth source，至少包含 `.audit.yaml`、`scope.md`、`plan.md`、`tasks.md`，後續 findings 與報告也沿用同一 lifecycle。這樣可以把「目前 review 到哪裡、哪些 finding 已建立、哪些項目仍待檢查」從靜態文件中分離出來，避免每次更新都必須重寫整份 published report。

Alternative considered: 直接在 `docs/security/` 持續追加 Markdown 文件。Rejected，因為 `docs/security/` 適合對外發布的穩定輸出，不適合追蹤進行中的 review 狀態、pending items 與 archive lifecycle。

### Re-audit the current repository state instead of inheriting the 2026-04-05 conclusions

舊 baseline 仍是重要輸入，但新 audit 的 boundaries、threat model 與 review checklist 必須直接對應目前的 `backend/`、`frontend/`、`nginx/`、Docker 與 dependency manifests。像 `/submit` 與 `/admin/import-students` 目前已經掛上 `Depends(get_current_user)`，代表舊 finding 不應直接被複製，而要重新驗證後再決定是否保留、降級、關閉或改寫。

Alternative considered: 直接把 2026-04-05 文件搬進新的 audit 目錄。Rejected，因為那會把舊結論與新程式碼混在一起，失去 full-project re-audit 的意義。

### Split internal audit artifacts from published security baseline documentation

`.security-audit/` 負責 lifecycle 與 working materials，`docs/security/` 負責 published baseline、executive summary 與讀者導向的 findings index。這個分工讓 review 階段可持續增補證據，同時保留對維護者與利害關係人的穩定閱讀入口。

Alternative considered: 僅保留 `.security-audit/`，不再更新 `docs/security/`。Rejected，因為既有 spec 已要求在 `docs/security/` 發布 security audit，且維護者現有文件閱讀路徑也集中在 `docs/`。

### Organize review categories by attack surface and trust boundary

本輪 audit 不只按檔案夾切分，而是依 attack surface 與 trust boundary 建立 review 類別，例如 authentication、authorization、session/token handling、input/file handling、configuration/deployment、data protection 與 operational flows。這能避免單一檔案同時橫跨多種風險時被錯誤地歸成單一類別，也能讓 checklist 直接映射到 OWASP review methodology。

Alternative considered: 只按 `backend/`、`frontend/`、`deployment/` 做三大任務群組。Rejected，因為這種切法不利於追蹤跨層問題，例如 client-controlled token data、proxy 與 backend trust boundary、或 configuration 與 authorization 的交互影響。

## Risks / Trade-offs

- [Audit artifacts may expose sensitive findings if committed broadly] → 在 scope 與 proposal 中明確標示 `.security-audit/` 的用途，並提醒維護者決定是否加入 `.gitignore` 或改採受控發布流程。
- [Historical findings may conflict with current code] → 在 plan 與 tasks 中加入重新驗證既有 finding 狀態的步驟，避免直接沿用舊 severity 與結論。
- [Full-project scope may become too broad for one review pass] → 以 OWASP category-based tasks 拆分 review sessions，並在 tasks 中保留逐類別完成與回填 findings 的節奏。
- [Published baseline can drift from working audit artifacts] → 要求 `docs/security/` 的刷新輸出引用對應 audit name、date 與 supporting artifacts，降低文件漂移。

## Migration Plan

1. 建立新的 Spectra change 與 `.security-audit/active/project-wide-security-audit-2026-04-06/` workspace。
2. 依目前 repository state 撰寫 `scope.md`、`plan.md`、`tasks.md`，作為 review 階段的入口。
3. 執行 `owasp:review` 產生 findings，並在需要時回寫 task completion 狀態。
4. 產出更新後的 published baseline 到 `docs/security/`，使其引用本輪 audit 的實際 evidence 與 finding status。
5. review/report 完成後，將 audit 轉入 archive，保留可追溯歷史。

## Open Questions

- 本階段沒有未解的 open question。已決定將 `.security-audit/` 作為 version-controlled 的 working source of truth，讓 active 與 archived audit 都可被追溯。
- Published baseline 將延續 `docs/security/<date>_codex_audit/` 命名，以維持與既有文件集一致的閱讀路徑。
- Dependency vulnerability scanning 將納入本輪 audit methodology 與報告章節，作為對 source review 的補充證據，而不是獨立替代品。
