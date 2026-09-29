# SP2L Strategy A V2 Forward-Parity Checkpoint — 2026-09-29

## Purpose

Freeze the exact research-only V2 backtest implementation that produced the previously recovered 61.6519% reference result, and document the current forward-runner equivalence status before any new forward test.

This checkpoint does **not** promote V2 geometry to canonical Strategy A and does **not** authorize production BUY/SELL decisions.

## Recovered reference

Artifact:

`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260928T074842Z.json`

Reference result:

- signals: 1472
- trades: 1356
- wins: 836
- losses: 520
- completed win rate: 61.651917%
- net R: +316
- simplified PF: 1.607692
- max drawdown: 10R
- max consecutive losses: 10

Reference contract:

- P-Gap research threshold: 1.0 price unit
- spike multiplier: 1.5
- maximum SL distance: 10.0
- TP: 1R
- setup: before / spike / after
- trigger: first post-setup lower-low (BUY) / higher-high (SELL)
- entry: trigger Low (BUY) / High (SELL)
- SL: candle before Spike Low (BUY) / High (SELL)
- intrabar resolution: SL-first
- EMA/ATR/ADX/trend filters: disabled
- session filter: disabled
- second entry: disabled
- canonical: false

## Exact generator

Backtest script:

`scripts/run_sp2l_strategy_a_v2_mt5_backtest.py`

Detector:

`scripts/sp2l_strategy_a_v2_detector.py`

## Current forward implementation

The current multi-symbol forward runner contains the same V2 setup and first-trigger geometry:

`scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`

Its `detect()` and `find_first_entry()` implement:

- same three-candle setup
- same P-Gap threshold
- same spike body comparison
- first later lower-low / higher-high
- trigger Low / High entry
- candle-before-Spike SL
- 1R TP
- max SL distance

Therefore the previous conclusion that the forward runner was using the old Author-Replica four-candle detector is no longer correct for the current multi-symbol runner.

## Remaining parity blockers

The V2 backtest and current forward runner are **not yet execution/population-equivalent**:

1. **Session filter**
   - V2 reference backtest: disabled.
   - Forward runner: London-open → New-York-close gate is enabled by default.

2. **Historical lookback**
   - V2 backtest searches the full loaded history after each setup.
   - Forward runner currently polls only a small `copy_rates_from_pos` window (default 10 bars).
   - Therefore a valid first trigger occurring beyond that live lookback can be missed.

3. **History acquisition**
   - V2 backtest: `copy_rates_range`.
   - Forward runner: `copy_rates_from_pos`.
   - This is an acquisition-path difference and must be treated separately from geometry.

4. **Execution/fill semantics**
   - V2 backtest evaluates theoretical entry/SL/TP against subsequent M1 bars with SL-first same-bar resolution.
   - Forward runner submits a pending research order and is subject to broker order acceptance, fill timing, pending TTL, and market state.
   - These are unresolved execution semantics, not geometry.

5. **Signal state**
   - Forward runner suppresses repeated trigger keys through persisted state.
   - This is operational lifecycle behavior and must not be confused with the V2 backtest signal ledger.

## Decision gate

No fresh forward performance claim should be compared directly with the 61.6519% reference until:

`V2 geometry parity` + `signal-population parity` + `execution semantics documented separately`

are all explicitly reconciled.

The next engineering step is therefore a deterministic V2 forward-parity harness/check, not parameter tuning and not a new trading run.
