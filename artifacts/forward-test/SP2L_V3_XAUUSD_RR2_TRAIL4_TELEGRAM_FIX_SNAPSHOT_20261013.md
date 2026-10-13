# SP2L RR2/TRAIL4 Telegram Lifecycle Fix Snapshot — 2026-10-13

## Scope
Research/demo forward-notification reliability only. No Strategy A geometry, entry/exit rules, order sizing, or trade-execution semantics changed.

## Changes on this branch
- `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
  - Formats broker deal timestamps as UTC epoch -> Iran UTC+03:30 directly. It no longer subtracts the inferred MT5 server offset from `deal.time`.
- `scripts/run_sp2l_v3_xauusd_forward_test.py`
  - Persists each successfully acknowledged lifecycle deal immediately.
  - Ensures the first unavailable session-clock observation is logged deterministically, independent of host monotonic uptime; this was exposed by the existing focused CI suite.
  - If a lifecycle Telegram send fails, stops processing later deals in that poll. This prevents a CLOSED notification from overtaking an OPENED notification that is waiting for retry.
  - Failed lifecycle messages remain unmarked and eligible for retry on the next poll.
- `tests/test_sp2l_v3_pending_expiry.py`
  - Added regression tests for the expected UTC+03:30 deal time and for retry/order preservation (OPENED before CLOSED).
- This snapshot documents the handoff.

## Expected notification flow
1. A candidate passes the configured gates and broker order submission succeeds; the signal message is sent. A failed signal notification is kept in `pending_signal_notifications` and retried.
2. The actual broker entry deal is detected from MT5 history; an OPENED lifecycle message is sent.
3. The actual broker exit deal is detected; a CLOSED message is sent with broker-derived result data.
4. Failed lifecycle sends are retried on subsequent polls. Later lifecycle deals do not leapfrog a failed earlier deal.

## Guarantees and limitations
- GitHub Actions `SP2L forensic deterministic checks` passed on code commit `e07b0c702402e20743f6a2499aeae6bb9c62df05`: detector consistency PASS, reconciliation tests 2 passed, and pending/lifecycle suite 32 passed. Run: https://github.com/wareshgold/xauusd-strategy-a/actions/runs/38356182938.
- Telegram Bot API does not provide a general idempotency key for `sendMessage`; if Telegram accepts a message but the response is lost, duplicate delivery remains possible. The changes reduce local replay windows but cannot promise exactly-once delivery.
- Delivery latency depends on network/API responsiveness. This change does not claim a hard real-time guarantee.
- No live MT5 order was placed or modified by these changes.

## Deployment / forward-test handoff
- Do not assume the running local process has these changes until the branch is pulled and the forward runner is restarted.
- Preserve all existing forward event logs and generated CSV/JSON evidence; do not clean or overwrite them.
- After pulling, run the focused regression tests first. Then perform a controlled restart of only the identified RR2/TRAIL4 forward runner, verify account/server/symbol/magic and Telegram startup banner, and capture a new timestamped forward snapshot.
- Keep this as DEMO/RESEARCH evidence only; it does not authorize canonical or production decisions.
