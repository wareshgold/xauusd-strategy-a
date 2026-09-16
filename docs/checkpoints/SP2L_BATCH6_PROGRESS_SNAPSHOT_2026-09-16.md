# SP2L Batch 6 Progress Snapshot — 2026-09-16

## Completed in this pass

- Added deterministic source-discrimination fixtures for F09–F14.
- Added tests covering trigger-family preservation, Entry vs Leg-2 separation, competing 2X anchors, AB=CD exact-equality observation, and distinct wick/body/pivot candidates.
- Added a source-resolution status matrix documenting what is confirmed versus missing.
- Preserved all unresolved geometry as unresolved.
- No production BUY/SELL logic changed.

## Current gate

| Gate | Status |
|---|---|
| Source Resolution | 🟡 Partial |
| Synthetic Fixtures | 🟢 Advanced |
| Frozen Geometry | 🔴 BLOCKED |
| Untouched Validation | 🔒 |
| Robustness / Stability | 🔒 |
| Fresh Holdout | 🔒 |
| Production | 🔴 OFF |

## Critical unresolved items

1. Exact Entry anchor.
2. Exact SL/invalidation anchor and wick/body semantics.
3. Mandatory Limit-refresh condition/threshold.
4. Canonical trigger acceptance and precedence.
5. Exact 2X anchor/sizing/target semantics.
6. Exact AB=CD A/B/C/D anchors and tolerance.

## Next step

Continue transcript/source forensics against F09–F14. Prefer worked examples that expose numeric price levels and measurement conventions. If the source does not uniquely determine a field, freeze that field as `UNRESOLVED` rather than infer it from backtest performance.
