# SP2L RR2/TRAIL4 Telegram Lifecycle Fix Snapshot — 2026-10-13

## Scope
Research/demo forward-notification reliability only. No Strategy A geometry, entry/exit rules, order sizing, or trade-execution semantics changed.

## Changes on this branch
- `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
  - Formats broker deal timestamps as UTC epoch -> Iran UTC+03:30 directly. It no longer subtracts the inferred MT5 server offset from `deal.time`.
  - The signal notification now explicitly says `PENDING ORDER ACCEPTED (NOT FILLED)`, distinguishing a live pending order from an actual entry deal.
  - An execution-blocked candidate sends an `ORDER NOT PLACED` notification with the gateway reason. Failed blocked-order notifications are persisted and retried on subsequent polls.
- `scripts/run_sp2l_v3_xauusd_forward_test.py`
  - Persists each successfully acknowledged lifecycle deal immediately.
  - Ensures the first unavailable session-clock observation is logged deterministically, independent of host monotonic uptime; this was exposed by the existing focused CI suite.
  - If a lifecycle Telegram send fails, stops processing later deals in that poll. This prevents a CLOSED notification from overtaking an OPENED notification that is waiting for retry.
  - Failed lifecycle messages remain unmarked and eligible for retry on the next poll.
- `tests/test_sp2l_v3_pending_expiry.py`
  - Added regression tests for the expected UTC+03:30 deal time and for retry/order preservation (OPENED before CLOSED).
  - Added tests asserting that pending-order messages explicitly say NOT FILLED and blocked execution messages report ORDER NOT PLACED with the gateway reason.
- This snapshot documents the handoff.

## Expected notification flow
1. A candidate passes the configured gates and broker order submission succeeds; the signal message states that the pending order is accepted but NOT FILLED. A failed signal notification is kept in `pending_signal_notifications` and retried.
1a. If submission is blocked/rejected, an `ORDER NOT PLACED` Telegram message includes the execution reason; failed sends are kept in `pending_execution_notifications` and retried.
2. The actual broker entry deal is detected from MT5 history; an OPENED lifecycle message is sent.
3. The actual broker exit deal is detected; a CLOSED message is sent with broker-derived result data.
4. Failed lifecycle sends are retried on subsequent polls. Later lifecycle deals do not leapfrog a failed earlier deal.

## Guarantees and limitations
- GitHub Actions `SP2L forensic deterministic checks` passed on the current code before this snapshot refresh: detector consistency PASS, reconciliation tests 2 passed, and pending/lifecycle suite 34 passed. Run: https://github.com/wareshgold/xauusd-strategy-a/actions/runs/38356949233.
- Telegram Bot API does not provide a general idempotency key for `sendMessage`; if Telegram accepts a message but the response is lost, duplicate delivery remains possible. The changes reduce local replay windows but cannot promise exactly-once delivery.
- Delivery latency depends on network/API responsiveness. This change does not claim a hard real-time guarantee.
- No live MT5 order was placed or modified by these changes.

## Deployment / forward-test handoff
- `ORDER NOT PLACED` means the gateway did not confirm an accepted order; it is distinct from a pending order that was accepted but has not filled. `OPENED` remains tied to an observed MT5 entry deal.
- Do not assume the running local process has these changes until the branch is pulled and the forward runner is restarted.
- Preserve all existing forward event logs and generated CSV/JSON evidence; do not clean or overwrite them.
- After pulling, run the focused regression tests first. Then perform a controlled restart of only the identified RR2/TRAIL4 forward runner, verify account/server/symbol/magic and Telegram startup banner, and capture a new timestamped forward snapshot.
- Keep this as DEMO/RESEARCH evidence only; it does not authorize canonical or production decisions.
