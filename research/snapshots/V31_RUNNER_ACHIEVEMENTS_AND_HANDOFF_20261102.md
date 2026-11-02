# V3.1 Runner — Daily Achievements & Controlled-Restart Snapshot
Date: 2026-11-02
Snapshot scope: repository-visible engineering state and operational handoff
Status: RESEARCH / DEMO RUNNER — NOT RESTARTED; NO ORDER ACTION AUTHORIZED

## 1. Runner identity (do not confuse with V3)

This snapshot is specifically for **Strategy A V3.1**, the XAUUSD RR4 / ACT40 / DIST40 forward runner.

- Repository: `wareshgold/xauusd-strategy-a`
- Main V3.1 worktree recorded today: `D:\Mirzaei\Private\1\xauusd-strategy-a-v3-1-clock-guard`
- Integrated candidate worktree recorded today: `D:\Mirzaei\Private\1\xauusd-strategy-a-v3-1-integrated-20261102`
- V3.1 entry script: `scripts/run_sp2l_v3_1_xauusd_forward_test.py`
- Shared underlying runner: `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
- Configuration module: `sp2l_v3_1_rr4_act40_config`
- Strategy label: RR4 / ACT40 / DIST40
- Exact broker symbol in the restart runbook: `XAUUSD.ecn`
- V3.1 magic: `26092301`; legacy V3 magic remains `26092201`
- V3.1 event log: `artifacts/forward-test/SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl`
- V3.1 state: `runtime/sp2l_v3_1_xauusd_rr4_act40_forward_state.json`
- V3.1 remains research-only and DEMO-only. No canonical Strategy A geometry or production signal authority is created by this work.

## 2. Today's completed achievements

### A. Telegram credential and deal-lifecycle reliability — PR #389

PR #389, **Fix V3.1 Telegram delivery configuration and deduplicate deal lifecycle events**, was merged on 2026-11-02.

- Merge commit: `edc1f97c91102100d748bab1c90487cb8ac87998`
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/389
- Deal observation is tracked separately from successful Telegram delivery.
- Each deal ticket produces one observed lifecycle event; failed Telegram delivery remains retryable.
- Successful retry is represented separately as delivery confirmation.
- The read-only monitor counts unique deal tickets, suppresses duplicate lifecycle rows, and computes reported net once per unique deal.
- Telegram process-environment credentials take precedence as a complete pair. Partial environment credentials fail closed rather than mixing environment and file values.
- Deterministic lifecycle-idempotency and Telegram-source tests were added.
- PR verification reported forensic CI PASS.
- Local `config/telegram.json` was copied into the integrated V3.1 worktree, remains Git-ignored, and its contents/secrets are intentionally not recorded here.

### B. Startup broker recovery, shared lock and restart safety — PR #390

PR #390, **Add fail-closed V3.1 startup broker recovery**, is open, Draft and not merged.

- Branch: `fix/v31-startup-broker-recovery-20261102`
- Reviewed head: `9c006512b550d3c2f7826df4439a3fe636cac25f`
- Base branch: `research/strategy-a-v3-1-magic-clock-guard-20261102`
- Base SHA: `edc1f97c91102100d748bab1c90487cb8ac87998`
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/390
- Startup recovery queries active broker orders and positions by exact symbol + V3.1 magic.
- MT5 query failure (`None`) is distinguished from a valid empty inventory.
- Only supported owned pending-limit orders and valid owned positions are recovered into a fresh V3.1 state.
- Invalid owned tickets, unsupported same-symbol/same-magic order types, incomplete inventory and state-persistence failures are designed to abort startup.
- Recovery is read-only at the broker boundary: it does not place, cancel or modify orders and does not replay historical deal notifications.
- The shared lock is intended to coordinate separate worktrees and to fail closed on malformed/unreadable lock state or filesystem errors.
- Lock acquisition is placed before START event logging, Telegram startup notification, state reconciliation and polling; release checks the recorded owner PID.
- A controlled-restart runbook was added.

### C. Automated validation recorded for PR #390

GitHub Actions forensic run: `41416755168`

Observed job result: `forensic-checks = completed / success`.

Completed steps included:
- shared detector fixture
- V3.1 deal lifecycle idempotency tests
- V3.1 startup broker recovery tests
- shared runner lock tests
- Python compilation of V3.1 runner modules
- Telegram credential source tests
- reconciliation tests

CI success validates the committed automated checks; it does not establish live MT5 behavior or prove the singleton lock safe under every concurrent interleaving.

### D. Controlled restart documentation

Runbook:
`research/runbooks/V31_CONTROLLED_RESTART_RUNBOOK_20261102.md`

It records:
- the old runner predates and does not honor the new shared lock;
- the old event log and state must be preserved as evidence, not copied into the new session;
- the new worktree must start with fresh state and recover only currently active broker-owned objects;
- the local ignored Telegram configuration must remain outside Git;
- the operator must explicitly pin `SP2L_PENDING_SERVER_OFFSET_HOURS=2`;
- DEMO account, exact symbol/magic, clean worktree and lock preflight are required;
- the old PID must be confirmed absent before the new runner can start;
- a separate explicit operator approval is required before start.

## 3. Blocking review finding — do not merge PR #390 yet

A race condition was identified in `scripts/sp2l_runner_lock.py` stale-lock replacement.

Current sequence:
1. Two processes can both read the same stale lock and determine its PID is no longer alive.
2. Process A unlinks the stale file and creates a new lock for itself.
3. Process B can then unlink the path without rechecking that it still refers to the stale lock it inspected.
4. Process B can create another lock while A is already proceeding.

This can invalidate singleton protection and permit two runners to believe they own the lock. Existing stale-lock tests cover sequential replacement, not this competing-process interleaving.

**Required before merge:** replace stale-file reclamation with a race-safe OS-level locking/ownership design suitable for the supported Windows environment (and any other supported platform), or otherwise prove an equivalent atomic compare-and-reclaim protocol. Add a deterministic multi-process contention/reclamation test. Re-run CI and review the resulting implementation. Until then PR #390 is not merge-ready.

Additional review notes:
- The current V3.1 wrapper sends/logs the START Telegram banner before startup recovery completes. Consider making the success banner follow successful recovery and state persistence so the notification cannot imply a successful start when recovery aborts.
- Ensure MT5 shutdown/cleanup is also covered if lock acquisition itself raises after MT5 initialization.

These are review findings, not claims that they have already been fixed.

## 4. Operational state and hard safety boundary

Last recorded operational facts for 2026-11-02:
- Legacy V3.1 process PID: `4068` (recorded earlier; its current liveness has not been re-queried in this snapshot).
- The legacy process predates the shared lock and does not honor it.
- The user reported no runner restart and no order submission.
- No MT5 order, pending order or position was modified as part of this repository review.
- The Telegram configuration was copied locally into the integrated worktree; secrets are not part of this snapshot.

Do not infer that the new lock protects against PID 4068. Do not start the updated runner while the legacy process may still be alive. Do not stop PID 4068, merge PR #390, or start any runner without separate explicit operator authorization.

## 5. Next engineering sequence

1. Fix the shared-lock stale-reclamation race and add competing-process tests.
2. Move the positive startup notification after successful recovery/state persistence; ensure MT5 cleanup on lock-acquisition failure.
3. Re-run the forensic workflow and review the exact new head/CI results.
4. Only after a clean review, request a separate decision on PR #390 merge.
5. Before any controlled restart, preserve the old event/state/config/log evidence with timestamps and SHA-256; do not overwrite prior snapshots.
6. Obtain explicit approval before stopping the verified old PID. Confirm it is absent and no other V3.1 process remains.
7. Preflight the new worktree, local ignored Telegram config, DEMO account, exact symbol/magic, server offset and shared lock.
8. Obtain a separate explicit start approval. After start, verify one PID, fresh state, `STARTUP_BROKER_RECOVERY` event and read-only monitor state.

## 6. Provenance

This snapshot is committed on a separate documentation branch based on PR #390 head. It does not modify PR #390, the V3.1 runner source, local MT5 runtime files, event logs, state files, Telegram secrets, or any running process.

- Source PR #389: https://github.com/wareshgold/xauusd-strategy-a/pull/389
- Source PR #390: https://github.com/wareshgold/xauusd-strategy-a/pull/390
- PR #390 reviewed head: https://github.com/wareshgold/xauusd-strategy-a/commit/9c006512b550d3c2f7826df4439a3fe636cac25f
- Controlled restart runbook: https://github.com/wareshgold/xauusd-strategy-a/blob/fix/v31-startup-broker-recovery-20261102/research/runbooks/V31_CONTROLLED_RESTART_RUNBOOK_20261102.md
