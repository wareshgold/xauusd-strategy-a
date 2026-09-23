# SP2L Strategy A — MT5/Telegram Live-Test Runbook (2026-09-21)

## Purpose

Controlled end-to-end validation of the live execution infrastructure without changing or inventing Strategy A geometry.

## Current safety state

- Strategy A geometry remains unresolved/frozen-gated.
- Strategy A adapter remains inactive.
- `LIVE_TRADING_ENABLE=false` by default.
- `ALLOW_REAL_EXECUTION=false` by default.
- CLOSEONLY/DISABLED/unknown MT5 symbol modes are hard real-execution blockers.
- Real execution is currently **NOT READY** because the OtetGroup account has no tested openable metal symbol.

## Dry-run test

Use:

```powershell
python scripts/run_live_session.py --check-only
python scripts/live_signal_simulator.py --seed 7 --unique-run
python scripts/live_session_report.py
python scripts/telegram_diagnostic.py --get-me   # test-only; sends no messages
```

### Repeated simulator runs (duplicate protection unchanged)

The gateway's DUPLICATE_SIGNAL_ID protection is intentionally untouched.
The simulator namespaces its deterministic signal ID so re-running the same
seed never collides with a previously processed test signal:

```powershell
python scripts/live_signal_simulator.py --seed 7 --unique-run
# -> SIM-<UTC-timestamp>-0007, e.g. SIM-20260921T091500Z-0007

# or with an explicit deterministic namespace / ID:
python scripts/live_signal_simulator.py --seed 7 --run-id 20260921T091500Z
python scripts/live_signal_simulator.py --seed 7 --signal-id SIM-MYTEST-0007
```

Same seed → same direction/entry/SL/TP values on every machine (verified by
tests); only the ID namespace changes. A deliberately replayed duplicate ID
is still rejected with DUPLICATE_SIGNAL_ID.

Expected safety outcome on the current account:

- pre-flight: `NOT_READY`
- reason: `mt5_symbol_spec`
- simulator: dry-run only
- no broker open order

## Broker unblock requirement

Before any real order test, obtain from the broker:

1. an account allowed to open positions;
2. the exact XAUUSD symbol for that account;
3. confirmation that the symbol trade mode permits opening.

Then rerun pre-flight and verify `READY` before considering a controlled real-order test.

## Telegram configuration diagnostic (test-only)
`scripts/telegram_diagnostic.py` reports the configuration path clearly:
```powershell
python scripts/telegram_diagnostic.py            # config presence only (offline)
python scripts/telegram_diagnostic.py --get-me   # + read-only bot identity check
```

- Reports bot token / chat id as **configured / not configured**, with
  masked fingerprints (`1234...wxyz`) — credentials are never printed in full.
- `--get-me` calls the read-only Bot API `getMe`: it sends **no messages** to
  any chat and reveals only the bot identity (first name/username/id).
- Exit code 0 = configuration complete (and token valid, if checked).

## Prohibited shortcuts

Do not bypass the CLOSEONLY gate.
Do not substitute an unverified metal symbol.
Do not activate the Strategy A adapter merely to make the execution path produce signals.
Do not modify P-Gap, AB=CD, Leg1/Leg2, entry, SL, TP, fill, or pending-order semantics in this execution task.

## Checkpoint

- Safety hardening commit: `f7f705f`
- Broker blocker issue: #237

## 2026-09-23 — Long-running forward session (watchdog)

The multi-symbol forward runner is a single-instance process guarded by
`runtime/sp2l_multi_symbol_forward_runner.lock` — a second runner refuses to
start ("two runners would duplicate every order"). It sends a startup banner
to Telegram (`START_TELEGRAM` event) and a daily summary at 21:00 UTC
(`SP2L_DAILY_SUMMARY_UTC_HOUR`, one per UTC day, over that day's events).

For a session that survives closing the PowerShell window:

```powershell
start /b python scripts\forward_watchdog.py        # keeps the runner alive
python scripts\forward_watchdog.py --stop          # stop watchdog + notice
```

- The watchdog restarts the runner after a crash (max 20 by default,
  `FORWARD_WATCHDOG_MAX_RESTARTS`) and notifies Telegram on DOWN/UP.
- Runner stdout is appended to `artifacts/forward-test/runner_stdout.log`.
- Exit-telemetry guarantees: exit deals whose own-position entry cannot be
  resolved are deferred, never sent with invented numbers (`n/a (unlinked)`).
- Execution mode `PENDING_LIMIT_RESEARCH` is published by the runner to the
  gateway via `MT5_FORWARD_ORDER_MODE`; fills must sit at the theoretical
  entry, keeping 1R intact.
- Full suite green as of `2026-09-23`: pytest 82 passed.
