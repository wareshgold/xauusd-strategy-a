# SP2L Fixed Snapshot Stability Plan — 2026-09-17

Research-only plan following the fixed OTET XAUUSD.ecn M1 snapshot. The objective is reproducibility and temporal stability of the author-associated replica, not canonical Strategy A validation.

## Fixed current snapshot
- Source: `MetaTrader5.copy_rates_from`
- Terminal: `Otet Group MT5 Terminal`
- Server: `OtetGroup-MT5`
- Symbol: `XAUUSD.ecn`
- Timeframe: M1
- Bars: 10,000
- Snapshot end: `2026-09-17T10:45:00+00:00`
- First bar: `2026-09-08T05:00:00+00:00`
- Last bar: `2026-09-17T10:45:00+00:00`
- Candle SHA-256: `4282cf2ff65e908ad5539b22e84bf0973812413c6d429bd8e8ad0cd8c06d3e5a`

## Replica configuration
- `pGapPrice = 1.0`
- `spikeMultiplier = 1.5`
- `maxSlPrice = 10.0`
- `tpR = 1.0`
- All other implementation behavior remains unchanged. No parameter optimization is permitted in this study.

## Current observed result
The fixed MT5 snapshot produced 62 signals, 44 wins, 16 losses, 2 ambiguous, decisive win rate 73.33%, total +28R, PF 2.75. These are descriptive author-replica results only; they are not canonical Strategy A validation because source geometry and execution semantics remain partially unresolved.

## Stability study
Use independently fixed historical MT5 snapshots at approximately:
1. current reference snapshot
2. 1 week earlier
3. 2 weeks earlier
4. 3 weeks earlier
5. 1 month earlier
6. additional older snapshots where data availability permits

Every snapshot must record exact end timestamp, bar count, first/last timestamps, symbol contract, and candle SHA-256. The exact same replica implementation/configuration must be used for every snapshot.

## Required outputs
- signal count
- decisive wins/losses
- ambiguous/open/unresolved count
- decisive win rate
- total R
- profit factor
- expectancy
- maximum drawdown R
- long/short counts and results
- timestamp coverage

## Guardrails
A threshold such as 60% is not a standalone acceptance rule. Stability must be assessed using sample size, dispersion across periods, R-based outcomes, drawdown, and unresolved execution semantics. Do not tune parameters to make historical periods pass a chosen threshold.

This study can provide reproducibility/stability evidence for the author-associated implementation candidate. It does not freeze P-Gap, AB=CD, entry, fill, SL, 2X, Round Level, or other unresolved canonical geometry.

## Workflow position
`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Current status remains before Frozen Geometry. Stability experiments are explicitly noncanonical and research-only.
