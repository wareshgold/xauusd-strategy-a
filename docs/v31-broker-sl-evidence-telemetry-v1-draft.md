# V3.1 Broker-Side SL Evidence Telemetry — V1 Draft

**Status:** Research/documentation draft; not approved for implementation  
**Scope:** Evidence capture for existing SL modification attempts only  
**Execution safety:** No change to entry, exit, activation, distance, retry, or order-management behavior  
**Canonical status:** Non-canonical; telemetry does not define SP2L geometry or trading rules

## 1. Code review baseline

Reviewed GitHub source branch: `fix/v31-trailing-live-quote-retry-20261103`.

Relevant files:
- `scripts/run_sp2l_v3_1_xauusd_forward_test.py`
- `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
- `scripts/sp2l_trailing_rules.py`

Observed current flow:

1. `trail_positions()` calls the original `monitor_position_lifecycle()`.
2. The original monitor calls `mt5.positions_get(symbol=symbol)`.
3. It emits `POSITION_LIFECYCLE` only when the Position SL/TP marker has not already been recorded in `state["order_states"]`.
4. Trailing reads positions, evaluates the completed M1 bar, refreshes symbol/quote constraints, and sends `TRADE_ACTION_SLTP` through `mt5.order_send()`.
5. Only after the send returns does it emit `TRAIL_UPDATE`.

### Confirmed instrumentation gaps

- No unique identifier links one SL modification request to its response and subsequent Position readback.
- No event is written immediately before `order_send()`; a crash around the call can leave no explicit request record.
- `TRAIL_UPDATE` records the response result, but not a separately queried post-request SL value.
- `attempt_number` exists, but is not a globally unique attempt identifier.
- `POSITION_LIFECYCLE` is change-triggered/deduplicated, not a record of every poll or every post-request observation.
- The base monitor uses `mt5.positions_get(symbol=symbol) or []`; therefore `None` (query failure) and an empty result (valid no-position result) are collapsed in that path.
- The reviewed V3.1 trailing path collapses `positions_get()` returning `None` into an empty list; a sibling current-base snapshot instead returns silently on `None`. Neither path emits a dedicated observation-failure event.

These findings explain why absence of a later `POSITION_LIFECYCLE` event cannot be interpreted as proof that no broker readback occurred or that the SL modification failed.

## 2. Proposed correlation model

For every actual `order_send(TRADE_ACTION_SLTP)` call:

- `trail_cycle_id`: deterministic grouping key for symbol + position + completed-bar timestamp.
- `trail_attempt_id`: unique ID for this individual send attempt.
- `attempt_number`: existing retry ordinal, retained for readability.
- `position_id`, `symbol`, `magic`, `runner_version`, `config_hash`: identity/provenance fields where available.

A retry gets a new `trail_attempt_id`, the same `trail_cycle_id`, and its own `attempt_number`. Do not use MT5 `order` or `deal` identifiers as the primary correlation key for an SLTP modification.

## 3. Proposed append-only event sequence

### A. `TRAIL_REQUEST` — immediately before the API call

Capture:
- correlation IDs and Position identity
- `old_sl`, `requested_sl`, `tp`
- completed-bar timestamp and attempt number
- bid/ask, point, tick size, digits
- stops level, freeze level, computed minimum distance
- request timestamp in UTC

The event must describe the exact request values passed to MT5, not recomputed display values.

### B. `TRAIL_RESPONSE` — immediately after the API call returns

Capture:
- correlation IDs
- whether the API returned an object
- retcode and comment when available
- `mt5.last_error()` when the API returns `None`
- response timestamp in UTC
- reported API success as a separate field

An API success response is not itself a Position-state confirmation.

### C. `TRAIL_BROKER_OBSERVATION` — read-only Position readback

After the response, query the same Position by ticket if supported by the installed MT5 Python API. Capture:
- correlation IDs
- observation timestamp in UTC
- query outcome: `OK`, `QUERY_FAILED`, or `POSITION_NOT_FOUND`
- observed SL/TP and Position identity fields when found
- MT5 last-error details when the query fails

Do not collapse `None` and an empty result. Do not substitute requested SL, old SL, or zero for an unavailable observation.

### D. `TRAIL_VERIFICATION` — deterministic comparison

Capture:
- correlation IDs
- requested SL and observed SL
- comparison basis (symbol digits/tick size)
- verification status:
  - `CONFIRMED_MATCH`
  - `OBSERVED_MISMATCH`
  - `POSITION_NOT_FOUND`
  - `OBSERVATION_FAILED`
  - `PENDING_OBSERVATION`

A later routine Position snapshot may be linked to the same `trail_cycle_id` if a subsequent-observation policy is approved. Do not silently treat an unrelated snapshot as confirmation.

## 4. Interpretation rules

- `TRAIL_RESPONSE` success means the API reported success only.
- `CONFIRMED_MATCH` means a separate MT5 Position readback returned the requested SL for the same Position after the request.
- `OBSERVED_MISMATCH` is an observed discrepancy, not permission to retry or change trading behavior.
- `POSITION_NOT_FOUND` is not equivalent to a failed modification; the Position may have closed before readback.
- `OBSERVATION_FAILED` is a telemetry/query failure, not an SL failure.
- Missing events remain `UNKNOWN`; never infer success or failure from absence alone.
- These are broker-terminal state observations through MT5, not a second independent market-data source or a claim of exchange-level confirmation.

## 5. Non-interference requirements

The eventual implementation must be telemetry-only:
- Do not change the trailing formula, activation threshold, distance, bar selection, quote guard, retry policy, or attempt limits.
- Do not add an automatic retry based on verification status.
- Do not block or permit an SL request based on the new verification result.
- Do not change entry, TP, pending-order, or close logic.
- Preserve the existing event schema and add versioned event types/fields.
- No account login, password, access token, or other credentials in evidence events.

Logging failure policy must be reviewed before implementation. Telemetry must not silently alter order-management behavior; if evidence cannot be written, record/raise an explicit telemetry-health condition through a separately reviewed mechanism rather than changing the SL decision path.

## 6. Synthetic test matrix

Use mocked MT5 responses only; no live account or broker calls.

1. API returns DONE; readback returns requested SL.
2. API returns DONE; readback returns a different SL.
3. API returns non-DONE; readback remains old SL.
4. API returns `None`; response includes last-error details.
5. Readback returns `None` (query failure).
6. Readback returns an empty collection (Position not found).
7. Retry sequence: same cycle ID, distinct attempt IDs, increasing attempt numbers.
8. Restart/replay: request without response remains incomplete and is not auto-classified.
9. Duplicate event replay is detected without deleting or rewriting source events.
10. BUY and SELL values compare correctly at the instrument tick precision.
11. Logging/serialization exceptions do not change the SL calculation or retry decision.
12. Existing trailing-rule tests remain unchanged and pass.

## 7. Evidence package impact

For each attempt, the audit should be able to report:
- request count
- response count
- response success/failure/unknown counts
- readback success/failure/not-found counts
- exact requested-SL matches
- observed mismatches
- incomplete sequences
- duplicate or orphan events

The 43 existing `MT5_DEAL_HISTORY_QUERY_FAILED` events are a separate Deal-history observability issue. They must not be conflated with SL readback failures. Their impact requires a separate breakdown by query, target, and error detail.

## 8. Approval gates

This draft is not implementation authorization. Before code changes:
1. Review the event contract and non-interference policy.
2. Confirm the installed MT5 Python API supports the proposed ticket-scoped readback.
3. Confirm timestamp precision and tick-size comparison rules.
4. Approve the logging-failure policy.
5. Implement only on an isolated branch.
6. Run synthetic tests and the existing regression suite.
7. Review the diff for zero changes to trading decisions.
8. Keep deployment separate; no live Runner restart without explicit operator approval.
