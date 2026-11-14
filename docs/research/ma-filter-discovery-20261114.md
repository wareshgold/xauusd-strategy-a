# MA Filter Research — One-Week Realized-Population Discovery

**Date:** 2026-11-14  
**Status:** Research-only / descriptive / non-canonical  
**Branch:** `research/ma-filter-forward-week-20261114`  
**Related PR:** [#418](https://github.com/wareshgold/xauusd-strategy-a/pull/418)

## 1. Purpose and decision boundary

This note records the first MA-filter comparison against the realized Strategy A Runner population for 2026-11-09 through 2026-11-13.

It is a **Discovery observation**, not evidence of a deployable edge. No MA type or period is selected, no Strategy A source rule is changed, and no production Runner or configuration is modified. The comparison must not be interpreted as counterfactual backtesting or as permission to issue BUY/SELL decisions.

## 2. Evidence population

Local export directory (not committed): `artifacts/ma_filter_week_20261109/`

| Artifact | SHA-256 |
|---|---|
| `runner_deals.csv` | `de25f6c791c6d50d6c371e8cbb8a2fd4a73deacc10eb5d2d5f3286f62d40d87c` |
| `xauusd_m1.csv` | `0b149aee3d9ae21cfe5a21ab7f6055231ca433f0334e56c0f3bf55b143b3e0d8` |

- 139 deal rows; 6,898 M1 bars.
- M1 span: 2026-11-09T01:00:00Z to 2026-11-13T23:57:00Z.
- Four M1 gaps exceed 60 seconds; largest gap: 3,660 seconds.
- 70 entry deals (46 BUY, 24 SELL); 69 closed positions and one open position.
- Closed population: 41 wins, 28 losses; win rate 59.42%.
- Closed net: -2.67 USD (gross +0.78, commission -3.45; swap/fee 0).
- Baseline F00: PF 0.9673, average net -0.039 USD per closed position.

The one open position is excluded from closed-trade performance statistics.

## 3. Alignment limitation

MA classification uses the **last completed M1 bar at or before the actual entry DEAL time**. This is a fill-time alignment proxy, not the exact Runner candidate/decision information set.

Runtime source review found:
- `trigger_time` is stamped from the trigger candle's bar-open timestamp in broker/server epoch.
- The trigger scan can include the final array element, which may be the current/incomplete M1 bar.
- The wrapper stamps `trigger_time`; it is not an exact detection, decision, order-send, or fill timestamp.
- Exact polling/detection timing remains unresolved.

A direct isolated AST fixture test of the runtime `find_first_entry` function was added as `tests/test_ma_runtime_final_bar_semantics.py`; the user ran it locally and all three tests passed (BUY final-bar trigger, SELL final-bar trigger, and no trigger when the final bar does not break the prior extreme). This validates the tested source behavior only; it does not resolve the actual decision timestamp.

Therefore, the results below are **descriptive classifications of trades that already occurred**. They do not estimate the outcomes of rejected trades, cannot establish a counterfactual strategy edge, and may contain timing/alignment bias.

## 4. Observed comparison

All values below are for the 69-position closed realized population, filtered by the stated MA condition at the fill-time proxy. F00 is the unfiltered baseline.

| Filter | Rule family | N | Win % | Net USD | PF | Avg net USD | Max DD USD |
|---|---|---:|---:|---:|---:|---:|---:|
| F00 | Baseline | 69 | 59.42 | -2.67 | 0.967 | -0.039 | 35.08 |
| F01 | SMA 50 price-side | 50 | 70.00 | 28.92 | 1.814 | 0.578 | 9.79 |
| F02 | SMA 100 price-side | 41 | 68.29 | 18.07 | 1.512 | 0.441 | 12.35 |
| F03 | EMA 50 price-side | 49 | 69.39 | 25.37 | 1.715 | 0.518 | 9.70 |
| F04 | EMA 100 price-side | 45 | 68.89 | 17.85 | 1.456 | 0.397 | 12.35 |
| F05 | SMA 20 price-side | 61 | 62.30 | 16.08 | 1.271 | 0.264 | 16.68 |
| F06 | SMA 200 price-side | 33 | 75.76 | 20.55 | 1.873 | 0.623 | 10.04 |
| F07 | EMA 20 price-side | 59 | 61.02 | 8.61 | 1.145 | 0.146 | 16.68 |
| F08 | EMA 200 price-side | 32 | 78.12 | 24.21 | 2.305 | 0.757 | 5.52 |
| F09 | SMA 50 + SMA 100 price-side | 39 | 69.23 | 24.32 | 1.853 | 0.624 | 8.45 |
| F10 | EMA 50 + EMA 100 price-side | 42 | 69.05 | 23.08 | 1.714 | 0.550 | 7.26 |
| F11 | SMA stack + price-side | 27 | 74.07 | 24.05 | 2.327 | 0.891 | 8.45 |
| F12 | EMA stack + price-side | 22 | 86.36 | 25.40 | 3.520 | 1.155 | 5.52 |
| F13 | OR of SMA/EMA 50/100 price-side | 54 | 68.52 | 23.65 | 1.558 | 0.438 | 12.35 |

The comparison script also records excluded winners/losers per filter in the generated local report. Those counts are not repeated here because the key interpretation is the small, already-realized subset, not a simulated selection policy.

## 5. Discovery interpretation

- F01, F03, F08, F09, and F12 are **temporary research candidates** for a larger Discovery comparison, not selected filters.
- F06 and F11 remain useful exploratory challengers.
- F12 has the strongest observed PF and win rate in this small sample, but only 22 trades; its apparent advantage is especially vulnerable to sampling noise and selection effects.
- F08 also has only 32 trades.
- The reduction in trade count is material for every filter. These results do not show what would have happened to trades that the filter would have rejected.
- F14–F18 remain blocked because the slope lookback/horizon is not source-defined. No arbitrary slope convention is introduced.
- M0–M4 management replay remains blocked pending source resolution of execution/fill/SL/TP/commission/spread/intrabar semantics. In particular, no ACT40/TRAIL40 behavior is inferred or authorized by this comparison.

## 6. Required next steps

1. Resolve/reconstruct the Runner candidate/decision timestamp and the exact information available at that moment. Do not substitute fill time or trigger-bar open time as if it were the decision timestamp.
2. Establish whether a matching multi-month **Runner deal population** exists and can be aligned with its M1 history. Historical market data alone is insufficient to replay the realized Runner population.
3. Add synthetic fixtures for the comparison script's position grouping, partial/multiple exits, reversal/ambiguous cases, timestamp boundary/equality handling, M1 gaps, and MA initialization before using it for a larger study.
4. Only after alignment and fixture correctness, run long-term Discovery on a frozen population; report per-filter sample sizes, rejected winners/losers, uncertainty intervals, daily/block-bootstrap stability, and multiple-comparison controls.
5. Keep all candidate definitions and outputs research-only. No canonical selection or production change until source resolution, untouched validation, robustness/stability, and a fresh holdout are completed.

## 7. Reproducibility pointers

- Analysis script: `scripts/research/analyze_ma_filter_realized_population.py`
- Runtime final-bar fixture: `tests/test_ma_runtime_final_bar_semantics.py`
- One-week local output: `artifacts/ma_filter_week_20261109/ma_filter_comparison.md` (local-only; not committed)
- Runtime wrapper SHA-256: `1E50F4AC41A397BB0FFA7DA7A2A2678E7066FCB1634DFD7190DA4D219812DE49`
- Shared runtime source SHA-256: `889155AC4E4DF6E4CE8B21B566415747DC017E9FB3919544D701A1EF80C40EE3`

**Conclusion:** The one-week realized-population comparison is a useful Discovery lead, but it is not a validated MA-filter edge. The immediate blocker is decision-time alignment, followed by validation of the analysis script and availability of a matching longer-term Runner population.


## 8. Analyzer validation hardening — 2026-11-14

During preparation for a longer-history run, code review identified a population-accounting issue: the analyzer previously dropped a position from **every** filter, including F00 baseline, whenever any one of the eight MA series was still warming up. That would bias early-history baseline counts and make the baseline denominator depend on the longest MA.

The analyzer has now been changed so:
- F00 always retains every time-aligned closed position.
- Each individual MA filter is marked unavailable only when its own required MA inputs are not initialized.
- Composite filters are unavailable only when the inputs required by that composite are missing.
- The report includes an explicit `Unavailable` count per filter rather than silently removing those positions from the full population.

Added `tests/test_ma_filter_realized_population_fixtures.py` with nine synthetic tests covering SMA/EMA initialization, insufficient history, partial exits and net-cost aggregation, open positions, reversal ambiguity, unsupported direction, equality-neutral classification, and filter-specific MA warm-up availability.

**Execution status:** These new tests have been committed but have not yet been run in the user's local worktree. Do not treat the analyzer hardening as test-passed until the local test command succeeds. Further fixtures are still needed for duplicate/out-of-order M1 timestamps, M1 gaps, and exact bar-boundary alignment before a long-term study.
