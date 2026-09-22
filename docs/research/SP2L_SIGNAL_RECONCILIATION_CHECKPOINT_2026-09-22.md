# SP2L Signal Reconciliation Checkpoint — 2026-09-22

## Scope

Research-only reconciliation of the condition diagnostic predicate against the exact `signal()` implementation on MT5 M1 data for 2026-09-14 through 2026-09-18 UTC.

Branch at execution:
`research/sp2l-multi-symbol-condition-diagnostics-2026-09-22`

Base implementation commit:
`fde99645ca83cb81729e33c688f1e152aa83a486`

Configuration:
- P-Gap price: 1.0
- Spike multiplier: 1.5
- Max SL price: 10.0
- TP R: 1.0

## Results

| Symbol | Side | Diagnostic | Exact signal | Both | Diagnostic-only | Signal-only |
|---|---:|---:|---:|---:|---:|---:|
| BTCUSD.ecn | BUY | 33 | 33 | 33 | 0 | 0 |
| BTCUSD.ecn | SELL | 33 | 33 | 33 | 0 | 0 |
| EURUSD.ecn | BUY | 0 | 0 | 0 | 0 | 0 |
| EURUSD.ecn | SELL | 0 | 0 | 0 | 0 | 0 |
| USTEC.c.ecn | BUY | 26 | 26 | 26 | 0 | 0 |
| USTEC.c.ecn | SELL | 24 | 24 | 24 | 0 | 0 |

All three symbol runs reported empty `first_disagreements` for both BUY and SELL.

## Interpretation

The corrected research diagnostic now reconciles condition-for-condition with the imported author-replica `signal()` for all tested symbol/side combinations in this week.

This closes the **engineering reconciliation issue** that previously appeared on the BTCUSD SELL path. The earlier one-case discrepancy was caused by the diagnostic predicate omitting the exact SELL condition `spike.open < A.open`; that omission has been corrected.

This result does **not** validate or freeze the underlying trading geometry as teacher-canonical. It only establishes implementation consistency between the diagnostic predicate and the current research `signal()` implementation.

## Source / canonical status

No canonical Strategy A geometry is changed by this checkpoint.

Still unresolved:
- exact source-defined A/B anchors;
- exact C anchor;
- executable P-Gap formula;
- complete spike grammar;
- AB=CD anchors/tolerance;
- pending-limit fill semantics;
- execution semantics.

Next research gate remains source geometry resolution, followed by frozen geometry and untouched validation.

## MT5 data coverage

- BTCUSD.ecn: 10,000 bars returned; first returned 2026-09-10 01:09 UTC; last returned 2026-09-18 23:54 UTC.
- EURUSD.ecn: 10,000 bars returned; first returned 2026-09-10 01:14 UTC; last returned 2026-09-18 23:58 UTC.
- USTEC.c.ecn: 10,000 bars returned; first returned 2026-09-09 17:55 UTC; last returned 2026-09-18 23:57 UTC.

These are MT5 acquisition observations and are not evidence that the source geometry is canonical.
