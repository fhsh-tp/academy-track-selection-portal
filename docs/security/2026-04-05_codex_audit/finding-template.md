# Finding Template

後續若要新增 finding，建議維持以下結構，讓不同批次的 audit 記錄可以互相比較。

## 建議欄位

1. `Finding ID`
2. `Title`
3. `Status`
4. `Severity`
5. `Category`
6. `Affected Areas`
7. `Summary`
8. `Business / Administrative Impact`
9. `Source Evidence`
10. `Risk Analysis`
11. `Recommended Remediation`
12. `Follow-up Owner`

## 建議格式

```md
# FINDING-XXX Title

## Metadata

- Status: Open / Deferred for discussion / Closed
- Severity: Critical / High / Medium / Low
- Category: OWASP ...
- Affected Areas:
  - `path/to/file`

## Summary

...

## Business / Administrative Impact

...

## Source Evidence

- `file:line-line`

## Risk Analysis

...

## Recommended Remediation

...

## Follow-up Owner

...
```

## 寫作原則

- 一律附 source evidence，不寫只有結論的 finding
- 說明技術風險時，也要說明行政或維運影響
- 如果暫不修補，必須記錄為 `Open` 或 `Deferred for discussion`，不能直接省略
- remediation 可以分成短期與長期，不必假裝一次到位
