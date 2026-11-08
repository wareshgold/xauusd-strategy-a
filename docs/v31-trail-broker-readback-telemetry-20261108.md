# V3.1 Trailing Broker Readback Telemetry

**Status:** Isolated research implementation; draft review only  
**Canonical status:** Non-canonical  
**Runtime status:** Not deployed; current Runner must remain stopped until operator-approved review and pull.

## Scope

Capture append-only evidence around each existing V3.1 trailing SLTP request:

1. `TRAIL_REQUEST` immediately before the existing `order_send`.
2. `TRAIL_RESPONSE` immediately after the API returns.
3. `TRAIL_BROKER_OBSERVATION` from read-only `positions_get(ticket=...)`.
4. `TRAIL_VERIFICATION` comparing the requested SL with the observed SL.

Each event carries a deterministic `trail_cycle_id` and a unique `trail_attempt_id`. Retries retain the cycle ID and receive a new attempt ID.

## Status semantics

- `CONFIRMED_MATCH`: ticket-scoped readback returned an SL matching the requested SL within half a broker tick (or half the displayed digit unit, whichever is larger).
- `OBSERVED_MISMATCH`: readback succeeded, but the observed SL differs from the request.
- `POSITION_NOT_FOUND`: ticket-scoped readback returned no matching position.
- `OBSERVATION_FAILED`: readback returned `None` or raised; MT5 last-error detail is recorded where available.

API success and broker readback are separate facts. A successful API retcode is not treated as state confirmation. A readback failure is not treated as an SL failure. Missing evidence remains unknown.

## Non-interference boundary

This change does not alter:
- entry detection or order submission;
- trailing activation threshold, favorable-extreme calculation, or distance;
- completed-bar selection;
- quote/stop/freeze guards;
- retry eligibility, attempt limits, or cooldown;
- TP, pending-order, or close behavior.

The telemetry helper calls `order_send` exactly once and does not retry. It performs only an additional read-only ticket-scoped position query after the response. Telemetry event-write exceptions are caught and counted in the existing `TRAIL_UPDATE.telemetry_write_failures` field; they do not change the request or retry decision.

## Validation

Synthetic tests cover API success/mismatch, invalid-stops response, `None` response with last-error, readback `None`, readback exception, empty/mismatched ticket result, tick precision, retry correlation IDs, logger failure, and exactly-one-send behavior.

The PR workflow adds this test module and compiles the new helper. CI must pass before any local deployment. No live MT5 call is made by the tests.

## Deployment gate

This branch is not a deployment instruction. Do not merge, pull into the running worktree, or restart a Runner until the operator reviews the PR and explicitly approves deployment.
