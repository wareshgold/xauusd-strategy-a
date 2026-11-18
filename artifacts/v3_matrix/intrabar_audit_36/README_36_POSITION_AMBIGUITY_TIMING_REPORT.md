# XAUUSD V3 — 36-Position Intrabar Ambiguity & Timing Report

**Status:** research-only diagnostic; non-canonical  
**Source branch:** `research/v3-matrix-per-position-summary-20261118`  
**Source JSON blob SHA:** `e60bdf1375730d66287a88e94afcdbd086d86c02`  
**Source rows:** 21,600 audit rows; 36 positions × 600 parameter combinations  
**Audit window represented by source M1 data:** 2026-10-01 through 2026-10-05 (UTC)

## 1. Scope and interpretation

This report reorganizes the already-published per-position summary. It does not rerun the strategy, reconstruct tick order, or change the audit classifications. The observational unit is a **parameter combination**, not an independent trade. Each position contributes 600 combinations.

The audit does not calculate P/L, R, win rate, profit factor, drawdown, rankings, or preferred settings. It does not model order execution or assume 2X fills, volume changes, average-price changes, or broker fill semantics. No canonical rule is created.

## 2. Classification totals

| Classification | Rows | Share of 21,600 |
|---|---:|---:|
| AMBIGUOUS | 18,120 | 83.89% |
| SINGLE_LEVEL_TOUCH_ORDER_NOT_PROVEN | 1,080 | 5.00% |
| NO_LEVEL_TOUCH_OBSERVED | 2,400 | 11.11% |
| **Total** | **21,600** | **100.00%** |

Position-level distribution:
- 28 positions have all 600 combinations classified AMBIGUOUS.
- 4 positions have a mixed AMBIGUOUS / single-level classification.
- 4 positions have all 600 combinations classified NO_LEVEL_TOUCH_OBSERVED.
- 4 positions contain at least one SINGLE_LEVEL_TOUCH_ORDER_NOT_PROVEN combination.

These are counts of position summaries; they are not additional independent samples.

## 3. Main ambiguity mechanisms

| Diagnostic flag | Rows | Share of all combinations |
|---|---:|---:|
| TRAIL_ACTIVATION_LEVEL_TOUCHED | 17,040 | 78.89% |
| UPDATED_TRAIL_SL_TOUCHED_SAME_BAR | 17,040 | 78.89% |
| PRE_UPDATE_SL_LEVEL_TOUCHED | 2,160 | 10.00% |
| TP_LEVEL_TOUCHED | 600 | 2.78% |
| 2X_LEVEL_TOUCHED | 2,490 | 11.53% |
| 2X_AND_EXIT_LEVEL_SAME_BAR | 1,470 | 6.81% |
| NO_EXIT_LEVEL_TOUCH_IN_OBSERVED_WINDOW | 2,400 | 11.11% |

The trail mechanism is the dominant recorded ambiguity: activation and the updated trailing stop are both touched within the same M1 bar in 17,040 combinations. M1 OHLC does not establish the intrabar ordering needed to prove whether the update preceded the stop touch.

2X level-touch is diagnostic only. 1,470 combinations record a 2X-level touch and an exit-level touch in the same bar. This is not evidence that a second order was filled or that the position size or average entry changed.

## 4. Position-level timing and ambiguity inventory

The two timestamp columns below are independently aggregated earliest timestamps from each position's 600 combinations. They are **not paired observations**. Comparing them does not establish event order for an individual parameter combination. Blank means no timestamp was recorded for that event in the position summary.

| Position | Side | Ambiguous | Single touch | No touch | Trail-update/same-bar | 2X-before-candidate field | Earliest candidate bar (UTC) | Earliest 2X touch (UTC) |
|---|---|---:|---:|---:|---:|---:|---|---|
| 62458477 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-01 16:44:00 UTC | — |
| 62466595 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-01 17:26:00 UTC | — |
| 62472493 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-01 17:56:00 UTC | — |
| 62479760 | SELL | 300 | 300 | 0 | 0 | 300 | 2026-10-01 18:38:00 UTC | 2026-10-01 18:37:00 UTC |
| 62483102 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-01 18:53:00 UTC | — |
| 62486473 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-01 19:25:00 UTC | — |
| 62488249 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-01 19:41:00 UTC | — |
| 62491448 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-01 20:11:00 UTC | — |
| 62492610 | BUY | 0 | 0 | 600 | 0 | 0 | — | — |
| 62497786 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-01 21:15:00 UTC | — |
| 62499705 | BUY | 300 | 300 | 0 | 0 | 300 | 2026-10-01 22:07:00 UTC | 2026-10-01 21:50:00 UTC |
| 62503253 | BUY | 600 | 0 | 0 | 600 | 300 | 2026-10-01 23:04:00 UTC | 2026-10-01 23:04:00 UTC |
| 62506281 | BUY | 420 | 180 | 0 | 240 | 300 | 2026-10-02 03:01:00 UTC | 2026-10-02 03:01:00 UTC |
| 62507768 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 03:40:00 UTC | — |
| 62510782 | BUY | 0 | 0 | 600 | 0 | 0 | — | — |
| 62511473 | BUY | 600 | 0 | 0 | 600 | 90 | 2026-10-02 05:21:00 UTC | 2026-10-02 05:24:00 UTC |
| 62512516 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 06:09:00 UTC | — |
| 62516401 | BUY | 0 | 0 | 600 | 0 | 0 | — | — |
| 62516729 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 08:28:00 UTC | — |
| 62518329 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 08:50:00 UTC | — |
| 62521529 | SELL | 600 | 0 | 0 | 600 | 300 | 2026-10-02 09:25:00 UTC | 2026-10-02 09:22:00 UTC |
| 62540713 | SELL | 300 | 300 | 0 | 0 | 300 | 2026-10-02 12:49:00 UTC | 2026-10-02 12:49:00 UTC |
| 62546910 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 13:38:00 UTC | — |
| 62552588 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 14:44:00 UTC | — |
| 62555855 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 15:21:00 UTC | — |
| 62585649 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 16:46:00 UTC | — |
| 62592622 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 17:25:00 UTC | — |
| 62594268 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 17:33:00 UTC | — |
| 62598298 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 17:57:00 UTC | — |
| 62604959 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 18:30:00 UTC | — |
| 62614431 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 19:49:00 UTC | — |
| 62615799 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 20:11:00 UTC | — |
| 62618151 | BUY | 600 | 0 | 0 | 600 | 0 | 2026-10-02 20:37:00 UTC | — |
| 62623643 | BUY | 600 | 0 | 0 | 600 | 300 | 2026-10-02 22:04:00 UTC | 2026-10-02 22:03:00 UTC |
| 62624533 | SELL | 0 | 0 | 600 | 0 | 300 | — | 2026-10-02 22:20:00 UTC |
| 62625703 | SELL | 600 | 0 | 0 | 600 | 0 | 2026-10-02 22:42:00 UTC | — |

## 5. Data-window and partial-bar caveats

- Entry-minute partial exclusion is recorded for all 21,600 rows. The partial entry-minute OHLC was excluded from the scan.
- Exit-minute partial inclusion as a whole bar is recorded for 21,000 rows. This can expose price movement that occurred after the actual exit timestamp; it is a known observation-window limitation, not proof of a tradable event.
- The remaining 600 rows are associated with the one position whose exit minute was not partial in this summary.
- Maximum missing M1 minutes reported across positions: 0. All position summaries report entry and exit minute bars present.
- A position with zero inspected bars and NO_LEVEL_TOUCH_OBSERVED must not be interpreted as evidence that no price level was touched in the full market path; it means no candidate exit-level touch was observed within the audit's inspected window.

## 6. What this establishes — and what it does not

**Established by this diagnostic**
1. The legacy M1 replay contains extensive same-bar ordering ambiguity, especially around trailing-stop updates.
2. 2X-level touches and same-bar 2X/exit collisions occur in a subset of parameter combinations and require finer-grained event data to resolve.
3. Partial-minute handling is systematic and must remain visible in any later replay interpretation.

**Not established**
1. The actual tick sequence inside any ambiguous M1 candle.
2. Whether a trailing-stop modification would have been accepted by the broker before a later price touch.
3. Whether a 2X pending order would have filled, its filled volume, or the resulting average entry.
4. Any counterfactual P/L, performance improvement, optimal parameter, or statistically validated edge.

## 7. Evidence required for the next resolution step

Prioritize tick-level reconstruction for:
- combinations with `UPDATED_TRAIL_SL_TOUCHED_SAME_BAR`;
- combinations with `2X_AND_EXIT_LEVEL_SAME_BAR`;
- cases with `PRE_UPDATE_SL_LEVEL_TOUCHED` and a competing 2X touch;
- exit-minute partial cases where the M1 candle extends beyond the actual exit timestamp.

Tick data alone may still be insufficient to reproduce broker execution. Any execution claim would additionally require timestamped order-send/modify acknowledgements, broker retcodes, order/deal history, bid/ask-side prices, and the applicable symbol stop/freeze constraints. Until those are reconciled, keep path ordering and fill semantics unresolved.

## 8. Reproducibility metadata

- Source audit type: `OFFLINE_INTRABAR_AMBIGUITY_AUDIT_ONLY`
- Source rows: `21600`
- Positions: `36`
- Variants per position: `600`
- Row unit: `parameter_combination_not_independent_trade`
- P/L computed: `false`
- Execution modeled: `false`
- Fill semantics assumed: `false`
- Canonical rules created: `false`

**Conclusion:** retain the original M1 matrix as a historical diagnostic only. Do not use its counterfactual outputs to claim live performance or select production settings. Resolve the source/execution semantics and reconstruct ambiguous paths from timestamped tick and broker evidence before any performance comparison.
