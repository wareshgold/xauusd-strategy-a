# SP2L Management Matrix & Forward Runner Checkpoint — 2026-10-28

## Purpose and governance

This checkpoint preserves the research state reached by 2026-10-28. It is a research record, not a canonical strategy specification and not authorization to change live/demo execution. Source meaning outranks backtest performance. No guessed SP2L geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules are promoted to canonical status. The workflow remains: SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.

## Management matrix: historical M1 research

Dataset:
- Path: `data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv` in the Strategy A repository.
- SHA-256: `09FB33790E46539DF7EA072D0796A84F1136B242E32E28B365CCD2C604DD8CAE`.
- 28,815 M1 bars; 553 shared candidates.
- Research assumptions: point 0.01, volume 0.01 lot, contract size $100, commission $0.05/completed trade; M1 spread proxy applied to BUY entry and SELL exit. Swap, slippage, latency, and tick-level intrabar execution excluded. Ambiguous same-bar SL/TP cases excluded from decisive counts.

Scenarios:
- RUNNER: management mode RUNNER, activation_R=2.5, trail_distance_R=3.0.
- BE_0.5R_LOCK_0.05: activation_R=0.5, lock_price=0.05.
- Fairness check: 553/553 shared signals; no differences in entry price, initial SL, or initial risk price; no duplicates.

Reported historical estimates:
- RUNNER: 551 decisive closed; 2 open/unresolved; exits SL=351, TRAIL_SL=200; no ambiguous cases; gross $681.01; spread $121.87; commission $27.55; net $531.59; realized R total 228.7106R.
- BE: 548 decisive closed; 5 ambiguous SL_AND_TP_SAME_BAR; exits BREAK_EVEN_SL=293, TP=133, SL=122; gross $521.49; spread $121.30; commission $27.40; net $372.79.
- Difference in this sample: RUNNER +$158.80. Not apples-to-apples because RUNNER has no fixed TP while BE retains a fixed TP. These results are estimates under the stated assumptions, not proof of a live edge.

Weekly net by exit date (week starts Monday):
- RUNNER: week 2026-08-17 -$38.05 (24 trades); 2026-08-24 +$130.00 (145); 2026-08-31 +$359.22 (124); 2026-09-07 +$82.68 (136); 2026-09-14 -$2.26 (122). Positive 3/5 weeks.
- BE: week 2026-08-17 +$20.14 (25); 2026-08-24 +$129.77 (147); 2026-08-31 +$90.32 (118); 2026-09-07 +$56.17 (135); 2026-09-14 +$76.39 (123). Positive 5/5 weeks.
- Excluding week 2026-08-31: RUNNER $172.37, BE $282.47; BE ahead $110.10.
- RUNNER's three strongest days (Aug 31, Sep 4, Sep 10) contributed $353.96, about 66.6% of its $531.59 net.
- Trade-close-sequence drawdown: RUNNER $123.53; BE $33.66. This is not time-aware portfolio drawdown because positions overlap.
- Leave-one-week-out differences vary; no robust winner established. Do not select canonical management rules from these backtest results.

## July data provenance status

Thirty-three copies named `xauusd-ecn-m1-2026-07.csv` were found across research roots, with three whole-file hashes. Representative copies all had 31,483 data rows and candle range 2026-07-01T01:00:00Z to 2026-07-31T23:57:00Z. Representative file hash prefixes: `073D803C5E8DC437`, `0215C22898AC5B86`, `482991DF85C71430`. All eight checked column hashes matched across representatives (timestamp, OHLC, tick_volume, spread, real_volume); whole-file hashes differ, likely formatting/encoding/line endings, not yet proven.
- July is outside the Aug 21–Sep 19 sample period but is NOT yet certified as an untouched Fresh Holdout because prior use in reports, parameter selection, or rule decisions has not been ruled out.
- Next provenance tasks: search reports/scripts/manifests for July use; audit timestamps, gaps, duplicates, spread and data integrity; preserve source files unchanged.

## Forward runner status observed 2026-10-28 08:30–08:32 local

Root: `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-rr2-trail4`
Runner script: `scripts/run_sp2l_v3_xauusd_forward_test.py`
Event log: `artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl`
State: `runtime/sp2l_v3_xauusd_rr2_trail4_forward_state.json`
Source SHA-256 at inspection: `0FE5B67D33BC93D9A7244C79B951F91E9A00A616960C2AD6DFD4E292611DC873`.
- PID 9420 started 2026-10-27 09:26:23, parent PID 7536, executable `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`.
- PID 10792 started at the same time, parent PID 9420, executable `C:\\Users\\Mr.Mirzaei\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`. Both command lines reference the same runner script. Relationship and reason for child interpreter still need investigation; do not assume two independent runners.
- Event log last write at 2026-10-28 05:57:02; state last write at 08:31:29. These different timestamps alone do not prove runner stopped.
- A 5,000-event tail contained 4,492 `MT5_DEAL_HISTORY_QUERY_FAILED` events. Examples report query `history_orders_get(ticket)`, target tickets, and `MT5 returned None; mt5_last_error=(-2, 'Terminal: Invalid params')`.
- Source search found the main lifecycle query at line 266 using `mt5.history_orders_get(_RUN_STARTED_UTC, datetime.now(timezone.utc), group=symbol)`; the tracked deal collection call is around lines 332–336 and passes `history_orders_get=getattr(mt5, "history_orders_get", None)`. The error text says `history_orders_get(ticket)`; exact call site/signature inside `collect_tracked_deals` still must be inspected before diagnosing or changing it.
- Latest counts within the last 5,000 events: CANDIDATE=47, ORDER_ATTEMPT=47, ORDER_RESULT=47, EXECUTION_BLOCKED=10, PENDING_ORDER_LIFECYCLE=92, POSITION_LIFECYCLE=52, TRAIL_UPDATE=31, DAILY_SUMMARY=3. Last candidate/order result at 2026-10-28T00:49:19Z; last pending lifecycle at 02:27:02Z; last position lifecycle at 00:26:33Z; last trailing update at 00:27:02Z.
- A recent signal was blocked with `LIMIT_ENTRY_NOT_PLACEABLE_AT_CURRENT_MARKET`. A trailing modification logged `success=true`, retcode 10009, comment “Request executed”. These are event records, not a complete current account reconciliation.
- State listed 12 position IDs: 64470852, 64481377, 64482263, 64485969, 64495595, 64500649, 64511757, 64519072, 64530054, 64553029, 64561114, 64562010. These are tracked state IDs and are NOT yet confirmed to be 12 currently open positions or 12 closed trades.

## Safe next steps

1. Preserve runner, event log, state, and source file; no restart, edits, order actions, or parameter changes before diagnosis.
2. Read-only inspect the full `collect_tracked_deals` definition and all call sites to identify the exact `history_orders_get(ticket)` call and its expected API signature. Verify against installed MetaTrader5 package/API docs and tests before proposing a fix.
3. Inspect the parent/child process launch chain and Python interpreter selection without killing either process.
4. Reconcile tracked position IDs with current MT5 open positions and deal/order history via a safe read-only query; distinguish pending, open, closed, and history-query-failed.
5. Continue July provenance/data quality audit. Do not call July a Fresh Holdout until evidence supports that label.
6. No canonical rule or production decision from these diagnostics or backtest matrix alone.

Checkpoint records research and observed state only; it does not certify the runner as healthy or the matrix as statistically validated.
