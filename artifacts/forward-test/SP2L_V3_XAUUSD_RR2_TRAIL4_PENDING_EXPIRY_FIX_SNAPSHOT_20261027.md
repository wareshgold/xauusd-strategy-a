# SP2L V3 XAUUSD RR2/TRAIL4 Pending Expiry Fix Snapshot — 2026-10-27

## Purpose and classification
This is a code-change/research handoff snapshot for the RR2/TRAIL4 pending-order TTL clock correction. It is not a new MT5 runtime/forward-test capture, does not certify a trading edge, and does not make Strategy A canonical. `canonical=false`.

## Recorded source
- Repository: `wareshgold/xauusd-strategy-a`
- PR: [#358 — Fix RR2/TRAIL4 pending expiry using UTC epoch time](https://github.com/wareshgold/xauusd-strategy-a/pull/358)
- Merge commit: `97b595723b7f79361e99fd6d36486cc54cc95fe6`
- Source branch used for the reviewed change: `fix/rr2-trail4-pending-expiry-utc-clock-rebased-20261027`
- Base branch: `fix/rr2-trail4-pending-lifecycle-safe-20261011`
- CI run: [SP2L forensic deterministic checks #585](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40454479231) — SUCCESS.

## Scope of code change
File: `scripts/run_sp2l_v3_xauusd_forward_test.py`
- Calculate pending-order age from MT5 `order.time_setup` Unix epoch and `time.time()`.
- Remove pending TTL's dependency on broker UTC-offset/DST inference and a fresh/advancing tick.
- Fail closed for missing/invalid or future setup timestamps.
- Limit cancellation eligibility to the configured symbol, configured magic number, and BUY_LIMIT/SELL_LIMIT orders.
- Keep cancellation failures retryable; an already confirmed cancellation is not repeated.

File: `tests/test_sp2l_v3_pending_expiry.py`
- Update pending-order fixtures to use Unix-epoch timestamps.
- Retain lifecycle/reconciliation regression coverage.
- Verify expiry with no usable tick/server offset, no premature expiry, invalid/future timestamp handling, and ownership/type restrictions.

## Validation evidence
The GitHub Actions run completed successfully. The following workflow steps passed:
- Install deterministic test dependencies
- Run shared detector fixture
- Run reconciliation tests
- Run pending-order expiry regression tests

This is CI evidence only. The updated runner has not been verified in the user's local MT5 terminal or against a controlled broker order in this snapshot.

## Strategy behavior boundary
The intended scope is pending-order TTL clock handling only. No intended change to signal detection/entry criteria, P-Gap, spike detection, SL anchor, TP_R=2.0, trailing rules, order sizing, or Telegram lifecycle semantics. These invariants still require local diff/config verification before deployment; this snapshot does not independently prove runtime equivalence.

## Forward-test evidence preservation
- No live MT5 order was placed or cancelled by the code change or CI.
- No local Forward Test process was stopped/restarted.
- Existing local event logs, CSV/JSON exports, and user-generated snapshots were not modified by this GitHub change.
- The tracked GitHub event log is historical research evidence, not a substitute for the user's latest local forward log. Do not overwrite it to manufacture a fresh runtime snapshot.
- Capture a separate timestamped runtime snapshot only after the user identifies the exact local runner/process and completes a controlled verification run.

## Deployment gate / next action
Before using this code in the forward test:
1. Inspect local branch, HEAD, worktree status, and hashes of the latest snapshots/logs read-only.
2. Compare the exact runner/config against the merged commit; verify entry/SL/TP/trailing settings remain unchanged.
3. Run the focused tests in the user's environment.
4. Only then perform a controlled restart of the identified DEMO/RESEARCH RR2/TRAIL4 runner and capture a new runtime snapshot.

Do not use `reset`, `clean`, broad staging, or overwrite existing evidence. This snapshot does not authorize production/live deployment.
