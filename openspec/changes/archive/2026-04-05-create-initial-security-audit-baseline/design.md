## Context

目前專案尚未有任何正式 security audit artifact，但 source code 已可見多個需要被審慎追蹤的風險面，包括 authentication / authorization 邊界、frontend token storage、CORS / CSP 設定、資料匯入流程，以及未驗證即可提交任意學生選填結果的 `/submit` integrity gap。這些問題即使暫未修補，也不能只停留在口頭討論。

本次 change 的目標是建立第一次 security audit baseline，而不是立刻做 remediation。換句話說，這份 audit 必須讓後續讀者知道哪些地方被檢查過、怎麼分級、為何判定為風險、目前狀態是什麼，以及下一步應由誰討論或處理。

## Goals / Non-Goals

**Goals:**

- 在 `docs/security/` 建立第一次正式 security audit。
- 以 OWASP 導向的 finding model 記錄 scope、methodology、findings、severity、evidence、impact 與 remediation priority。
- 明確保留未解高風險問題的 status 與討論脈絡，避免它們被錯誤視為 accepted risk。
- 以台灣繁體中文與 English technical terms 撰寫 audit deliverables。

**Non-Goals:**

- 不在本 change 中修補 production code 或更改部署架構。
- 不在本 change 中進行 dynamic testing 或外部滲透測試。
- 不在本 change 中完成所有 remediation planning；必要時另開 change。

## Decisions

### 將 security audit deliverables 與一般專案文件分離

首次 audit 產出集中放在 `docs/security/`，與一般 `docs/` 文件分開。這樣可以清楚區分「系統如何運作」與「系統有哪些資安風險」，也便於後續單獨更新 findings。

替代方案是把 security 內容分散寫入一般 architecture 或 known gaps 文件。這會讓 audit scope 與 finding tracking 失去獨立性，因此不採用。

### 以 OWASP-oriented finding model 建立第一次 audit

每一筆 finding 都需要至少包含 category、severity、evidence、impact 與 remediation，分類優先對齊 OWASP 類別，必要時補充 CWE-style naming。這樣可以讓後續 remediation、討論與外部審查都有一致語彙。

替代方案是僅用自由敘述列出問題。這種方式難以比較優先順序，也不利於追蹤，因此不採用。

### 以 finding status 追蹤未修補的高風險問題

像 `/submit` 的 unauthenticated integrity gap 這類問題，即使暫未修補，也必須標示為 `Open` 或 `Deferred for discussion` 等明確狀態，並記錄 discussion context 與 follow-up owner。這能避免高風險問題在上線壓力下被默默忽略。

替代方案是把它們寫成一般備註或 known issue。這會削弱風險可見度，因此不採用。

### 以台灣繁體中文與 English technical terms 撰寫 audit deliverables

`docs/security/` 交付物採用台灣慣用繁體中文，technical terms 優先保留 English，例如 `authentication`、`authorization`、`integrity`、`severity`、`evidence`、`remediation`。嚴格禁止中國大陸用語，以維持校內讀者的一致理解。

替代方案是全面中文化或雙語化。前者易產生術語歧義，後者維護成本過高，因此不採用。

### 以 source evidence 支撐每一筆 finding

每一筆 finding 都必須對應到具體 source evidence，例如 route 行為、token handling、upload path、database write path 或設定值。這能確保 audit 不是主觀印象，而是能被複核的靜態審查結果。

替代方案是只保留結論摘要。這會讓後續開發者難以驗證或修補，因此不採用。

## Risks / Trade-offs

- [只有靜態 code review，沒有 runtime 驗證] → 在 methodology 與 finding 中明確標示本次 audit 的限制與信心邊界。
- [未修補高風險問題可能在上線前造成壓力] → 用 finding status、remediation priority 與 follow-up owner 把後續決策顯性化。
- [audit 寫得過於抽象，對學生幫助有限] → 每一筆 finding 都附上具體 source evidence 與業務影響，避免只有分類名稱。
- [用語不一致降低可讀性] → 交付前執行 terminology review，統一台灣繁體中文與 English technical terms。

## Migration Plan

1. 建立 `docs/security/` 的目錄結構與 audit 閱讀順序。
2. 定義 methodology、scope、reviewed areas 與 finding template。
3. 依現有 source code 完成第一次 findings 整理，包含 `/submit` integrity gap。
4. 執行 terminology review 與 findings consistency review。
5. 將 remediation 需求整理為後續討論或下一個 change。

## Open Questions

- 已於本次 apply 前確認：第一次 audit 完成後先不立即開 remediation change，先建立 baseline 與風險分析。
- 已於本次 apply 前確認：`/submit` 的 integrity 風險短期優先補行政比對機制，並在 audit 中完整說明其可降低與無法降低的風險。
