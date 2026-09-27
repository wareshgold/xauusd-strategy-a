# SP2L Strategy A V2 — Multi-Week Test Matrix

Status: RESEARCH ONLY. No canonical or production decision.

## Objective

Measure whether the V2 candidate result is reproducible across symbols, timeframes,
trading windows, and calendar weeks instead of relying on a single favorable interval.

A week is treated as an independent observation. Aggregate metrics must not hide
week-to-week instability.

## Matrix

### Dimension A — symbol

| ID | Symbol | Purpose |
|---|---|---|
| S1 | XAUUSD (resolved broker symbol, currently XAUUSD.ecn) | Primary target |
| S2 | BTCUSD | Cross-market diagnostic |
| S3 | USTEC | Execution/market-structure diagnostic |
| S4 | DJ30 | Execution/market-structure diagnostic |

XAUUSD remains the primary Strategy A population. Other symbols are robustness
diagnostics, not evidence that the strategy transfers universally.

### Dimension B — timeframe

| ID | Timeframe | Purpose |
|---|---|---|
| T1 | M1 | Current V2 definition |
| T2 | M5 | Timeframe robustness diagnostic |
| T3 | M15 | Timeframe robustness diagnostic |

M1 is the only timeframe currently represented by the frozen V2 candidate.
M5/M15 must be treated as separate research candidates, not silent substitutions.

### Dimension C — trading window

| ID | Window (UTC) | Purpose |
|---|---|---|
| W0 | 00:00–24:00 | Full-day baseline |
| W1 | 07:00–17:00 | London → New York overlap research |
| W2 | 08:00–17:00 | Existing London→NY research convention |
| W3 | 13:00–17:00 | New York core diagnostic |

Session filtering is disabled in V2. These are observational slices unless a
separate candidate is explicitly registered.

### Dimension D — calendar sample

Primary historical population:

- 2026-01-01 → 2026-09-25
- split into calendar weeks
- retain every week with sufficient data
- do not average away missing weeks

Secondary stability populations:

- 2025 full year where MT5 history permits
- 2024 full year where MT5 history permits

The primary decision statistic is not one pooled win rate. Report the distribution
of weekly results.

## Required weekly metrics

For every symbol × timeframe × window × week:

- bars available / missing
- setups detected
- accepted signals
- trades
- wins / losses / ambiguous / EOD
- win rate
- net R
- profit factor
- max drawdown R
- max consecutive losses
- mean / median R
- expectancy per trade
- average risk
- BUY / SELL split
- duplicate/overlap count
- data-gap count

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
11. Wilson interval for weekly positive-week proportion

Never treat the pooled result as sufficient evidence when weekly dispersion is high.

## Required comparisons

For each candidate variation, compare against V2-CANDIDATE-001 using stable
setup keys and signal keys.

Changes must be classified as:

- ADDED_SETUP
- REMOVED_SETUP
- CHANGED_ENTRY
- CHANGED_SL
- CHANGED_TP
- CHANGED_EXIT
- DATA_MISSING
- SAME

No variant wins promotion merely because its backtest return is higher.

## Test ordering

Run in this order:

1. XAUUSD M1 full-day, all weeks
2. XAUUSD M1 session slices, all weeks
3. XAUUSD M1 BUY vs SELL, all weeks
4. XAUUSD M5 diagnostic
5. XAUUSD M15 diagnostic
6. BTCUSD M1 diagnostic
7. USTEC M1 diagnostic
8. DJ30 M1 diagnostic
9. extended 2025 population
10. extended 2024 population

This keeps the primary research population separate from robustness diagnostics.

## Interpretation rule

A single profitable week is not evidence of a stable edge.

A long sample with mixed positive and negative weeks is expected. The research
question is whether the distribution is sufficiently reproducible and whether
performance survives untouched time periods.

Weekly results must always remain visible in the artifact; never report only the
aggregate.

## Canonical status

This matrix does not alter V2 geometry and does not make any timeframe, symbol,
session, or filter canonical. It is a validation/robustness test plan.
