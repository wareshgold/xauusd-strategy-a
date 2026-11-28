# V3.1 Safe Startup & Owned-Trade Entry Lock — Progress Snapshot

**Snapshot date:** 2026-11-28  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Remote working branch:** `research/v31-owned-trade-entry-lock-20261128`  
**Implementation base:** `a007f9264b76c5917197b0a6f62db077f2f5309a`  
**Implementation HEAD before this snapshot refresh:** `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`  
**Local review worktree:** `F:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v31-entry-lock-review-20261128`  
**Remote branch:** `research/v31-owned-trade-entry-lock-20261128`. The local worktree was fast-forwarded and verified at `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`; no local push was performed.

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

The original targeted suite was expanded to 11 files and executed locally after fast-forwarding the lifecycle-diagnostic commits:

- `test_reconcile_sp2l_forward_backtest.py`
- `test_sp2l_forward_audit.py`
- `test_sp2l_forward_backtest_reconciliation_invariants.py`
- `test_sp2l_forward_backtest_reconciliation_v1.py`
- `test_sp2l_trailing_rules.py`
- `test_sp2l_trailing_state.py`
- `test_sp2l_v31_entry_guard.py`
- `test_sp2l_v31_monitor.py`
- `test_sp2l_v31_startup_safety.py`
- `test_sp2l_v31_startup_recovery.py`
- `test_sp2l_lifecycle_query_diagnostics.py`

**Latest local validation at HEAD `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`:** all 11 targeted test files completed with `PYTEST_EXIT=0`; the command reported `VALIDATION=PASS`. The three runner/helper files compiled with `PY_COMPILE_EXIT=0`; `git diff --check` completed with `DIFF_CHECK_EXIT=0`. The user supplied exit-code summary did not include pytest's collected/passed test count, so no exact count is claimed here.

The lifecycle diagnostics helper has three focused tests covering: (1) operation raises an exception and exactly one failure is reported, (2) MT5 returns `None` and the last-error detail is reported exactly once, and (3) a successful snapshot clears the failure state via the success callback.

The local Monitor fixture correction and startup-recovery test file remain uncommitted local changes; they were present before the latest fast-forward and remained present after it. The fixture correction adds `trade_mode=0` to the fake account info; production monitor code was not changed by that local fixture correction.

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

## 6. Post-snapshot lifecycle query diagnostics (2026-11-28)

Six commits were added after the snapshot commit `e44b66c3978dcbca3ca4649cf186b9784ead6b99`. The first three introduced V3.1/base lifecycle query failure logging; the next three added a testable query wrapper, focused tests, and fixed duplicate exception reporting:

- `d90aaffe6b14ef350e214f65ad0da81d61e4cd82` — V3.1 lifecycle query failure diagnostics for active orders, order history, and trailing position inventory.
- `7e35eeb60ff017e07241ae760263aee54eefd486` — base position lifecycle no longer treats a `None` result as an empty list; it logs a rate-limited diagnostic and skips that observer cycle.
- `5491483951dbe004c71fc9bd6de5c44416792a87` — protect the V3.1 diagnostic path if `mt5.last_error()` itself raises.
- `ad35f45c268e8989dc055d7d5bdfd52735586489` — add `scripts/sp2l_lifecycle_query_diagnostics.py`, a small testable wrapper distinguishing raised query exceptions from MT5 `None` results.
- `f752cd582da9474a50eeef208d1ce01be43ea913` — add three focused tests for exception, `None`, and successful query outcomes.
- `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2` — route the pending-history lifecycle query through the helper, preventing an exception from being logged a second time as an MT5 `None` result.

The remote branch was verified as 6 commits ahead of the snapshot commit and 0 behind at implementation HEAD `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`. The last three commits add the helper and tests and modify the V3.1 runner.

Behavioral boundaries:

- A failed active-order query stops that pending lifecycle/TTL pass; it does not cancel or classify orders as absent.
- A failed order-history query is logged; active-order observations can still be processed from the successful active snapshot.
- A failed trailing position query skips trailing changes and stale-extreme cleanup for that pass.
- The base position lifecycle observer logs and skips when its MT5 query fails; a successful later poll clears the one-shot diagnostic suppression for that symbol.
- The entry guard remains a separate last-moment check and continues to fail closed on its own query failure.

**Validation status:** local syntax compilation, all 11 targeted test files, and diff checks passed after all six post-snapshot commits were fetched. This is local automated test evidence only; it is not a live MT5 integration test, broker execution test, or forward-performance validation. No runner/terminal activation was performed.

## 7. Open review items — next planned work

1. **Integration-test startup and lifecycle.** Startup hook order has been source-traced: recovery is called after state load/reconciliation and before START notification and the polling/entry loop. Add integration-level tests to prove this behavior.
2. **Prove lifecycle continuity.** Verify that recovered owned positions/orders are placed in the state structures required by the existing position, pending-order, and trailing lifecycle handlers. In particular, inspect the recovered `state["positions"]` membership used by the position lifecycle observer.
3. **Add integration-level tests.** Exercise startup-hook ordering, existing owned position management while entry is blocked, pending-order management while entry is blocked, and no-entry behavior after query failure. Unit tests alone do not prove these cross-module paths.
4. **Finish runtime query-failure audit.** The V3.1 pending lifecycle/TTL and trailing inventory queries emit rate-limited failure diagnostics and fail closed for that pass. The pending-history query now uses a tested wrapper to avoid duplicate exception/None reporting. Re-check remaining lifecycle/history paths, including whether every query has appropriate rate limiting and whether a logging failure can interrupt a safety path.
5. **Review alert/logging failure paths.** Confirm a logging failure cannot bypass a safety block and document the expected operator response.
6. **Resolve branch naming.** The local branch label reported was `review/...`, while the confirmed GitHub branch is `research/...`. Fetch and verify remote/local ancestry before any further local push.
7. **Re-run targeted tests** after any code changes; keep the local Monitor fixture correction isolated and decide whether to commit it after review.
8. **Only after code review and explicit user approval:** configure the expected account identity locally, perform a controlled non-trading/preflight validation, and separately discuss a safe Windows startup mechanism. Do not activate Task Scheduler or start the Runner/MT5 without explicit authorization.

## 8. Workflow guardrails

This work remains separate from canonical Strategy A research. Follow the project workflow: source resolution → synthetic fixtures → frozen geometry → development → untouched validation → robustness/stability → fresh holdout → production. No unresolved source geometry may be inferred from backtest performance. AI may assist research, engineering, validation, documentation, and analytics, but must not autonomously define canonical rules or generate production BUY/SELL decisions.

**Current stopping point:** implementation and lifecycle query diagnostics exist on the research branch at `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`. Local syntax compilation, the 11-file targeted test command, and diff checks passed. The local review worktree still has uncommitted `tests/test_sp2l_v31_monitor.py` and `tests/test_sp2l_v31_startup_recovery.py` changes. No PR, live integration run, Runner/MT5 activation, account identity configuration, or autostart activation has occurred.


## 9. Startup inventory exception hardening (2026-11-28)

After the prior snapshot, code review found that MT5 inventory APIs can fail in two distinct ways: return `None`, or raise an exception. The existing startup classifier already rejected `None`, but raised exceptions in account-wide/per-symbol inventory queries could abort startup before the safety-block alert path ran.

Changes added on the research branch:

- `scripts/sp2l_v31_startup_safety.py` now exposes `query_inventory_snapshot`, which preserves `None` for the existing fail-closed classifier and wraps raised exceptions in `BrokerInventoryQueryError` with the exact query name.
- `tests/test_sp2l_v31_startup_safety.py` now tests both exception tagging and preservation of `None`.
- The V3.1 startup hook routes account info, account-wide orders/positions, and per-symbol orders/positions through a required-query wrapper. Raised exceptions trigger `STARTUP_SAFETY_BLOCKED`, a best-effort Telegram alert, and startup abort.
- The per-symbol order/position wrappers are scoped only to `_v31_startup_recovery`. A diff review caught and corrected an intermediate accidental replacement in the pending-TTL path before local validation was requested; the final diff confirms the TTL path retains its original direct query and diagnostic handling.

Commits after implementation HEAD `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`:

- `ed394cc669cdee78b26c64c7049e521ed2400c81` — add tagged startup inventory query exceptions.
- `ae8c4829367ae6374d903877e55d261cca300220` — add focused exception/None tests.
- `c64e98c2da8f4899175618ff0c9031d0f26e1fcf` — route startup inventory queries through the alerting wrapper.
- `cf8a89bdffdefc559d764c8d2b00f08b37b2996e` — correct wrapper scope; preserve the pending-TTL query path.
- `f458e668efa0a32ca954c66587a8c3cb168fd38a` — apply the same exception handling to the startup hook's account-info query.

**Current remote branch HEAD:** `f458e668efa0a32ca954c66587a8c3cb168fd38a` (6 commits ahead of `b0cfcf4b51c7592963a7b7c695ffa8cbc28660b2`, 0 behind). The latest local validation has not yet been run; local syntax compilation, targeted tests, and `git diff --check` are pending after the next fast-forward.

**Remaining qualification:** the base runner's first `mt5.account_info()` call occurs before the V3.1 startup-recovery hook. If that first call itself raises, the base runner aborts before the V3.1 hook's alert wrapper can run. This remains an alert-path review item; it still fails closed and cannot proceed into the polling/entry loop.

**Current local state last reported by the user:** review worktree HEAD `ae511254c15de3e7559608811212ccb107654adc`; preserved local changes remain `M tests/test_sp2l_v31_monitor.py` and `?? tests/test_sp2l_v31_startup_recovery.py`. No local commit or push was performed.

**Safety boundary unchanged:** no Runner/MT5 activation, no Task Scheduler/autostart change, no account identity environment configuration, no live configuration change, and no PR creation.

## 10. Cross-module startup/recovery/lifecycle contract coverage (2026-11-28)

Added `tests/test_sp2l_v31_startup_integration_contract.py` on the research branch. The tests combine the pure startup-recovery and owned-exposure classifiers and assert the runner's source-level control-flow wiring without importing or initializing MT5.

Coverage added:

- Recovery and entry-guard classifiers agree for owned pending-order-only, position-only, combined, and empty broker snapshots.
- The guard remains blocked while either owned inventory category is present and reports no exposure only for a valid empty snapshot.
- Account-wide foreign inventory is rejected rather than being treated as owned V3.1 inventory.
- The base runner invokes its recovery hook before the `START` event and before entering the polling loop.
- The base polling loop calls pending expiry/lifecycle, position lifecycle, and symbol lifecycle before candidate discovery and candidate execution.
- V3.1 wires the startup recovery hook, guarded executor, and trailing position manager into the base runner.
- The base position observer accepts a recovered position ticket through `state['positions']` even if its magic metadata does not match the normal magic check.

**Important test classification:** these are cross-module contract/source-control-flow tests, not a live MT5 integration test. They do not prove broker IPC, order modification/cancellation, trailing placement, or Telegram delivery. The actual broker interaction remains untested and no terminal was initialized.

**Latest remote branch HEAD:** `d80d911c297b2ca0635cf6d52da63599ec88a2b0` before this documentation update. The new contract tests have not yet been executed locally. The next local validation should run the existing 11 targeted test files plus `test_sp2l_v31_startup_integration_contract.py`, syntax compilation, and `git diff --check`.

**Local worktree caution:** the user previously reported a local untracked `tests/test_sp2l_v31_startup_recovery.py`. This branch deliberately adds a separate file named `test_sp2l_v31_startup_integration_contract.py`; it does not overwrite that local untracked test.

## 11. Initial MT5 account preflight alert hardening (2026-11-28)

The first `mt5.account_info()` call in the base runner occurs before the V3.1 recovery hook. It is now explicitly guarded:

- A raised `account_info()` exception, `None` result, malformed account object, or non-demo trade mode invokes the optional runner startup-failure hook and then aborts startup.
- V3.1 wires that hook to `scripts/sp2l_v31_startup_failure_alert.py`.
- The notification helper attempts event logging and Telegram delivery independently. A logging exception does not suppress the alert attempt; an alert exception does not alter the caller's startup abort.
- The base runner catches exceptions raised by the optional hook so notification failures cannot mask or replace the original startup failure.
- The hook is absent in generic runner configurations unless explicitly installed; no strategy, signal, order, trailing, or lifecycle behavior is changed after successful startup.

New source-level/unit coverage in `tests/test_sp2l_v31_startup_integration_contract.py` checks the preflight notification ordering, V3.1 hook wiring, and all four combinations of logging/Telegram success and failure.

**Validation pending:** this change has been committed to the research branch, but no local test run has yet been reported for this revision. The tests are deterministic helper/source-contract tests; they do not initialize MT5 or prove real Telegram delivery.

**Latest implementation commit before this documentation update:** `0972c20236c926b09b844325dbd4b02e8f851aa4`.

**Safety boundary unchanged:** no Runner or MT5 terminal was started, no account identity variables were set, no autostart was configured, no PR was created, and no live configuration or order behavior was changed.

## 12. Independent startup safety alert paths (2026-11-28)

A further source review found that the account-wide/per-symbol startup safety blocker called runner.log_event before attempting Telegram. If the event file could not be written, the exception prevented the operator alert from being attempted. The initial MT5 initialize() failure path also aborted before reaching the account-info alert hook.

Changes on the research branch:

- scripts/sp2l_v31_startup_failure_alert.py now supports explicit event names and alert headings/instructions while keeping event logging and Telegram delivery independent best-effort operations.
- The V3.1 _block_startup path uses that helper. A failed STARTUP_SAFETY_BLOCKED event write no longer suppresses the Telegram alert attempt; failure of both side effects still leaves the raised startup block intact.
- The alert-result event is named from the original failure event (for example, STARTUP_SAFETY_BLOCKED_ALERT) so initialization and safety-block diagnostics remain distinguishable.
- The base runner now alerts through the optional hook when mt5.initialize() raises or returns false, then aborts startup. The generic runner remains unchanged unless a V3.1 startup-failure hook is installed.
- Added deterministic tests for a failed safety-block event write with successful Telegram delivery, alert-event naming, and MT5 initialization alert-hook ordering.

**Latest remote implementation HEAD:** 24d37a5d8d1ca254eb0fdf9b831224965082d0c5, 13 commits ahead of 42fe5787dd8936551116f50387e35694e7f73523 and 0 behind at the latest GitHub comparison.

**Validation status:** GitHub reports no commit status checks and no workflow runs for this HEAD. The existing push-triggered forensic workflow is scoped to branches named research/sp2l-f13-forensic-repro-*; this review branch does not match that filter, and no PR exists to trigger its pull_request path. The new changes have not yet been executed in the user's local review worktree. Local syntax compilation, the targeted 12-file test set, and git diff --check remain required. No test success is claimed for this revision.

**Safety boundary unchanged:** no Runner/MT5 activation, no account identity configuration, no autostart change, no PR creation, no live configuration change, and no broker operation.
