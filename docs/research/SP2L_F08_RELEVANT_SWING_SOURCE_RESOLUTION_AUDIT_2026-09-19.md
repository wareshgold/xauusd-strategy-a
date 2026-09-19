# SP2L F08 — Relevant Swing Selection Source Resolution Audit — 2026-09-19

## Purpose
Resolve whether the archived source uniquely determines which local swing/low/high becomes the executable structural reference.

## Evidence reviewed
- SP2L Batch34 primary sequence geometry forensic.
- Unified Source Blocker Matrix.
- Primary transcript trigger/correction evidence.
- Frozen Geometry Gate audit.

## Source-confirmed observations
The primary sequence visibly marks multiple local lower points before the Buy Limit step. This establishes that local structural points matter to the teaching sequence.

The transcript also describes a bullish correction beginning by moving below the first low, while later source wording refers to the previous-candle low/high for the Second-Leg trigger.

## What remains ambiguous
The source does not uniquely define:
- “first important” vs latest relevant swing;
- pivot-window length;
- whether a swing is candle wick, body, or close based;
- how multiple candidate lows/highs are ranked;
- whether the selected point evolves as new candles form;
- exact bullish/bearish mirror;
- how swing selection interacts with P-Gap and Buy Limit;
- whether the swing is the same object as the spike-origin candle.

## Deterministic acceptance test
| Requirement | Status |
|---|---|
| Local structural points are relevant | SOURCE-SUPPORTED |
| Correction references a low/high structure | SOURCE-CONFIRMED at concept level |
| Unique swing-selection algorithm | UNRESOLVED |
| Pivot/Fractal window | UNRESOLVED |
| Wick/body semantics | UNRESOLVED |
| Candidate precedence | UNRESOLVED |
| Dynamic update rule | UNRESOLVED |
| Directional mirror | UNRESOLVED |

## Decision
**F08 = PARTIAL / UNRESOLVED.**

No conventional pivot/fractal algorithm is introduced and no swing candidate is selected from backtest performance.

## Gate impact
Frozen Geometry remains **BLOCKED**. No new backtest is justified.
