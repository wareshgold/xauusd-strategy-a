# SP2L Geometry Open Register — G28 — 2026-09-09

This register is the controlled boundary between source-confirmed semantics and executable geometry.

| ID | Question | Source status | Allowed research action | Production status |
|---|---|---|---|---|
| G1 | Exact P-Gap OHLC boundary and candle indexing | unresolved | compare source constructions; synthetic discrimination | blocked |
| G2 | Exact Entry anchor: structural pivot vs wick/body edge | unresolved | triangulate repeated bullish/bearish examples | blocked |
| G3 | Exact SL OHLC anchor and any buffer | unresolved | compare structural invalidation examples; no performance selection | blocked |
| G4 | Trigger acceptance and timing | unresolved | enumerate 1/2/3-candle and key-bar examples | blocked |
| G5 | A/B/C/D anchors and AB=CD tolerance | unresolved | discriminate wick/body/structural-pivot/mixed models | blocked |
| G6 | Leg2 projection and TP1 executable formula | unresolved | map narrated Leg1/Leg2 examples without assuming C=Entry | blocked |
| G7 | Pending replacement threshold/timing | unresolved | separate structural update from discretionary risk commentary | blocked |
| G8 | Exact bearish candle-level geometry | partial | mirror only source-proven structural relationships | blocked |

## Decision rules

- Source meaning cannot be selected by historical profitability.
- If two or more geometries remain source-consistent, the result is UNRESOLVED.
- A synthetic fixture may reject an interpretation, but cannot prove an interpretation that the source does not uniquely support.
- No production code may consume a value from this register unless its status becomes RESOLVED with source provenance.
- No implicit defaults for wick/body, tolerance, buffer, threshold, or candle indexing are permitted.

## Exit criterion for Frozen Geometry

All critical items G1–G6 must be RESOLVED or formally escalated as a source limitation with explicit non-executable semantics. G7–G8 must also be resolved before production execution behavior is frozen.
