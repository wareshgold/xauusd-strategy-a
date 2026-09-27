# SP2L Strategy A V2 — Multi-Week Test Matrix

Status: RESEARCH ONLY. No canonical or production decision.

## Objective

Measure reproducibility across XAUUSD and the selected FX population over many
calendar weeks. A week is an independent observation; pooled metrics must not
hide week-to-week instability.

BTCUSD, DJ30 and USTEC/US100 are excluded from this matrix because their
commission/minimum-volume characteristics are not aligned with the intended
research population.

## Symbol matrix

| ID | Symbol | Population | Pip convention |
|---|---|---|---|
| XAU | XAUUSD | Primary | broker contract metadata; report price move and pip-equivalent |
| FX1 | USDJPY | FX | MT5 symbol contract; JPY pip convention |
| FX2 | EURJPY | FX | MT5 symbol contract; JPY pip convention |
| FX3 | GBPUSD | FX | MT5 symbol contract |
| FX4 | GBPJPY | FX | MT5 symbol contract; JPY pip convention |
| FX5 | EURUSD | FX | MT5 symbol contract |
| FX6 | USDCHF | FX | MT5 symbol contract |
| FX7 | USDCAD | FX | MT5 symbol contract |

Do not hard-code one pip size for every instrument.

The runner must obtain the symbol's point/digits and derive the reporting pip
size from an explicit instrument convention. The convention used for every run
must be stored in the artifact.

For XAUUSD, report both raw price-unit profit/R and pip-equivalent movement.

For FX, report:
- pips per trade
- total pips
- average pips/trade
- median pips/trade
- winning/losing pips
- BUY/SELL pips

Pips are a reporting unit; R remains the normalized risk unit used by the V2
candidate.

## Timeframe matrix

| ID | Timeframe | Role |
|---|---|---|
| T1 | M1 | Primary V2 definition |
| T2 | M5 | Separate robustness candidate |
| T3 | M15 | Separate robustness candidate |

M1 remains the frozen V2 research definition. M5/M15 do not silently modify V2.

## Trading-window matrix

| ID | Window UTC | Role |
|---|---|---|
| W0 | 00:00–24:00 | Full-day baseline |
| W1 | 07:00–17:00 | London → New York diagnostic |
| W2 | 08:00–17:00 | Existing London → New York convention |
| W3 | 13:00–17:00 | New York core diagnostic |

Session-filtered runs are observational variants unless separately registered.

## Calendar population

Primary:
- 2026-01-01 → 2026-09-25
- split into calendar weeks
- preserve every eligible week separately

Extended:
- 2025 full year where MT5 history permits
- 2024 full year where MT5 history permits

The matrix must never collapse all weeks into a single number.

## Required weekly metrics

For every symbol × timeframe × window × week:

- bars available
- missing bars / data gaps
- setups
- accepted signals
- trades
- wins / losses / ambiguous / EOD
- win rate
- net R
- total pips
- average pips/trade
- median pips/trade
- winning pips
- losing pips
- profit factor
- max drawdown R
- max consecutive losses
- expectancy per trade
- average risk
- BUY / SELL split
- duplicate/overlap count

## Statistical stability

Report:
1. pooled trade metrics
2. median weekly net R
3. mean weekly net R
4. standard deviation of weekly net R
5. fraction of positive weeks
6. fraction of negative weeks
7. worst week
8. best week
9. worst consecutive losing weeks
10. bootstrap confidence interval for trade-level expectancy
11. Wilson interval for positive-week proportion
12. pooled and weekly pip distributions

A long sample is preferred because it provides more observations, but a longer
sample must remain decomposed by week and year. More history does not make
structural changes disappear.

## Comparison rules

For candidate variants, compare using stable setup keys and signal keys.

Classify changes as:
- ADDED_SETUP
- REMOVED_SETUP
- CHANGED_ENTRY
- CHANGED_SL
- CHANGED_TP
- CHANGED_EXIT
- DATA_MISSING
- SAME

Performance alone does not promote a variant.

## Execution order

1. XAUUSD M1 full-day, all weeks
2. XAUUSD M1 session slices, all weeks
3. XAUUSD M1 BUY vs SELL
4. FX M1 full-day for USDJPY, EURJPY, GBPUSD, GBPJPY, EURUSD, USDCHF, USDCAD
5. FX session slices
6. XAUUSD M5/M15 robustness
7. FX M5/M15 robustness
8. extended 2025
9. extended 2024

## Canonical status

This matrix does not change V2 geometry and does not make another symbol,
timeframe, session or pip convention canonical. It is a research/robustness plan.
