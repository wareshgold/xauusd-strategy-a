# SP2L Interactive Research Dashboard — Architecture Snapshot

**Snapshot date:** 2026-11-01  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Checkpoint branch:** `research/checkpoint-v3-exit-discovery-20261101`  
**Checkpoint base HEAD before this snapshot:** `0f5b3cd1b4cd287a8d432d73a244f4b85defe37a`  
**Status:** Planned / not implemented / research-only

## 1. User objective

Build an interactive research dashboard that can access preserved MT5 historical datasets (M1 and, where available, tick data) and let the user change strategy parameters and optional filters, then inspect the resulting backtest metrics and trade population with minimal delay.

The intended experience is an interactive laboratory, not a static report generator:
- Toggle filters such as EMA 20 and EMA 100 independently and in combination.
- Change numeric parameters such as RR, activation thresholds, trailing distances, and other explicitly supported research parameters.
- Immediately refresh or rapidly recompute Win Rate, net profit / net R, trade count, removed-signal count, Profit Factor, drawdown, and related metrics.
- Compare baseline and modified configurations side by side.
- Inspect which signals/trades were retained, excluded, or changed by a filter.
- Save each experiment with its configuration and reproducibility metadata.

All parameter names and semantics must be defined by the relevant strategy implementation or source-confirmed research specification. This dashboard plan does not define SP2L geometry, P-Gap, AB=CD anchors/tolerance, fill semantics, or execution rules.

## 2. Proposed architecture

### A. Data Manager
- Discover and register existing MT5 datasets.
- Preserve source files byte-for-byte.
- Record symbol, timeframe, date range, broker/source, timezone convention, data type (OHLC/tick), row/bar count, gaps, duplicate/out-of-order diagnostics, and SHA-256.
- Support explicit dataset selection; never silently substitute or repair a dataset.
- Keep OHLC-proxy and tick-level capabilities clearly distinguished.

### B. Strategy / Replay Engine
- Reuse the existing deterministic research/backtest engine where possible rather than reimplementing V3 entry logic in the UI.
- Separate frozen entry population from experimental exit management and optional research filters.
- Make assumptions visible: OHLC intrabar ambiguity, spread, slippage, commission, missing data, and fill model.
- No MT5 order placement and no broker-connected execution path.

### C. Interactive Parameter Lab
- UI controls for booleans, numeric parameters, ranges, and supported filter configuration.
- Initial filter examples: EMA 20, EMA 100; these are research hypotheses, not approved/canonical rules.
- Recompute only affected calculations where safe; use caching keyed by dataset hash, engine/version hash, entry-population hash, and full configuration.
- Clearly distinguish cached results from newly computed results.

### D. Results and Comparison
- Live/near-live KPI panels: signals, executed/decisive trades, filtered-out signals, wins/losses, win rate, net R/profit, Profit Factor, max drawdown, and ambiguity/unresolved counts.
- Baseline-versus-variant comparison.
- Trade-level diff showing exactly which signals were added, removed, or had changed outcomes.
- Time-slice and parameter-neighbourhood views.
- Exportable experiment report with full provenance.

### E. Experiment / Evidence Registry
- Immutable experiment records: configuration, source dataset hashes, entry population hash, engine commit/version, assumptions, output hashes, timestamps, and research stage.
- Refuse silent overwrite of prior experiments.
- Label results as exploratory, development, validation, or fresh holdout.
- Preserve separation between research experiments and frozen/canonical strategy definitions.

## 3. Performance and correctness requirements

- Preload/index historical data and cache deterministic intermediate results.
- Avoid full replay for UI-only changes when an exact safe incremental calculation is possible.
- Never trade correctness for apparent instant feedback; show a running/recomputing state when necessary.
- Repeated identical inputs must produce reproducible outputs.
- A changed input must invalidate all dependent cache keys.
- Every displayed metric must be traceable to the exact dataset, code version, and configuration.
- Missing or ambiguous outcomes must remain explicit; never convert unknown outcomes to zero or silently drop them from reports.
- Display dataset gaps and execution-model limitations alongside results.

## 4. Safety and project boundaries

- Dashboard is research/analytics only.
- It must not autonomously generate production BUY/SELL decisions.
- It must not place, modify, or close MT5 orders.
- It must not modify frozen V3 entry logic or canonical rules.
- EMA filters and user-adjustable parameters remain non-canonical research inputs unless separately source-confirmed and formally frozen.
- Development experiments must not consume or tune against Fresh Holdout data.
- The dashboard must enforce distinct Development, Untouched Validation, Robustness/Stability, and Fresh Holdout dataset roles.

## 5. Suggested implementation sequence

1. Data inventory and dataset registry using existing preserved MT5 files.
2. Engine adapter around the current deterministic V3 research replay; no entry-logic rewrite.
3. Minimal dashboard: dataset selector, baseline metrics, parameter controls, and recomputation.
4. EMA/filter experiment support with exact retained/removed trade identities.
5. Comparison workspace, experiment history, provenance manifests, and exports.
6. Performance optimization and cache correctness tests.
7. Stage-aware validation gates and holdout protections.
8. Only after these are proven, consider richer charting and tick-level replay integration.

## 6. Current project context at snapshot time

- The preserved V3 Exit Discovery run contains 462 frozen entry signals, 288 exit variants, and 133,056 replay rows on a 30-day M1 OHLC dataset.
- The M1 input contains 29,919 bars and 21 detected gaps / 12,802 missing minute slots; gaps were not filled.
- Discovery is exploratory and in-sample; no exit candidate is canonical or production-approved.
- The local artifact audit passed; evidence manifest SHA-256 reported by the user: `bea79456196e6e08b7186b1000eaec787d5ba6d697db0dd5c45bbb3322e49452`.
- The local robustness run completed and produced 288 variant rows and 1,152 time-slice rows. Its reported centered circular moving-block max-t diagnostic used 2,000 iterations, seed 20261101, 22 UTC trade days, block length 3, observed max-t 4.4762, 95th percentile 4.7700, and familywise p-value 0.06297.
- That p-value is exploratory only. Before interpreting it as robust evidence, the missing-day handling in the block bootstrap requires code review: sampled blocks must preserve calendar positions and missingness masks rather than compressing known observations across unknown dates.
- PR #380 remains Draft and unmerged; the latest branch head at snapshot time was `450f6384098d731d857139a9a4c039f378615d88`. Its post-fix CI status and the missingness-aware bootstrap review remain outstanding.

## 7. Immediate next work

Before dashboard implementation, finish the current robustness review:
1. Inspect and correct missingness-aware moving-block resampling so calendar spacing and the missingness mask remain aligned.
2. Add regression tests for irregular missing-day patterns and deterministic reproducibility.
3. Re-run targeted tests and all required CI checks for the corrected commit.
4. Review the local robustness outputs (time slices, local neighbourhoods, equivalence of variants) without promoting a winner.
5. Then start dashboard Phase 1 (Data Manager + dataset registry) as a separate research-only workstream.

**Non-goal:** This snapshot does not authorize parameter selection, canonicalization, production use, MT5 execution, or a Fresh Holdout run.
