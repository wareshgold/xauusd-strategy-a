# V3.1 Controlled Restart Runbook — 2026-11-02

Status: PREPARED / NOT AUTHORIZED TO EXECUTE

This runbook applies to the V3.1 RR4/ACT40 forward runner after PR #390 is reviewed and merged. It is an operational checklist, not strategy logic. No step below is permission to place orders.

## Safety facts

- The currently running legacy process was started from the original `xauusd-strategy-a-v3-1-clock-guard` worktree.
- The legacy runner predates the shared cross-worktree lock. It does not create or honor the new shared lock.
- Therefore the new lock cannot prove that the legacy process has stopped. Verify the legacy PID is absent before launching the updated runner.
- The updated runner has a fresh V3.1 state by design. It queries current active broker inventory by exact symbol + magic and persists recovered active order/position tickets before polling.
- Do not copy the old state file into the updated worktree. Do not copy the old event log into the new session. Preserve both as historical evidence in the original worktree.
- The ignored `config/telegram.json` is a local secret and is not part of Git. Transfer it locally only after fetching the reviewed branch; never print its contents or token.

## Preconditions

1. PR #390 is reviewed, CI green, and merged into `research/strategy-a-v3-1-magic-clock-guard-20261102`.
2. The updated worktree is checked out at the merged commit and has a clean Git status.
3. The local ignored Telegram config is copied from the original worktree only if the destination does not already exist; verify SHA-256 equality without displaying file contents.
4. Confirm the intended MT5 terminal/account is DEMO. The runner itself must continue to enforce the demo-only guard.
5. Confirm `SP2L_PENDING_SERVER_OFFSET_HOURS=2` is explicitly set in the launch shell. Never print the Telegram environment or config values.

## Stop and preserve the legacy session

1. Record the legacy runner PID and verify its executable command points to the original V3.1 runner script.
2. Before stopping, record event/state file size, last-write time and SHA-256 for evidence.
3. Stop only the verified runner PID after the operator explicitly authorizes the stop.
4. Wait until that PID is absent; also verify no other process is running the V3.1 runner script.
5. After the process exits, take a final immutable copy of the original event and state files into a timestamped evidence directory. Hash source and copy and require exact equality. Do not overwrite prior snapshots.

## Updated runner preflight

1. Verify the shared lock path resolves under the current user's temporary directory and that no lock is held by a live PID.
2. Verify the new worktree's ignored Telegram config exists and is ignored by Git.
3. Verify the new worktree has no inherited old state or event log. The runner should create a fresh state and a new event log.
4. Confirm exact symbol `XAUUSD.ecn`, V3.1 magic `26092301`, Demo account, and the reviewed RR4/ACT40 configuration from the local config module.
5. Confirm the pending server offset is explicitly pinned and the clock guard is healthy.

## Start gate

Start the updated runner only after a separate, explicit operator approval. If broker inventory query returns `None`, an owned order has an unsupported type, a ticket is invalid, the state write fails, the lock cannot be acquired, or the account is not Demo, startup must abort. Do not bypass any of these gates.

After start, verify a single runner PID, a newly created state file, the `STARTUP_BROKER_RECOVERY` event, and the monitor's read-only status. Do not infer that CI success proves live MT5 behavior.
