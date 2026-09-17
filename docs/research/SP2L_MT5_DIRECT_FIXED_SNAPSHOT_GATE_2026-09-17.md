# SP2L MT5 Direct Fixed-Snapshot Gate — 2026-09-17

## Status

Research-only. No canonical geometry change. No production signal generation.

## Direct MT5 observation supplied by operator

Source: `MetaTrader5.copy_rates_from`

- Terminal: Otet Group MT5 Terminal
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Requested/returned: 10,000 / 10,000
- Window: 2026-09-08T05:00:00Z through 2026-09-17T10:45:00Z
- Author-replica configuration: P-Gap price 1.0; spike multiplier 1.5; max SL distance 10.0; TP 1R
- Signals: 62
- Closed or ambiguous: 62
- Decisive wins/losses: 44 / 16
- Ambiguous: 2
- Decisive win rate: 73.3333%
- Total R: +28
- Profit factor: 2.75

These are descriptive results for this exact sample and implementation candidate. They are not canonical Strategy A validation results.

## Reproducibility issue identified

`copy_rates_from()` with a moving endpoint produces a different 10,000-bar window on different executions. The prior exported artifact ended at 2026-09-17T10:05:00Z, while this direct execution ended at 2026-09-17T10:45:00Z. Therefore the two result sets cannot be treated as a controlled feed comparison.

## Gate action

A fixed-endpoint research runner was added:

`scripts/run-author-replica-mt5-fixed-snapshot.py`

Default endpoint is the latest direct-MT5 observation (`2026-09-17T10:45:00+00:00`) and default size is 10,000 M1 bars. The runner records the complete candle snapshot and a SHA-256 hash of the normalized candle payload. It performs no trading calls.

## Required next comparison

1. Run the fixed snapshot from MT5.
2. Replay the resulting immutable JSON snapshot through the author-replica implementation.
3. Compare count, first/last timestamps, OHLC values, and candle SHA-256.
4. Only after equality is established treat MT5 direct and snapshot replay as the same data sample.
5. Preserve the author-replica result as implementation evidence, not canonical geometry.

## Research guardrails

- Do not tune P-Gap or spike thresholds from these results.
- Do not freeze P-Gap, AB=CD, entry/fill, SL, 2X, or Round Level semantics from performance.
- Frozen Geometry remains BLOCKED until source resolution is complete.
