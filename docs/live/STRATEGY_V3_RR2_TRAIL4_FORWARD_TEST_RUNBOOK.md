# Strategy V3 RR2/TRAIL4 — Reproducible Forward-Test Runbook

Status: **operational research/demo profile; not canonical; not production-approved**.

This document records how to reproduce the Strategy V3 runner associated with source commit
`dac76b09da01f022d745f51328ee703f6fb59851`. It is deliberately on a documentation branch and
does not promote the code to `main`.

## 1. Identity and frozen configuration

- Repository: `https://github.com/wareshgold/xauusd-strategy-a`
- Reference commit: `dac76b09da01f022d745f51328ee703f6fb59851`
- Runner: `scripts/run_sp2l_v3_xauusd_forward_test.py`
- Config: `scripts/sp2l_v3_rr2_trail4_config.py`
- Shared execution engine: `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
- Symbol requested by the runner: `XAUUSD`; broker symbol resolution is terminal-dependent (the observed account resolved it as `XAUUSD.ecn`).
- Timeframe: M1.
- P-Gap price: 1.0.
- Spike multiplier: 1.5.
- Maximum SL distance: 10.0 price units.
- TP: 2.0R.
- Order mode: `PENDING_LIMIT_RESEARCH`.
- SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`.
- Pending TTL: 30 minutes.
- Volume: 0.01 lot.
- Magic: 26092201 for the observed XAUUSD.ecn setup.
- Session policy: all market hours.
- Trailing config in source: `TRAIL_PIPS=4.0`, `XAU_PIP_SIZE_PRICE=0.1`, therefore `TRAIL_DISTANCE_PRICE=0.4`; trailing checks the latest completed M1 candle. The startup output's broker pip metadata (`pip_size=0.01`) is not the same setting as the trail distance calculation. Do not silently change either.
- Required server-offset override observed for the recorded launch: `SP2L_PENDING_SERVER_OFFSET_HOURS=2`.

The source explicitly marks this as a research experiment. Its rules are not source-confirmed canonical Strategy A rules.

## 2. Safety prerequisites

Use a dedicated **demo** account only. The runner source defaults `LIVE_TRADING_ENABLE` and
`ALLOW_REAL_EXECUTION` to `true` if not already set, so launching it is capable of sending orders.
Do not run this on a funded/real account. Do not start a second runner to “check” an existing session.

Required environment:
- Windows with MetaTrader 5 desktop terminal installed and logged into the intended demo account.
- Python compatible with the installed `MetaTrader5` package and the terminal.
- Repository checked out at the exact reference commit (or a reviewed, explicitly recorded replacement).
- Install live requirements into a dedicated virtual environment: `python -m pip install -r requirements-live.txt`.
- Confirm the broker's exact XAUUSD symbol, minimum/step volume, terminal connection, account type, and trade permissions before launch.
- Keep Telegram credentials private; never commit tokens or account credentials.
- Preserve event logs, runtime state, snapshots, and all existing worktree changes.

Observed setup from the recorded machine (not universal): Windows 11, Python 3.12.10, MetaTrader5 Python package 5.0.6180, terminal at `C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe`, server `OtetGroup-MT5`, symbol `XAUUSD.ecn`. Another operator must use their own terminal path, broker symbol and verified demo account.

## 3. Check out the recorded source

PowerShell example for a fresh clone:

```powershell
git clone https://github.com/wareshgold/xauusd-strategy-a.git
Set-Location .\xauusd-strategy-a
git checkout --detach dac76b09da01f022d745f51328ee703f6fb59851
git rev-parse HEAD
git status --short
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-live.txt
```

The printed HEAD must equal the reference SHA above. A detached checkout is intentional for reproducibility.
Do not copy the local runtime folder or live logs from another machine.

## 4. Preflight before starting

First inspect the existing session; do not launch if a runner may already be active.

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'run_sp2l_v3_xauusd_forward_test\.py' } |
  Select-Object ProcessId, ParentProcessId, ExecutablePath, CommandLine |
  Format-List

Get-ChildItem .\runtime -ErrorAction SilentlyContinue
Get-ChildItem .\artifacts\forward-test -ErrorAction SilentlyContinue
```

A runner may create a parent and child process; process count alone is not a duplicate-run test.
Inspect parent/child relationship, command line, lock/state and fresh event activity. Never kill either process solely because two matches appear.

Check MT5 is logged into the intended demo account. The recorded startup was:
- server: `OtetGroup-MT5`
- login: recorded account identifier is intentionally not repeated in this reusable public runbook
- symbol resolved: `XAUUSD.ecn`
- volume: `0.01`
- `canonical=false`

Do not proceed unless the account is definitely demo and the intended terminal is connected.

## 5. Start the V3 runner

Open a dedicated PowerShell window in the repository root. Use the virtual environment Python, not an arbitrary global Python. This is the recorded launch pattern:

```powershell
$ErrorActionPreference = "Stop"
$py = (Resolve-Path ".\.venv\Scripts\python.exe").Path
$runner = (Resolve-Path ".\scripts\run_sp2l_v3_xauusd_forward_test.py").Path

$env:SP2L_PENDING_SERVER_OFFSET_HOURS = "2"
$env:SP2L_SYMBOLS = "XAUUSD"
$env:SP2L_P_GAP_PRICE = "1.0"
$env:SP2L_SPIKE_MULTIPLIER = "1.5"
$env:SP2L_MAX_SL_DISTANCE = "10.0"
$env:SP2L_TP_R = "2.0"
$env:SP2L_VOLUME = "0.01"
$env:MT5_FORWARD_ORDER_MODE = "PENDING_LIMIT_RESEARCH"
$env:SP2L_PENDING_TTL_MINUTES = "30"

# Only after positively confirming this is the intended DEMO account:
$env:LIVE_TRADING_ENABLE = "true"
$env:ALLOW_REAL_EXECUTION = "true"

git rev-parse HEAD
& $py $runner
```

Expected startup banner should include `RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST`,
`canonical: false`, `pGapPrice: 1.0`, `spikeMultiplier: 1.5`, `maxSlDistance: 10.0`,
`tpR: 2.0`, `volume: 0.01`, `PENDING_LIMIT_RESEARCH`, `SPIKE_CANDLE_EXTREME_RESEARCH`,
and `pendingTtlMinutes: 30.0`. Confirm the actual broker-resolved symbol and account before allowing it to continue.
The server-offset value of 2 is an observation from one broker/session, not a universal value; verify it for the account in use.

Keep this console open unless the operator has a separately verified process supervisor. Do not launch it again just because the dashboard is stale.

## 6. Logs and runtime state

The V3 wrapper explicitly directs its event log and state to:
- `artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl`
- `runtime/sp2l_v3_xauusd_rr2_trail4_forward_state.json`

Inspect without editing:
```powershell
Get-Content .\artifacts\forward-test\SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl -Tail 30
Get-Item .\runtime\sp2l_v3_xauusd_rr2_trail4_forward_state.json |
  Select-Object FullName, Length, LastWriteTimeUtc
Get-FileHash .\artifacts\forward-test\SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl -Algorithm SHA256
```

The wrapper has run-scoped state and pending-order TTL logic to avoid replaying pre-existing broker history into Telegram/statistics and to avoid cancelling orders whose creation time is not known to this run. Orders without a local creation marker are intentionally left untouched. Treat event logs as evidence; do not overwrite or truncate them.

## 7. Dashboard (read-only)

The existing generic `scripts/live_dashboard.py` remains unchanged and may already be running at
`http://127.0.0.1:8790`. Do not stop, replace, or restart it as part of this change.

A separate V3-specific dashboard was added at `scripts/live_dashboard_v3.py`. It reads:
- State: `runtime/sp2l_v3_xauusd_rr2_trail4_forward_state.json`
- Events: `artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl`
- Shared runner lock: `runtime/sp2l_multi_symbol_forward_runner.lock`
- Default URL: `http://127.0.0.1:8792` (override with `SP2L_V3_DASHBOARD_PORT`)

It binds to loopback and is read-only; it does not place orders or write runner state. It still probes MT5
read-only for account mode/ticks, and the shared lock is used to inspect runner mode. Do not assume that
this new dashboard has been launched or validated on the operator's machine. First review and test it
in a separate console. Never start a second runner to validate the dashboard. The 8790 dashboard and
its process are intentionally left untouched.

## 8. Verify health and distinguish parent/child

A process existing is not proof that the runner is healthy. Verify:
1. Identify parent and child PIDs and confirm their executable/command lines.
2. Confirm the V3 state file's modification time advances while the runner is expected to poll.
3. Confirm new V3 event lines appear when relevant events occur.
4. Confirm the MT5 terminal is connected to the intended demo account and symbol ticks are current.
5. Check pending orders, fills, cancellations/expiry and position lifecycle in MT5 against the event log.
6. Check Telegram delivery only if Telegram notifications are configured; never paste secrets into logs/issues.

A quiet event log alone may mean no setup occurred; use state heartbeat and terminal connectivity too.
Do not infer a duplicate run from the parent+child pair alone.

## 9. Stop/restart policy

Do not use `Stop-Process`, Task Manager termination, or a second launch as a diagnostic. First inspect the
runner's documented shutdown behavior in the exact checked-out source and record current state/log hashes.
If a restart is required, plan it explicitly, confirm no pending orders or positions would be mishandled,
and preserve logs and snapshots before acting. Never assume stopping Python cancels broker orders.

## 10. Evidence and promotion status

For every run, record:
- exact Git HEAD and branch/tag;
- UTC start time, broker/server, demo confirmation, resolved symbol and volume;
- effective configuration and relevant environment overrides (excluding secrets);
- runner PIDs and parent-child relationship;
- event log/state paths and SHA-256 at the snapshot time;
- dashboard URL and whether it reads the V3-specific files;
- known outages, rejected orders, spreads/fees/slippage and any manual intervention.

This profile is named **Strategy Version 3 — Operational Forward-Test Winner (Research Only)**.
It is an operational selection, not a statistically proven winner, not a source-confirmed canonical
SP2L definition, and not approval for production/live-funded trading. Require frozen rules, untouched
validation, robustness/stability analysis and a fresh holdout before any promotion decision.
