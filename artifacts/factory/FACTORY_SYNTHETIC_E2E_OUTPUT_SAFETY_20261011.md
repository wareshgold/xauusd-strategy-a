# Synthetic Factory E2E — Output Safety Follow-up

Date: 2026-10-11

## Why this change was needed

The synthetic end-to-end runner already rejected the live worker snapshot, live job journal, and preserved demo status path. However, its default synthetic output paths could already exist as user-owned untracked artifacts. In that case the append-only journal could accumulate separate runs and the status publisher could replace an earlier snapshot.

## Guard added

`run_synthetic_e2e()` now refuses to start if either selected output file already exists. It also continues to reject protected live/demo paths and a status path identical to the journal path. It does not delete, truncate, rotate, or overwrite existing artifacts. Use two new isolated paths for every run.

A regression test covers status-only, journal-only, and both-existing cases, and asserts byte-for-byte preservation.

## Validation status

The preceding user-verified revision passed:
- focused lifecycle/recovery/journal tests: 63 passed
- full suite: 767 passed

Those results predate this output-path safety change. The new guard and regression tests still require local validation; no passing result is claimed for this revision yet.

## Next local step

From the Factory checkout, pull the branch, inspect status, run the synthetic E2E focused tests and the full test suite. Preserve all pre-existing untracked runtime files and Python cache directories.

For the actual synthetic run, create unique paths first (the example below uses a timestamp) and pass them explicitly. Then launch the dashboard in demo mode with those exact paths. The run is software-wiring evidence only: no canonical Strategy A geometry, no statistical-edge claim, no production BUY/SELL decisions, no MT5, no Holdout/Forward data, and no Forward Runner changes.

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$status = "$PWD\runtime\factory_synthetic_e2e_status_$stamp.json"
$journal = "$PWD\runtime\factory_synthetic_e2e_job_events_$stamp.jsonl"

.\.venv\Scripts\python.exe scripts/run_factory_synthetic_e2e.py --status-file $status --journal-file $journal

$env:SP2L_FACTORY_DEMO = "1"
$env:SP2L_FACTORY_DEMO_STATUS_FILE = $status
$env:SP2L_FACTORY_DEMO_JOB_EVENTS_FILE = $journal
.\.venv\Scripts\python.exe scripts/factory_dashboard.py
```

Open `http://127.0.0.1:8788/` and verify the displayed job ID and artifact match the synthetic runner output and the Job Journal Integrity panel reports `VALID` / `CONSISTENT`. Stop before any production or trading action; this is not a strategy certification.
