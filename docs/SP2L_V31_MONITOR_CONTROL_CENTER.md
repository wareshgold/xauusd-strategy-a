# SP2L V3.1 Monitor Control Center

## Purpose

A Persian-first, read-only operational view for the V3.1 XAUUSD Demo forward runner. This improves the existing filesystem-only monitor UI; it is not a strategy engine and does not make BUY/SELL decisions.

## Safety boundary

- Reads only the configured Runner state JSON and event JSONL files.
- Detects the Runner process by exact script path using a read-only Windows CIM query.
- Does not import MetaTrader5, initialize/shutdown MT5, or call account, tick, order, position, or trade APIs.
- Does not write Runner state, event logs, configuration, or trading files.
- Binds Flask to 127.0.0.1 only.
- Does not change or restart the Runner.

## Operator-facing layout

1. **Overall system status** — Runner process, state-file freshness, event-file freshness, and latest START timestamp.
2. **Activity since latest restart** — candidate events, order attempts, successful order results, execution blocks, trailing updates, unique deal lifecycle events, and event-reported net.
3. **Latest activity** — latest event and most recent order attempt, if any.
4. **Account and open trades** — explicitly unavailable because the dashboard does not query MT5. State-file tracked IDs are not broker inventory.
5. **Current-session diagnostics** — diagnostics after the latest START event.
6. **Historical diagnostics** — prior-session diagnostics collapsed separately so old incidents do not appear as current-session failures.
7. **Recent events** — the latest 12 events in the current session.

## Metric definitions and limitations

- Session boundary: the last readable `START` event in the currently loaded event window. If no START exists, the visible event window is used and the page says so.
- Event window: at most 2,000 most recent JSONL events. Counts are explicitly scoped to this readable window/current session, not claimed as lifetime totals.
- Candidate count: `CANDIDATE` events.
- Order attempts: `ORDER_ATTEMPT` events.
- Successful orders: `ORDER_RESULT` events whose nested `result.ok` is true. This is not live order inventory.
- Execution blocked: `EXECUTION_BLOCKED` events. These are informational and do not automatically indicate a software defect.
- Trailing counts: `TRAIL_UPDATE` events with explicit success true/false.
- Unique deal lifecycle count and net: deduplicated by deal ID when present, using `TELEGRAM_DEAL_LIFECYCLE` event fields. Account currency is not inferred; the UI labels the unit as unverified.
- State tracked IDs: IDs persisted in Runner state only; they are never presented as live broker positions/orders.
- File freshness: filesystem modification time. A quiet event file is not by itself proof that the Runner is stalled; state freshness and process status are shown separately.
- Current-session errors are computed after the latest START. Earlier diagnostics are shown under historical diagnostics.

## Dashboard refresh behavior

- Automatically updates every 15 seconds without a full browser-page reload.
- Replaces dashboard content in place and restores the current scroll position.
- Preserves expanded/collapsed historical-diagnostics details.
- Skips refresh while the browser tab is hidden and prevents overlapping requests.
- A temporary fetch failure leaves the current page visible and retries on the next interval.

## Local run

Use the existing read-only monitor worktree and point it at the active Runner worktree:

```powershell
$w = 'D:\Mirzaei\Private\1\xauusd-strategy-a-v3-dashboard-v3-20261103'
$runner = 'D:\Mirzaei\Private\1\xauusd-strategy-a-v3-1-trailing-retry-20261103'
$py = 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe'

$env:SP2L_RUNNER_ROOT = $runner
$env:SP2L_DASHBOARD_PORT = '8792'
& $py (Join-Path $w 'scripts\sp2l_v31_rr4_act40_monitor.py')
```

Open `http://127.0.0.1:8792`.

Do not launch the Professional Account Dashboard V3 against the active Runner terminal: it uses MT5 Python IPC. This Control Center deliberately avoids that connection.

## Acceptance checklist

- [ ] Existing monitor tests pass.
- [ ] New session-boundary tests pass.
- [ ] Confirm dashboard shows Runner status and file freshness.
- [ ] Confirm old Offset errors appear only under historical diagnostics after the latest START.
- [ ] Confirm MT5 remains NOT QUERIED.
- [ ] Confirm Runner PIDs and event/state files are not modified by the dashboard.
- [ ] Review on the local Factory PC before replacing the currently running monitor process.
