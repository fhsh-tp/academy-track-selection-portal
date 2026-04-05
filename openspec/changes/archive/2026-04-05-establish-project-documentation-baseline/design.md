## Context

專案目前以 FastAPI backend 搭配靜態 HTML/CSS/JavaScript frontend 運作，核心行為集中在少數 source files 中，但 `docs/` 尚未建立正式文件。這代表後續維護者與學生若要理解 authentication、選填流程、管理端流程、資料表、外部郵件整合或部署設定，只能直接進入 source code。

本次 change 的核心不是新增功能，而是建立一套可閱讀、可交接、可追溯的文件基線。由於主要讀者同時包含教師維護者與學生，因此文件必須兼顧 onboarding 友善度與技術準確度，避免只做成零散筆記或過度抽象的摘要。

## Goals / Non-Goals

**Goals:**

- 建立適合後續維護與學生理解的 `docs/` 文件集合。
- 讓讀者可以從高階總覽一路追到 subsystem、資料流、API、部署與營運資訊。
- 明確要求所有重要說明都能回溯到實際 source evidence。
- 以台灣繁體中文與 English technical terms 作為本次文件的寫作基準。

**Non-Goals:**

- 不在本 change 中撰寫正式 security audit findings。
- 不在本 change 中修補 application code 或調整部署架構。
- 不把文件寫成逐檔逐行的 code commentary。

## Decisions

### 以維護工作流程劃分 documentation information architecture

`docs/` 的章節將依照維護者的工作流程組織，例如總覽、角色與流程、architecture、backend / frontend、資料模型與 API、部署營運、已知缺口，而不是單純照檔案樹列出。這樣可以讓新讀者先建立系統心智模型，再回到對應 source files 深讀。

替代方案是做成 file-by-file inventory。這種寫法對交接的幫助有限，也不利於學生先理解系統全貌，因此不採用。

### 以 source evidence 建立文件 traceability

每一份重要文件都必須能對回具體 source evidence，例如 `route`、`environment variable`、資料表初始化位置與外部服務整合位置。這能避免文件與實作脫節，也讓未來更新文件時有可比對的錨點。

替代方案是只寫 narrative summary。這樣雖然省時，但無法支撐維護與審查，因此不採用。

### 以台灣繁體中文與 English technical terms 作為文件基準

proposal、design、tasks 與 `docs/` 內文採用台灣慣用繁體中文，technical terms 優先保留 English，例如 `authentication`、`authorization`、`token`、`route`、`deployment`、`remediation`。嚴格禁止中國大陸用語，以降低閱讀歧義。

Spectra `spec.md` 依工具慣例維持 English normative language。這是工具語義需求，不代表一般文件可以放寬語言政策。

替代方案是全中文翻譯 technical terms 或全面雙語。前者容易造成術語偏差，後者維護成本過高，因此不採用。

### 以 onboarding path 服務學生與新維護者

文件將明確提供閱讀順序，使第一次接手的人可以先讀專案目標與主要流程，再進入 subsystem 與營運細節。這可以同時服務學生讀者與實際維護者，而不必為不同受眾各寫一套文件。

替代方案是只寫深度技術文件。這會提高學生閱讀門檻，因此不採用。

## Risks / Trade-offs

- [文件內容太多，容易退化成流水帳] → 用固定章節與 source-backed summary 控制篇幅，優先解釋維護者需要做決策的內容。
- [source code 後續更新使文件過時] → 在每個主要章節保留明確 source references，讓後續維護時可快速比對。
- [台灣繁體中文與 English technical terms 混寫不一致] → 建立 terminology review 步驟，在交付前逐頁檢查。
- [學生與維護者期待不同] → 以 onboarding path 串接總覽與深度章節，避免分裂成兩套文件。

## Migration Plan

1. 建立 `docs/` 的資訊架構、索引與閱讀順序。
2. 盤點主要 source evidence，整理 roles、flows、subsystems、routes、data model 與 deployment inputs。
3. 撰寫一般專案文件，涵蓋 overview、architecture、backend / frontend、API、data model、operations 與 known gaps。
4. 執行 terminology review，確認台灣繁體中文、English technical terms 與禁止中國大陸用語的規範都已落實。

## Open Questions

- 已於本次 apply 前確認：文件採用文字與 file references 為主，不納入 UI screenshots。
- 已於本次 apply 前確認：已知缺口章節需區分「功能缺口」與「營運風險」兩類，以便後續開 change。
