# 文件寫作與用語政策

本文件定義這一輪 `docs/` 交付物的寫法，目標是讓後續維護者與學生閱讀時有一致的語感與術語。

## 語言原則

- 一般敘述使用台灣慣用繁體中文。
- technical terms 優先保留 English，例如 `authentication`、`authorization`、`token`、`route`、`deployment`、`localStorage`、`remediation`。
- 嚴格禁止中國大陸用語。
- Spectra `spec.md` 例外使用 English normative language，這是工具規格需求，不套用到一般 `docs/`。

## 建議保留 English 的 technical terms

以下術語除非有更清楚的既有寫法，否則優先保留 English：

- `backend`
- `frontend`
- `route`
- `request`
- `response`
- `payload`
- `token`
- `access token`
- `authentication`
- `authorization`
- `deployment`
- `environment variable`
- `database`
- `connection pool`
- `scheduler`
- `trust boundary`
- `source evidence`
- `known gaps`
- `operational risk`

## 常見禁用詞對照

下表左欄刻意列出「禁用示例」，目的是提醒後續撰寫時避開，不代表這些用語可在一般文件中使用。

| 避免使用 | 建議寫法 |
| --- | --- |
| 信息 | 資訊 |
| 接口 | 介面 |
| 配置 | 設定 |
| 日志 | 記錄 / log |
| 权限 / 許可權 | 權限 |
| 默認 | 預設 |
| 數據 | 資料 |
| 運維 | 維運 / 營運維護 |
| 調用 | 呼叫 |
| 併發 | 並行 / `concurrency` |

## File Reference 原則

本輪文件明確採用「file reference 為主，不放 screenshots」。

寫作時建議：

1. 每個重要章節都附上主要 source evidence。
2. 若能精確指出行號，優先標示行號。
3. 若要描述某個流程，至少同時引用 frontend 與 backend 對應檔案。
4. 若要描述 deployment / runtime 行為，需附上 environment variables 或 app lifecycle 的 source evidence。

## Known Gaps 分類原則

`docs/known-gaps.md` 固定分成兩類：

- **功能缺口**：會直接影響使用者流程或造成 UI / backend 不一致
- **營運風險**：會影響部署、維護、資料一致性或行政流程，但不一定立刻在 UI 爆出錯誤

Security finding 不在一般 known gaps 詳寫，應交由 `docs/security/` 追蹤。
