# V3.1 Evidence Collection — Read-Only Code Audit

**Date:** 2026-11-08  
**Status:** Research audit; no runtime or trading changes  
**Reviewed source branch:** `fix/v31-history-query-helper-import-20261102`

## 1. Trailing evidence path

The V3.1 wrapper calls the original Position lifecycle monitor before evaluating/sending a trailing update. The base monitor reads `positions_get(symbol=...)` and emits a `POSITION_LIFECYCLE` event only for a previously unseen Position SL/TP marker stored in `state["order_states"]`.

Consequences:
- `POSITION_LIFECYCLE` is change-triggered/deduplicated telemetry, not a record of every polling observation.
- A later lifecycle event with the requested SL is useful readback corroboration.
- Absence of a later lifecycle event is inconclusive: it can reflect no changed marker, a closed/not-found Position, a failed read, or a missing poll/event.
- In the reviewed branch, the base monitor collapses `positions_get() is None` into an empty list. The trailing path also uses an empty-list fallback in that branch. This does not preserve the MT5 distinction between query failure and a valid empty result.

The trailing code emits `TRAIL_UPDATE` after `order_send(TRADE_ACTION_SLTP)`. It includes retcode/comment and a boolean derived from `TRADE_RETCODE_DONE`, but there is no unique per-send ID, pre-send request event, or immediate readback linked to that send.

## 2. Deal-history query failure semantics

The reviewed helper modules are:
- `scripts/sp2l_tracked_deal_history.py`
- `scripts/sp2l_history_query_failure_log.py`

### Query behavior

`collect_tracked_deals()` performs targeted history queries:
1. For each tracked order, optionally calls `history_orders_get(ticket=order_id)`.
2. For each tracked order, calls `history_deals_get(ticket=order_id)`.
3. For each known/linked Position ID, calls `history_deals_get(position=position_id)`.

The helper treats an empty tuple/list as a valid empty result. Exceptions and `None` are raised as `DealHistoryQueryError` with query, target ID, and MT5 last-error details where available.

A failure aborts that collection pass. The V3.1 caller logs the diagnostic (subject to deduplication), saves state, and returns without processing the partial deal list. A later polling pass can retry. A complete successful collection clears the failure-log gate.

### Meaning of the 43 archived diagnostics

The failure gate keys diagnostics by `(query, target, detail)` and emits each distinct key once until a complete collection pass succeeds. Repeated identical failures during that interval are suppressed; after a successful pass, the same failure can be emitted again if it recurs.

Therefore:
- 43 `MT5_DEAL_HISTORY_QUERY_FAILED` events are 43 emitted diagnostic records.
- They are **not** necessarily 43 total failed API calls.
- They are **not** necessarily 43 separate polling cycles.
- The count alone cannot produce a failure rate or prove the final MT5 history is incomplete.
- Each event indicates a history-collection pass was deferred at that point; the error's `query`, `target`, and `detail` fields are needed to characterize the failure.

The safe caller behavior is important: a query failure is not silently converted into an empty history result, and lifecycle processing is deferred for that pass.

## 3. Separate observability gaps

The 43 Deal-history diagnostics do not measure Position readback failures. The Position lifecycle monitor has its own `positions_get()` path and currently does not emit a distinct query-failure event when MT5 returns `None`.

Thus the current evidence package has two separate questions:
- Deal history collection reliability: represented by `MT5_DEAL_HISTORY_QUERY_FAILED`.
- Position/SL readback reliability: not fully represented by a dedicated query outcome event.

Do not combine these into one failure count.

## 4. Next analysis required for the archived package

Aggregate the 43 events by:
- `query`
- `target` (report count and number of distinct target IDs)
- normalized `detail` / MT5 last-error code
- event time bucket (to identify recurrences after successful intervals)

Do not publish raw ticket IDs in the summary. Report only counts and anonymized error categories.

Also calculate:
- total distinct tracked order IDs and Position IDs queried
- number of complete collection passes, if pass boundaries can be reconstructed
- number of failures per query family
- whether each target later appears in a successful collection or final MT5 history

If pass boundaries cannot be reconstructed from the event log, explicitly label failure rates as unavailable.

## 5. Non-interference boundary

This audit is diagnostic only. It does not authorize changes to the active Runner, MT5 calls, trailing retries, order execution, or Strategy A rules. Any telemetry patch must remain isolated, synthetic-tested, reviewed for zero decision-path changes, and separately approved before deployment.
