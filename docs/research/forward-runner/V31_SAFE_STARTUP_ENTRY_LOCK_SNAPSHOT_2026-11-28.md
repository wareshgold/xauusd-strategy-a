# V3.1 Safe Startup & Owned-Trade Entry Lock — Progress Snapshot

**Snapshot date:** 2026-11-28  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Remote working branch:** `research/v31-owned-trade-entry-lock-20261128`  
**Implementation base:** `a007f9264b76c5917197b0a6f62db077f2f5309a`  
**Implementation HEAD before this snapshot commit:** `8f9e7d2e31038a13fb12d7d8bf6ecc8d579ff3f4`  
**Local worktree branch label reported during review:** `review/v31-owned-trade-entry-lock-20261128`  
**Remote branch comparison:** 9 commits ahead of base, 0 behind. The remote branch name is `research/...`; the local branch label is `review/...`. Confirm/refetch branch mapping before any future push from the local worktree.

## 1. Why this work started

The V3.1 forward runner and MT5 terminal were found stopped after the Thursday session. Windows System events showed a planned restart initiated by `MoUsoCoreWorker.exe` on 2026-11-27 at approximately 03:32:39 local time, followed by Event Log shutdown and system restart at approximately 03:35. This is strong evidence of a Windows servicing/update restart, not proof of the runner's exact last execution instant.

The runner event JSONL's last observed event was a daily summary at 2026-11-27 00:30:13 local time. Runtime state was last written at 03:32:39, matching the restart initiation time. This is consistent with the runner saving state near the restart, but does not independently prove process liveness until shutdown.

No matching V3.1/MT5 scheduled task or Startup-folder/Run-key autostart entry was found in the audit. Windows Update policy values were observed as `AUOptions=2` and `NoAutoRebootWithLoggedOnUsers=1`; these are not an absolute guarantee against restart.

## 2. User-approved operational policy

This is an operational safety policy only. It does **not** define canonical SP2L geometry, P-Gap, AB=CD anchors/tolerance, fill semantics, or trading rules.

- If a recognized V3.1-owned position or pending order exists, the runner must continue managing that existing inventory.
- While either an owned position or owned pending order exists, no new V3.1 entry may be submitted.
- New entry may be considered only after both owned positions and owned pending orders are absent.
- Unknown/manual/foreign account inventory must be classified separately and block startup with an operator alert.
- Broker query failure, malformed inventory, uncertain recovery, or failed persistence must fail closed.
- The guard must not prevent lifecycle/trailing management of already-owned trades.
- No live behavior, MT5 startup, Runner startup, or Task Scheduler activation is authorized by this snapshot.

## 3. Implementation present on the research branch

The branch contains 9 commits after the base and changes 5 tracked files (620 insertions, 16 deletions in the comparison reported locally).

### New helper: `scripts/sp2l_v31_entry_guard.py`

- Classifies orders and positions for an exact symbol + magic pair.
- Treats `None` query results as broker inventory unavailable, never as an empty inventory.
- Validates symbol, magic, and positive ticket fields; rejects malformed or duplicate owned tickets.
- Reports whether an owned pending order and/or owned position is active.

### New helper: `scripts/sp2l_v31_startup_safety.py`

- Requires explicit expected account login and server values from environment variables:
  - `SP2L_EXPECTED_ACCOUNT_LOGIN`
  - `SP2L_EXPECTED_ACCOUNT_SERVER`
- Requires exact login and server match with MT5 account info.
- Inspects account-wide active orders and positions against configured (symbol, magic) ownership pairs.
- Blocks on query failure, missing ownership scope, malformed/duplicate inventory, or any unrecognized/manual/foreign inventory.

No account login value is embedded in code or this snapshot.

### Runner integration: `scripts/run_sp2l_v3_1_xauusd_forward_test.py`

- Startup recovery checks account identity first, then account-wide orders/positions, then performs per-config owned-inventory recovery.
- Recovery or state-persistence failures log a startup block, attempt a Telegram alert, and raise. Alert failure does not authorize continuation.
- Recovered state is saved before the recovery-success event.
- The candidate execution wrapper re-queries symbol-specific orders and positions immediately before the original execution function.
- An active owned position/order or unavailable/malformed broker inventory blocks that entry attempt; an empty valid owned inventory proceeds to the existing execution-clock validation and original executor.
- This is a last-moment application-level check, not an atomic broker-side lock; a race with external/manual actions remains theoretically possible.

## 4. Validation completed

### Targeted test suite

The 9 relevant files were collected and then executed together:

- `test_reconcile_sp2l_forward_backtest.py`
- `test_sp2l_forward_audit.py`
- `test_sp2l_forward_backtest_reconciliation_invariants.py`
- `test_sp2l_forward_backtest_reconciliation_v1.py`
- `test_sp2l_trailing_rules.py`
- `test_sp2l_trailing_state.py`
- `test_sp2l_v31_entry_guard.py`
- `test_sp2l_v31_monitor.py`
- `test_sp2l_v31_startup_safety.py`

**Latest local result:** 69 passed in 0.54s; `PYTEST_EXIT=0`.  
**Diff check:** clean.

Important qualification: the successful local run included a one-line, uncommitted test-fixture correction in `tests/test_sp2l_v31_monitor.py` adding `trade_mode=0` to the fake `account_info()` object. The production monitor was not changed. The fixture correction is local-only at this snapshot and is not included in the remote implementation commits.

A broader `pytest -k v31` collection attempt was not a valid full-suite result: 5 unrelated test modules failed collection because the isolated review venv does not have `MetaTrader5` and `numpy`. Those dependencies were deliberately not installed into the runner environment. The 69-test targeted suite is the relevant passing evidence so far.

## 5. Current repository / runtime safety state

- Implementation branch is research-only; no PR has been opened.
- The original runner worktree was not modified by the review-branch work.
- The local review worktree had one uncommitted change: the Monitor test fixture correction described above.
- No Runner was started.
- No MT5 terminal was started by this work.
- No Task Scheduler task or Windows autostart entry was created or activated.
- No account identity environment variables were configured.
- No live configuration or production BUY/SELL behavior was changed.
- No claim is made that the implementation is production-ready.

## 6. Open review items — next planned work

1. **Finish control-flow audit.** Trace the exact base-runner startup hook call site and prove it runs before the polling/entry loop.
2. **Prove lifecycle continuity.** Verify that recovered owned positions/orders are placed in the state structures required by the existing position, pending-order, and trailing lifecycle handlers. In particular, inspect the recovered `state["positions"]` membership used by the position lifecycle observer.
3. **Add integration-level tests.** Exercise startup-hook ordering, existing owned position management while entry is blocked, pending-order management while entry is blocked, and no-entry behavior after query failure. Unit tests alone do not prove these cross-module paths.
4. **Review runtime query-failure semantics.** Inspect lifecycle functions that currently use patterns such as `orders_get(...) or []` / `positions_get(...) or []`; ensure a runtime `None` cannot be silently mistaken for an empty inventory where that would compromise management or safety.
5. **Review alert/logging failure paths.** Confirm a logging failure cannot bypass a safety block and document the expected operator response.
6. **Resolve branch naming.** The local branch label reported was `review/...`, while the confirmed GitHub branch is `research/...`. Fetch and verify remote/local ancestry before any further local push.
7. **Re-run targeted tests** after any code changes; keep the local Monitor fixture correction isolated and decide whether to commit it after review.
8. **Only after code review and explicit user approval:** configure the expected account identity locally, perform a controlled non-trading/preflight validation, and separately discuss a safe Windows startup mechanism. Do not activate Task Scheduler or start the Runner/MT5 without explicit authorization.

## 7. Workflow guardrails

This work remains separate from canonical Strategy A research. Follow the project workflow: source resolution → synthetic fixtures → frozen geometry → development → untouched validation → robustness/stability → fresh holdout → production. No unresolved source geometry may be inferred from backtest performance. AI may assist research, engineering, validation, documentation, and analytics, but must not autonomously define canonical rules or generate production BUY/SELL decisions.

**Current stopping point:** implementation exists on the research branch; the targeted 69-test suite passes locally with one uncommitted test-fixture correction; static control-flow and lifecycle integration audit remains incomplete. No activation.
