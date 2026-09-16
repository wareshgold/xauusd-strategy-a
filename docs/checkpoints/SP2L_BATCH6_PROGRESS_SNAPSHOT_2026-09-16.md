# SP2L Batch 6 Progress Snapshot — 2026-09-16

## Completed in this pass

- Added deterministic source-discrimination fixtures for F09–F14.
- Added tests covering trigger-family preservation, Entry vs Leg-2 separation, competing 2X anchors, AB=CD exact-equality observation, and distinct wick/body/pivot candidates.
- Recovered and directly inspected the authoritative transcript blob.
- Cross-referenced transcript evidence with the existing visual geometry triangulation.
- Added `docs/research/SP2L_SOURCE_RECONCILIATION_F09_F14_2026-09-16.md`.
- Updated the F09–F14 source-resolution matrix to distinguish partial source discrimination from canonical freeze.
- Preserved all unresolved geometry as unresolved.
- No production BUY/SELL logic changed.

## Reconciliation result

- **F09 Entry:** PARTIAL. Demonstrated bullish visuals strongly support a dynamic/relevant completed higher-low pending entry, but this is not yet universal across Spike variants and entry-vs-Leg-2-origin semantics remain unresolved.
- **F10 Stop:** PARTIAL. Structural invalidation is distinct from entry; exact OHLC/wick/body anchor and buffer remain unresolved.
- **F11 Refresh:** PARTIAL / behavior confirmed. Delete/re-place behavior is source-supported; mandatory refresh threshold remains qualitative/unresolved.
- **F12 Trigger:** PARTIAL. One-, two-, and three-candle structures plus Bar/Key-Bar variants are source-described; deterministic classifier/precedence remains unresolved.
- **F13 2X:** PARTIAL. Optional second position and approximately half-target concept are source-supported; exact anchor/sizing/stop/fill semantics remain unresolved.
- **F14 AB=CD:** PARTIAL. SPIKE-2LEG ↔ AB=CD and Leg2≈Leg1 magnitude are source-supported; exact A/B/C/D endpoints and tolerance remain unresolved.
- **P-Gap:** UNRESOLVED at deterministic formula level; source distinguishes it from E-Gap/Common-Gap and ties it to breakout construction, but no unique OHLC equation is established.

## Current gate

| Gate | Status |
|---|---|
| Source Resolution | 🟡 PARTIAL / materially strengthened |
| Synthetic Fixtures | 🟢 ADVANCED |
| Frozen Geometry | 🔴 BLOCKED |
| Untouched Validation | 🔒 LOCKED |
| Robustness / Stability | 🔒 LOCKED |
| Fresh Holdout | 🔒 LOCKED |
| Production | 🔴 OFF |

## Critical unresolved items

1. Exact Entry anchor and universal scope.
2. Exact SL/invalidation OHLC anchor, wick/body semantics and buffer.
3. Mandatory Limit-refresh condition/threshold.
4. Canonical trigger acceptance and precedence.
5. Exact 2X anchor/sizing/target/stop/fill semantics.
6. Exact AB=CD A/B/C/D anchors and tolerance.
7. Exact P-Gap OHLC formula.

## Non-negotiable boundary

No source ambiguity is resolved by backtest performance. No P-Gap formula, AB=CD anchors/tolerance, 2X formula, fill semantics, stop buffer, refresh threshold, or production BUY/SELL rule is inferred or promoted from this pass. The 125R extreme trade remains untouched.

## Next step

Acquire the smallest source-primary evidence needed to uniquely discriminate the remaining anchors/conditions, especially worked visual/value examples for F09/F10/F13/F14 and explicit refresh/trigger-selection evidence for F11/F12. Do not enter historical validation until Frozen Geometry is unblocked.
