# V3.1 Cohort Diagnostics — Local Runbook (2026-11-08)

## Status

Added to the draft forensic branch:
- `scripts/sp2l_v31_forward_cohort_diagnostics.py`
- `tests/test_sp2l_v31_forward_cohort_diagnostics.py`

This analyzer consumes only the local per-position CSV produced by the first-pass forensic analyzer. It does not read the private ZIP, connect to MT5, or modify the runner. It reports:
- BUY / SELL cohorts;
- trailing event-count cohorts (0 / 1 / 2+) and side-by-trailing cohorts;
- hold duration from UTC entry/exit timestamps, with explicit buckets: <5m, 5–15m, 15–30m, 30–60m, >=60m;
- net, PF, win/loss, average and median metrics;
- signed entry-to-exit movement in raw price units only;
- missing time/volume and entry/exit volume mismatch flags.

The script and tests are newly committed but have NOT yet been run in the operator's local environment. Do not claim test pass or analysis completion until local output is reviewed.

## Run in the existing isolated forensic worktree

Fetch the latest PR branch before running, because these files were added after the first local worktree setup. Then run:

```powershell
$repo = "D:\Mirzaei\Private\1\xauusd-strategy-a-evidence-audit"
$worktree = "D:\Mirzaei\Private\1\xauusd-strategy-a-v31-local-forensic-20261108"
$py = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"

git -C $repo fetch origin research/v31-local-forward-forensic-20261108
if ($LASTEXITCODE -ne 0) { throw "Fetch failed" }

git -C $worktree status --short
if ($LASTEXITCODE -ne 0) { throw "Forensic worktree not found" }

git -C $worktree pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Fast-forward failed; stop and inspect local worktree" }

Set-Location $worktree
& $py -m pytest -q tests/test_sp2l_v31_forward_forensic.py tests/test_sp2l_v31_forward_cohort_diagnostics.py
if ($LASTEXITCODE -ne 0) { throw "Synthetic tests failed; do not continue" }

& $py scripts\sp2l_v31_forward_cohort_diagnostics.py --csv artifacts\forensic\v31-local-20261108\v31_closed_positions.csv --out artifacts\forensic\v31-local-20261108\cohort_diagnostics.json 2>&1 |
    Tee-Object -Variable cohortOutput
if ($LASTEXITCODE -ne 0) { throw "Cohort analysis failed" }

$cohortOutput | Set-Clipboard
Write-Host "COHORT_REPORT_COPIED_TO_CLIPBOARD"
```

The existing forensic worktree may contain uncommitted local artifacts. `git pull --ff-only` is intentionally non-destructive; if it refuses because of local changes, stop and report the message. Do not reset, clean, stash, delete, or recreate the worktree.

## Interpretation limits

- Trailing groups are descriptive and selected by price path; they do not establish that trailing caused better outcomes.
- Hold-duration cohorts are descriptive, not an execution rule.
- Raw price movement is not converted to pips, points, or R.
- Volume mismatch is flagged for investigation; it is not automatically labeled a broker error.
- Partial closes, INOUT/reversals, initial SL geometry, MFE/MAE, and same-entry V3 counterfactual remain unresolved.
- This runbook does not authorize V3 rollback, V3.2, or parameter changes.
