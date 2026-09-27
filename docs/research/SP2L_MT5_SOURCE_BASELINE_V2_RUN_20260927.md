# SP2L MT5 Source Baseline V2 — Run 2026-09-27

Research-only reproducibility record. This result is not canonical Strategy A evidence.

## Execution
- Runner: `scripts/run_sp2l_mt5_source_baseline_v2.py`
- Detector: `scripts/sp2l_strategy_a_v2_detector.py`
- Resolved symbol: XAUUSD.ecn
- Timeframe: M1
- Window: 2026-09-14T00:00:00Z through 2026-09-25T23:59:59Z
- Bars: 13,790
- Session filter: OFF
- 2X: OFF
- P-Gap research threshold: 1.0
- Spike multiplier: 1.5
- Max SL distance: 10.0
- TP: 1R

## Observed result
- Signals: 227
- Decisive: 220
- Wins: 124
- Losses: 96
- Ambiguous: 5
- No fill: 2
- Win rate on decisive: 56.363636%
- Net: +28R

## Interpretation boundary
This establishes a reproducible run of the dedicated V2 detector against the connected MT5 history for this window. It does not establish the source meaning of unresolved P-Gap geometry, trigger semantics, SL boundary semantics, fill chronology, or outcome semantics.

The earlier remembered 222 / 204 / 127 / 77 result is not treated as proven-parity evidence. Reconciliation must use signal ledgers and frozen contracts rather than selecting the more favorable result.
