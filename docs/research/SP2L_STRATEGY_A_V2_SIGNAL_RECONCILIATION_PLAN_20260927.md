# SP2L Strategy A V2 — Signal Reconciliation Gate — 2026-09-27

## Purpose

Reconcile the large difference between the V2 MT5 replay and the earlier source-aligned replay before any parameter optimization.

## Fixed evidence

V2 replay:
- 222 signals
- 204 trades
- 127 wins / 77 losses
- 62.2549% completed win rate
- +50R
- artifact: `artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260927T052251Z.json`

Earlier source-aligned replay:
- 53 signals
- 33 decisive outcomes
- 12 wins / 21 losses
- -9R
- same broad MT5-local research window

## Reconciliation categories

Every setup should be classified as:
1. COMMON — both detectors identify the setup.
2. V2_ONLY — identified only by V2.
3. SOURCE_ALIGNED_ONLY — identified only by source-aligned research geometry.

For common setups, compare:
- setup timestamp;
- direction;
- before/spike/after candle roles;
- trigger timestamp;
- entry anchor;
- SL anchor;
- risk distance;
- outcome classification.

For non-common setups, inspect representative OHLC windows and identify the first rule-level divergence.

## Research constraints

- No parameter optimization before reconciliation.
- No canonical promotion from backtest performance.
- No production BUY/SELL generation.
- Unresolved source geometry remains unresolved.
- Any proposed interpretation must be labeled research-only until source evidence supports it.

## Success criterion

The reconciliation should explain the signal-count divergence at rule level, not merely demonstrate that one implementation has better performance.

## Next experiment

Implement a deterministic signal-set comparison artifact using the same MT5-local history and frozen date window, then inspect representative V2-only and source-aligned-only cases.
