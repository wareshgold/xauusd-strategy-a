# Dashboard Forensic Snapshot — 2026-11-10

## Purpose and safety boundary

Checkpoint for the V3.1 Dashboard investigation. This is a research/diagnostic snapshot only.

- Do not stop, restart, kill, or reconfigure the Runner or MT5 terminal.
- Do not initialize or shut down MT5 from diagnostic processes.
- Do not alter live execution code, orders, positions, or Runner state.
- Dashboard changes must remain file-only, read-only, isolated, and tested before any deployment.
- No canonical SP2L geometry or trading rule is changed by this work.

## Live observations supplied by the user

Dashboard API: `http://127.0.0.1:8791/api/status`

- Dashboard version: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`
- Runner reported alive: `true`; reported Runner PID: `8312`
- Earlier process inventory identified Dashboard monitor PID `6356`, running:
  `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-dashboard-v3-20261103\\scripts\\sp2l_v31_rr4_act40_monitor.py`
- Event file:
  `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-trailing-retry-20261103\\artifacts\\forward-test\\SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl`
- Event lines: `1519`; malformed: `0`; read error: none.
- State age at observation: approximately `2 seconds`.
- Dashboard diagnostic counts at observation: ERROR `17`, WARNING `66`, INFO `17`.

These are point-in-time observations from the user's machine, not a continuous health guarantee.

## Confirmed Dashboard code finding

Reviewed monitor source:
- Repository: `wareshgold/xauusd-strategy-a`
- File: `scripts/sp2l_v31_rr4_act40_monitor.py`
- Branch: `research/v31-dashboard-local-monitor-20261104`
- Blob SHA: `29767dd7e9502f701ada0b5b730066bf83d07b82`

In `_build_diagnostics()`, the generic event detail construction currently collects selected keys such as `retcode`, `comment`, `last_error`, `reason`, retry fields, and nested result fields. It does not include the source event's `query`, `target`, or `detail` fields. Consequently, generic diagnostics for `MT5_DEAL_HISTORY_QUERY_FAILED` display only a generic message and hide the actual MT5 error payload.

**Dashboard fix scope:** preserve and render the original source `detail` plus `query` and `target` in the diagnostic detail; add focused tests. Keep the monitor filesystem-only and do not introduce MT5 access.

## Runtime evidence: history query failures

Two latest examples supplied by the user:

1. UTC `2026-11-10T05:17:24.553962+00:00`
   - event: `MT5_DEAL_HISTORY_QUERY_FAILED`
   - query: `history_orders_get`
   - target: `65628271`
   - detail: `MT5 returned None; MT5 last_error=(-2, 'Terminal: Invalid params')`

2. UTC `2026-11-10T08:20:07.216743+00:00`
   - event: `MT5_DEAL_HISTORY_QUERY_FAILED`
   - query: `history_orders_get`
   - target: `65639448`
   - detail: `MT5 returned None; MT5 last_error=(-2, 'Terminal: Invalid params')`

Interpretation status:
- Confirmed: MT5 rejected these history query calls with Invalid params.
- Not yet confirmed: whether the caller supplied a position identifier where an order ticket was required, or another invalid argument. This requires inspection of the exact local Runner source and call site.
- Do not change Runner code until the call path, identifier semantics, and relevant MT5 API signature are verified offline.

## Runtime evidence: deferred trailing

Two latest `TRAIL_DEFERRED` events supplied by the user:

1. UTC `2026-11-10T06:25:00.782798+00:00`
   - position: `65631028`, direction: SELL
   - normalized SL: `4122.33`
   - Ask: `4123.48`
   - SL is `1.15` below Ask (wrong side for a SELL stop-loss at that observed quote).

2. UTC `2026-11-10T08:22:01.432972+00:00`
   - position: `65639448`, direction: SELL
   - normalized SL: `4116.46`
   - Ask: `4116.99`
   - SL is `0.53` below Ask (wrong side for a SELL stop-loss at that observed quote).

Both events report:
- reason: `CURRENT_QUOTE_OR_BROKER_DISTANCE`
- stops_level: `0`
- freeze_level: `0`
- min_distance: `0.0`

Important: zero reported broker stop/freeze distance does not make a SELL SL valid when it is below the current Ask. The two samples are consistent with the quote having crossed the proposed stop level before modification. This is evidence about these two events only, not proof of the complete trailing algorithm's correctness.

The user's query for the last two `TRAIL_DEFERRED_RECOVERED` events returned no rows. Therefore these two deferred examples have no recovery confirmed by the supplied output. Do not label them recovered.

## Work completed in this investigation

- Confirmed port `8791` is the active Dashboard endpoint; port `8792` had no listener in the earlier process check.
- Confirmed API responds and reports fresh state/event data.
- Identified that Dashboard's generic diagnostics omit important source fields.
- Extracted two concrete history-query failures and two deferred trailing examples.
- No Runner/MT5 action, restart, execution change, or live file modification was performed.

## Open work — next sequence

1. **Dashboard-only patch (isolated branch/worktree):**
   - Include original event `detail`, `query`, and `target` in diagnostic detail.
   - Ensure detail is escaped safely in HTML.
   - Add regression tests for `MT5_DEAL_HISTORY_QUERY_FAILED` proving all three fields appear.
   - Keep monitor read-only; no MT5 imports or initialization.
2. **Offline Runner source audit:**
   - Inspect the exact local source used by the active Runner under
     `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-trailing-retry-20261103`.
   - Trace the `history_orders_get` caller, target identifier origin, argument shape, and error handling.
   - Compare with the already-fixed history-helper behavior; do not assume the old defect is identical.
   - Report findings before proposing any Runner change.
3. **Offline trailing audit:**
   - Trace how SELL trailing SL is calculated and normalized.
   - Determine whether a quote-crossed candidate is expected to defer and whether the retry lifecycle later records success.
   - Use immutable copies/log evidence; do not interact with MT5.
4. Run focused Dashboard tests, record test output and hashes, then prepare a reviewable PR. Do not deploy or restart the active Dashboard without the user's explicit go-ahead.

## Resume point

Start with item 1 (isolated Dashboard diagnostics patch), while separately auditing the Runner source read-only. Preserve the live processes and all existing user work.
