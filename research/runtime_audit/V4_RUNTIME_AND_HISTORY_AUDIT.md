# V4 Source, Runtime, and MT5 History Audit

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Audit basis:** read-only inspection of supplied `xauusd-strategy-a-rr2-trail4` worktree and snapshot captured 2026-10-28 08:50:36 +03:30.  
**Independent research branch:** `research/strategy-v4-xauusd-20261028`, based at `dac76b09da01f022d745f51328ee703f6fb59851`.

## 1. Source and active-process identity

- Observed repository path: `D:\Mirzaei\Private\1\xauusd-strategy-a-rr2-trail4`.
- Observed branch/HEAD: `fix/rr2-trail4-pending-lifecycle-list-local-20261008` / `dac76b09da01f022d745f51328ee703f6fb59851`.
- Repository remote: `https://github.com/wareshgold/xauusd-strategy-a.git`.
- Initial status contained four modified tracked paths, including the forward-event log and V3 runner; many untracked backups/snapshots also existed. None was staged, discarded, or transferred automatically.
- Target runner on disk SHA256: `0fe5b67d33bc93d9a7244c79b951f91e9a00a616960c2ad6dfd4e292611dc873`, matching the supplied SHA and the 2026-10-28 history snapshot.
- Target helper on disk SHA256: `86eda557b8982a5aa45a30159a20c1c44eeb18f4889f0fe5e9870d8d51337725`, matching the supplied SHA and snapshot.
- Other on-disk observations: generic runner `238ae453292ba4cdfea64e463a0bc93d76040721cd8709df5fba84da725ebdd5`; RR2/TRAIL4 config `f70b0dcc4c50e6d95ffac2e39afb1ca044830027feacfc1d1e21ecdad40e24e8`; failure gate `aace1f4b684b5613ff95534856882e28744c343cbaab5ce0995abe4d9dbe2bfd`.
- Read-only process snapshot observed `terminal64.exe` PID 7860, Python PID 9420 and child PID 10792 running the target script. The two Python processes had same runner path but different executable paths. The process list does not prove the exact bytes of Python modules already loaded in memory: **IN-MEMORY HELPER VERSION UNRESOLVED**.
- No runner, terminal, trading configuration, account or order was stopped, restarted, changed or contacted by this audit or research replay. No live/test orders were sent.

## 2. Runner behavior observed in code (not production certification)

References below are to the captured disk source in `research/source_audit/observed_disk/`.

- Wrapper sets XAUUSD, V3 RR2/TRAIL4 config, pending-limit research mode, TTL=30 minutes, and the all-market-hours gate. `sp2l_v3_rr2_trail4_config.py` encodes a three-candle candidate, numeric P-Gap research threshold 1.0 price units, spike body multiplier 1.5, maximum SL distance 10, TP=2R, trailing distance=4 × 0.10 = 0.40 price, trigger-bar low/high theoretical entry, and pre-spike candle extreme SL. These are code-observed research choices, not canonical rules.
- Wrapper trails from completed M1 candle high/low; requires broker stops/freeze distance against bid/ask; only one attempt per (position, completed bar) key. It logs attempt success/failure. Tick/path within that M1 bar remains unknowable from OHLC.
- Pending expiry considers symbol+magic owned limit orders. It fails closed if it cannot validate a pinned UTC+3 server offset against fresh advancing tick time and a 120-second freshness window. It compares `time_setup` on that assumed server clock with TTL and delegates cancellation; only a confirmed cancellation suppresses subsequent expiry attempts. No cancellation test was executed against live MT5.
- Pending lifecycle adopts active matching symbol/magic limit orders for post-restart lifecycle tracking; records status from active and historical order views.
- Deal history helper resolves tracked order IDs using `history_orders_get(ticket=order_id)`, obtains `position_id`, then queries `history_deals_get(position=position_id)`; it deduplicates on deal ticket, symbol-checks, sorts by `(deal.time, deal.ticket)`, and distinguishes `None`/exception from valid empty results.
- On query error, wrapper writes `MT5_DEAL_HISTORY_QUERY_FAILED`, saves state and defers lifecycle. `HistoryQueryFailureLogGate` suppresses repeated identical `(query,target,detail)` diagnostics until a successful complete poll. Therefore error-event counts reflect log-gate history, not guaranteed raw API call counts.
- Entry deal sends lifecycle Telegram and marks deal seen only after successful send. Failed send saves state and breaks so a later poll retries and chronological delivery is maintained; a process crash after remote delivery but before local state save can still duplicate delivery. Not exactly-once.
- Position-entry lookup uses position history without a range first and a date-range fallback filtered by position; entry deals also require runner magic. Close notification is deferred when entry cannot be linked.

## 3. History-query findings

Captured event file: `research/source_audit/observed_disk/artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl` (11,448,573 bytes; SHA256 `dc0b5ef20bfb61987095fc9f87095fbd85bbfe261705a2fbf64aa3533fac69a0`).

- 34,379 logged `MT5_DEAL_HISTORY_QUERY_FAILED` events total:
  - `history_orders_get`: 10 events, one target (63440809), on 2026-10-14 12:24:07–12:24:25 UTC, `None` with no last-error detail.
  - `history_deals_get(ticket)`: 34,346 events, targets 63440809 and 63487497, 2026-10-14 12:24:27 through 2026-10-15 09:54:49 UTC, `None`; corresponds to an earlier helper path. The overwhelming count is observed telemetry, not necessarily raw query count, because versions/log gate changed over time.
  - `history_orders_get(ticket)`: 23 events, 23 distinct targets, each logged once, 2026-10-15, 16, 26–28; detail consistently `MT5 returned None; mt5_last_error=(-2, 'Terminal: Invalid params')`.
- Episode count uses a descriptive, not causal, rule: split same-query/same-target failures when adjacent event times differ by >180 seconds. That yields one episode for the 10 old `history_orders_get` records, two episodes for old `history_deals_get(ticket)` (one per target), and 23 episodes for new `history_orders_get(ticket)` (distinct targets, single report each). This does not measure unlogged calls.
- Old `history_deals_get(ticket=order_id)` semantics are evidenced by helper source comments and the 2026-10-28 captured history matrix: on the same MT5 terminal, tested `history_deals_get(ticket=<order-like id>)` returned `None` with `(-2, 'Terminal: Invalid params')`; `history_orders_get(ticket=...)` and `history_deals_get(position=...)` succeeded for selected older IDs. That demonstrates the selected call-form mismatch for those tested examples, not the cause of every historical error.
- The later `history_orders_get(ticket)` `Invalid params` failure **cause is UNRESOLVED**. Possibilities include API binding/context semantics, ticket not accepted/available in that exact terminal state, data/history availability, target type/value/context, state inconsistency, or terminal/server behavior. No one possibility is proven.
- For each of the six supplied IDs (64485969, 64511757, 64519072, 64530054, 64561114, 64562010), one `history_orders_get(ticket)` error is logged. Every ID appears in captured `state.orders` and `state.positions`, not in `state.deals`. Event history first records these as order results/pending lifecycle; then query failure; then position lifecycle and deal lifecycle events within approximately 3–10 seconds. Actual deal ticket values differ from the shared-looking order/position IDs. Later lifecycle progress does not establish why the initial order-history query failed.
- Snapshot `mt5_history_matrix_results.json` tested IDs 64470852, 64471071, 64481377, 64481443, 64482263, and several positions. It observed `history_orders_get(ticket)` success and `history_deals_get(position)` success for tested earlier chains; its helper live-test returned 10 deals. It did not test any of the six supplied IDs and cannot be generalized to them.

## 4. Event log and state audit

- 39,886 JSONL events; all parse; 19 event types, each with one observed key schema; no exact duplicate full event records.
- Timestamps parse on all lines; first 2026-10-01 10:01:08.808053 UTC, last 2026-10-28 02:27:02.246297 UTC; no adjacent timestamp inversions; 317 zero-second adjacent intervals, 474 intervals >60 seconds and 56 >1 hour. Log interval is sparse event telemetry, not a continuous poll trace.
- Counts: START 30; START_TELEGRAM 30; SESSION_GATE 150; CANDIDATE 150; ORDER_ATTEMPT 150; ORDER_RESULT 150; TELEGRAM_SIGNAL 118; POSITION_LIFECYCLE 164; PENDING_ORDER_LIFECYCLE 257; TRAIL_UPDATE 99 (91 success, 8 failure); EXECUTION_BLOCKED 32; TELEGRAM_DEAL_LIFECYCLE 2,647; TELEGRAM_SIGNAL_RETRY 1,302; DAILY_SUMMARY 60; PENDING_ORDER_TTL_SKIPPED 26; SESSION_CUTOFF_DEFERRED 138; PENDING_ORDER_EXPIRED 2; TELEGRAM_PENDING_EXPIRED 2; MT5_DEAL_HISTORY_QUERY_FAILED 34,379.
- State at snapshot: 24 order IDs, 12 position IDs, 24 deal IDs, 51 order-state markers, 12 `position_orders` map keys, 12 `signal_orders` map keys. State is a current capped/reconciled snapshot, not a complete historical ledger. Historical event log contains more than 12 positions and 2,647 deal lifecycle messages; state/event count mismatch is expected from state capping and event history and cannot alone establish missing events.
- Event schema cannot independently establish every event category asked for: explicit partial-fill lifecycle is NOT_PROVABLE; a general cancel/reject taxonomy is incomplete; exact position/order/deal relation is sometimes only inferable from linked event fields; broker deal history was not queried by this audit. No claim is made that all lifecycle events are represented.
- `PENDING_ORDER_TTL_SKIPPED`=26 and `SESSION_CUTOFF_DEFERRED`=138 are safety-gate telemetry. They indicate no action at those observations; suppressed or rate-limited repeats may exist.
- All preserved snapshot files are copied without modification under `research/manifests/original_history_snapshot_20261028_085035/`. `research/runtime_audit/raw_event_summary.json` and `event_type_counts.csv` contain counts.

## 5. Evidence that remains unresolved/not tested

- Root cause of new `history_orders_get(ticket)` errors; live-memory helper version; complete unlogged error count; read-only reproduction for the six target IDs is not run because it would require connecting to the active MT5 terminal and could interfere with the live runner.
- Real pending placement/cancel/reject/partial-fill semantics; exact expiry behavior under server clock/DST changes; open position SL/TP broker outcomes; exact Telegram duplicate behavior across process crashes.
- Canonical executable P-Gap formula, AB=CD A/B/C/D anchors/tolerance, exact source-to-OHLC fill, broker costs, slippage and spread-unit conversion.
- No production inference, live BUY/SELL signal, or strategy promotion.
