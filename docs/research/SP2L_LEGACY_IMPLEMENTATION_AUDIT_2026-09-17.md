# SP2L Legacy Author Implementation Audit — 2026-09-17

## Status

`RESEARCH_ONLY / IMPLEMENTATION EVIDENCE / NON-CANONICAL`

This document audits the author-associated public repository:

`AlirezaSadabadi/PythonTraderBot`

Relevant paths:
- `code/SP2L/SP2L.ipynb`
- `code/SP2L/SP2L2_Advanced_Backtest.ipynb`
- `code/SP2L/SP2L_Advanced_Bot.py`
- `code/SP2L/Meta.py`
- `code/README.md`

The repository is treated as **implementation evidence**, not as an automatic replacement for primary training-source semantics. Source meaning remains authoritative for canonical Strategy A geometry.

## 1. Why this artifact matters

The repository contains a complete historical implementation of an SP2L detector/backtest/trader and therefore exposes concrete hypotheses for dimensions that remain unresolved in the source-resolution track.

The earlier `SP2L.ipynb` explicitly defines:

- `spikeCandleSize = 1.5`
- `pGapSize = 1`
- `backCandleSampleCount = 3`
- P-Gap as `low-1 > high-3 + pGapSize` for BUY and the mirrored SELL condition.
- Spike as the middle candle body exceeding 1.5x the bodies of the adjacent candles and current candle.

The advanced implementation carries these concepts forward with broker-point conversion and adds explicit entry/SL/TP/trend/filter logic.

## 2. Source-vs-implementation classification

| Dimension | Author implementation evidence | Current source-resolution status | Canonical? |
|---|---|---|---|
| 3-candle reference geometry | Explicit | Source visually supports spike + surrounding candles, exact classifier still under review | NO |
| P-Gap | `1.0` price in earlier notebook; later `100` broker points | Primary artifact visibly labels P-Gap, exact executable formula still unresolved | NO |
| Spike size | `1.5x` body comparison | Source has spike-candle teaching; exact executable classifier not fully discriminated | NO |
| Spike candle position | middle candle (`-2` in notebook / `-3` live indexing) | Consistent with inspected implementation and source examples | NO |
| BUY entry | first later candle whose low breaks previous candle low | Implementation-defined | NO |
| SELL entry | first later candle whose high breaks previous candle high | Implementation-defined | NO |
| BUY SL | low of candle before spike | Implementation-defined; source visual separation exists | NO |
| SELL SL | high of candle before spike | Implementation-defined; source visual separation exists | NO |
| TP | 1R | Source shows TP1/TP2 concepts; exact formula unresolved | NO |
| 2X | entry +/- half risk; optional; volume multiplier 2.0 | Source teaches 2X, exact formula/execution semantics unresolved | NO |
| EMA filter | EMA 60, enabled by default in advanced implementation | No source confirmation as canonical SP2L rule | NO |
| Trend filter | max one opposite high/low move, enabled by default | No source confirmation as canonical executable filter | NO |
| ADX filter | optional, disabled | No source confirmation | NO |
| NY session filter | optional, disabled; 01:00–05:00 New York | Current project has a separate configurable London→NY research window | NO |
| Max SL distance | 1000 points | No source confirmation | NO |

## 3. Important exact implementation findings

### 3.1 Earlier SP2L notebook

The original notebook's executable conditions use the following reference structure:

- current candle = `0`
- candle after spike = `1`
- spike candle = `2`
- candle before spike = `3`

For BUY:

`pGapBuy = low-1 > high-3 + pGapSize`

For SELL:

`pGapSell = high-1 < low-3 - pGapSize`

Spike body is measured using **body values**, not wick ranges.

This is valuable evidence because it gives a historical author implementation of the exact candidate geometry we have been keeping as unresolved hypotheses.

### 3.2 Advanced backtest

The advanced backtest retains the same 3-candle P-Gap/spike structure and then searches forward for the first valid entry.

For BUY:

- SL = low of the candle before the spike.
- Entry = first later candle whose low is below the previous candle low.
- Risk = entry - SL.
- TP = entry + `TP_R * risk`.

For SELL the implementation is mirrored:

- SL = high of the candle before the spike.
- Entry = first later candle whose high is above the previous candle high.
- Risk = SL - entry.
- TP = entry - `TP_R * risk`.

The advanced implementation also applies optional EMA/trend/range/session filters before accepting the first entry.

### 3.3 2X implementation

The advanced implementation calculates:

- BUY 2X entry = `entry - risk / 2`
- SELL 2X entry = `entry + risk / 2`
- second-entry volume multiplier = `2.0`

In the current advanced bot, `USE_SECOND_ENTRY = False` by default.

This is an **implementation formula**, not yet a source-discriminated canonical 2X rule.

## 4. Backtest result recorded in the artifact

The current `SP2L2_Advanced_Backtest.ipynb` contains an execution output showing:

- BUY signals: 47
- SELL signals: 46
- Signals: 93
- Completed trades: 92
- Wins: 66
- Losses: 26
- Win rate: 71.74%
- Total R: +40.0R
- Profit factor: 2.538
- Max drawdown: -300
- TP exits: 66
- SL exits: 25
- Same-bar SL/TP: 1

These numbers are **historical artifact output only**. They are not a current project validation result and cannot promote any geometry to canonical status.

## 5. Repository claim discrepancy

The repository README/searchable description states that `SP2L_Advanced` has a claimed `84% winrate`, `profit factor 5.5`, and `return 43%`. The inspected advanced backtest notebook output instead records `71.74%`, `PF 2.538`, and `40%` return for its shown run.

This discrepancy must be treated as an unresolved provenance/version/dataset difference until independently reproduced. Neither claim is promoted as a Strategy A performance result.

## 6. Timestamp risk discovered

`code/SP2L/Meta.py` converts MT5 epoch seconds using:

`pd.to_datetime(df["time"], unit="s")`

which produces a naive datetime index.

Its default `fromDate` also adds `timedelta(hours=3)` before `copy_rates_from`.

The advanced session helper subsequently interprets naive timestamps as `Etc/GMT-3` before converting to New York.

The current Strategy A timestamp investigation has established a separate canonical research basis of UTC timestamps. Therefore the legacy session-time handling must **not** be copied into the current canonical pipeline without an explicit source/data-basis reconciliation.

## 7. Governance conclusion

This repository materially improves the research position because it exposes concrete historical implementation hypotheses for P-Gap, spike geometry, entry, SL, TP, and 2X.

However:

1. implementation evidence does not automatically become source-confirmed canonical geometry;
2. backtest performance cannot be used to choose between competing source hypotheses;
3. the current Frozen Geometry gate remains BLOCKED;
4. the legacy code should be used as a **hypothesis map / reconciliation target** against the primary training artifact;
5. any dimension where the primary source clearly confirms the same rule can be moved to human adjudication with the author implementation as corroborating evidence;
6. unresolved dimensions remain `REMAINS_BLOCKED`.

## 8. Recommended next research pass

Do not redesign the strategy from scratch.

Instead perform a **Legacy Implementation ↔ Primary Artifact Reconciliation** on these exact dimensions:

1. P-Gap: `low(after) vs high(before)` and the `1.0` / `100-point` distance.
2. Spike: middle candle body vs adjacent candle bodies, including the `1.5x` condition.
3. Entry: first lower-low / higher-high trigger after setup.
4. SL: candle-before-spike low/high.
5. TP: whether source's TP1 corresponds to 1R.
6. 2X: whether source visual/text corresponds to half-risk price and/or 2x size.
7. Any source statement that changes the implementation's candle indexing or lifecycle.

Only after these comparisons should a human adjudication package be updated.

## Gate

```text
LEGACY_IMPLEMENTATION_AUDIT = PASS
IMPLEMENTATION_AS_CANONICAL_SOURCE = NO
PRIMARY_SOURCE_RECONCILIATION = REQUIRED
FROZEN_GEOMETRY = BLOCKED
DEV = LOCKED
UNTUCHED_VALIDATION = LOCKED
ROBUSTNESS/STABILITY = LOCKED
FRESH_HOLDOUT = LOCKED
PRODUCTION = OFF
```
