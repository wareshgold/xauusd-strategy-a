# SP2L Multi-Symbol Backtest Validation Report

**Branch:** `research/sp2l-f13-demo-forward-slfixed-2026-09-21`  
**Period:** 2026-06-12 through 2026-09-23 UTC (September data through 2026-09-22 23:57/23:59 depending symbol)  
**Status:** RESEARCH ONLY / NON-CANONICAL

## 1. Frozen configuration

The existing source-aligned research configuration was replayed unchanged:

- P-Gap: 1.0 price units
- Spike multiplier: 1.5
- Max SL: 10.0 price units
- TP: 1R
- Timeframe: M1
- Data source: MetaTrader 5 terminal data
- No parameter optimization performed for this report

This report does not promote any rule to canonical status.

## 2. Overall results

| Symbol | Signals | Decisive | Wins | Losses | Ambiguous | Win rate | Net R | PF | 95% Wilson CI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| XAUUSD.ecn | 502 | 498 | 312 | 186 | 4 | 62.65% | +126R | 1.68 | 58.32–66.79% |
| USTEC.c.ecn | 275 | 267 | 187 | 80 | 8 | 70.04% | +107R | 2.34 | 64.29–75.22% |
| DJ30.c.ecn | 178 | 176 | 126 | 50 | 2* | 71.59% | +76R | 2.52 | 64.52–77.74% |
| **Combined** | **955** | **941** | **625** | **316** | **13** | **66.42%** | **+309R** | **1.98** | — |

\* The aggregate source summary records 1 DJ30 ambiguous row; the underlying monthly trade aggregation contains 2 non-decisive rows. This discrepancy is retained as a data-integrity item rather than silently resolved.

PF here is the simplified 1R accounting ratio: wins / losses. It is not a broker-realized profit factor.

## 3. Month-by-month

### XAUUSD.ecn

| Window | Signals | Wins | Losses | Ambiguous | Win rate | Net R |
|---|---:|---:|---:|---:|---:|---:|
| Jun 12–30 | 96 | 54 | 42 | 0 | 56.25% | +12R |
| July | 132 | 81 | 51 | 0 | 61.36% | +30R |
| August | 155 | 101 | 53 | 1 | 65.58% | +48R |
| Sep 1–22 | 119 | 76 | 40 | 3 | 65.52% | +36R |

### USTEC.c.ecn

| Window | Signals | Wins | Losses | Ambiguous | Win rate | Net R |
|---|---:|---:|---:|---:|---:|---:|
| Jun 12–30 | 37 | 26 | 8 | 3 | 76.47% | +18R |
| July | 67 | 48 | 17 | 2 | 73.85% | +31R |
| August | 87 | 61 | 26 | 0 | 70.11% | +35R |
| Sep 1–22 | 84 | 52 | 29 | 3 | 64.19% | +23R |

### DJ30.c.ecn

| Window | Signals | Wins | Losses | Ambiguous | Win rate | Net R |
|---|---:|---:|---:|---:|---:|---:|
| Jun 12–30 | 29 | 23 | 6 | 0 | 79.31% | +17R |
| July | 60 | 44 | 16 | 0 | 73.33% | +28R |
| August | 61 | 39 | 20 | 1 | 66.10% | +19R |
| Sep 1–22 | 28 | 20 | 8 | 0 | 71.43% | +12R |

## 4. Directional breakdown

The underlying trade records give:

| Symbol | Direction | Decisive | Wins | Losses | Win rate |
|---|---|---:|---:|---:|---:|
| XAUUSD.ecn | BUY | 243 | 152 | 91 | 62.55% |
| XAUUSD.ecn | SELL | 255 | 160 | 95 | 62.75% |
| USTEC.c.ecn | BUY | 139 | 99 | 40 | 71.22% |
| USTEC.c.ecn | SELL | 128 | 88 | 40 | 68.75% |
| DJ30.c.ecn | BUY | 94 | 66 | 28 | 70.21% |
| DJ30.c.ecn | SELL | 82 | 60 | 22 | 73.17% |

No directional filter is introduced from these observations.

## 5. Drawdown / loss-run diagnostics

Using the chronological decisive trade records and equal +1R/-1R accounting:

- Combined net: +309R
- Maximum sequential equity drawdown: 5R
- Maximum consecutive losses: 5

These are research diagnostics only. They are not broker-money drawdown estimates because spread, commission, swap, slippage, sizing and symbol-specific tick economics are not modeled.

## 6. Signal frequency

Across the 103 calendar-day window:

- XAUUSD: 502 signals, about 4.87 signals/calendar day
- USTEC: 275 signals, about 2.67 signals/calendar day
- DJ30: 178 signals, about 1.73 signals/calendar day
- Combined: 955 signals, about 9.27 signals/calendar day

These rates are descriptive only and should not be interpreted as expected future frequency.

## 7. Statistical interpretation

The decisive win-rate estimates are above 50% for all three symbols in this sample. The approximate 95% Wilson intervals are:

- XAUUSD: 58.32%–66.79%
- USTEC: 64.29%–75.22%
- DJ30: 64.52%–77.74%

These intervals describe uncertainty under a simple binomial model. They do **not** establish independence of trades, stationarity, execution realism, or future performance.

## 8. Data-quality findings

The source artifacts report unique and chronological timestamps for each monthly run. However:

1. There are substantial market-session/weekend gaps in the MT5 M1 data.
2. Historical MT5 timestamp mapping remains unresolved.
3. M1 data cannot determine whether SL or TP was hit first when both occur inside one candle; such cases are marked ambiguous.
4. Index spread/commission/swap economics are not modeled.
5. Replay uses theoretical entry levels. Live pending-limit fill behavior is not represented.
6. The sample is predominantly a summer/trending period and does not constitute a broad regime test.
7. The aggregate DJ30 ambiguous count differs by one between the summary artifact and underlying monthly trade aggregation; this must be reconciled before using the report as a formal validation artifact.

## 9. Decision status

This report does **not** declare a winning symbol, does not rank symbols for production use, and does not change Strategy A geometry.

The results support the next research step: robustness/stability testing of the already-frozen research configuration across XAUUSD, USTEC and DJ30, followed by an untouched validation/holdout. Forward-test execution should remain separate from this backtest.

## Source artifact

`artifacts/backtest-multi/SP2L_multi_symbol_replay_3.5month_summary_2026-06-12_2026-09-23.json`
