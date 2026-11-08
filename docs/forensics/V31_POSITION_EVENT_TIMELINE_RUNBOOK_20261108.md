# V3.1 Position Event Timeline — Local Runbook

## Purpose and safety

This tool builds per-position chronological evidence from the existing private forward ZIP. It is read-only, uses only Python standard-library plus the forensic analyzer, does not import/connect to MetaTrader5, and does not touch the active runner or state.

It joins broker entry/exit deals with runner `TRAIL_UPDATE`, `TRAIL_DEFERRED`, `POSITION_LIFECYCLE`, and `TELEGRAM_DEAL_LIFECYCLE` events by the recorded position identifier. The ZIP stays on the operator's PC.

## Run

Run from the isolated forensic worktree after pulling the latest draft PR branch:

```powershell
$py = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$zip = Join-Path $HOME "SP2L_PRIVATE_AUDIT_20261102_20261107.zip"
$out = "artifacts\forensic\v31-local-20261108"

& $py -m pytest -q tests\test_sp2l_v31_position_event_timeline.py
if ($LASTEXITCODE -ne 0) { throw "Timeline synthetic tests failed" }

& $py scripts\sp2l_v31_position_event_timeline.py --zip $zip --out $out --broker-server-offset-hours 2 2>&1 |
    Tee-Object -Variable timelineOutput
if ($LASTEXITCODE -ne 0) { throw "Timeline analysis failed" }

$timelineOutput | Set-Clipboard
Write-Host "TIMELINE_SUMMARY_COPIED_TO_CLIPBOARD"
```

## Outputs

- `v31_position_event_timeline.csv`: chronological entry/exit deal rows plus observed runner lifecycle/trailing events.
- `v31_position_event_summary.csv`: one compact row per position, including first/last recorded SL changes, deferred events, and elapsed time from entry to first recorded trail update when timestamps permit.
- `v31_event_timeline_summary.json`: event counts, ZIP identity, candidate price-data archive members, and explicit limitations.

## MFE/MAE boundary

The runner's `TRAIL_UPDATE` records include `bar_high` and `bar_low`, but only for bars on which a trail evaluation reached the update/logging point. Those sparse extrema do not cover every bar/tick during each holding interval. They must not be labeled MFE/MAE and cannot establish that a position had or lacked a trailing opportunity.

The script lists archive members whose names suggest tick/bar/rate data, but does not assume an undocumented schema or calculate excursions from unvalidated data. A separate price-data adapter must be added only after the archive member format, timestamp basis, symbol, bid/ask semantics, and coverage are inspected and validated.

No strategy geometry, fill semantics, SL anchor, causal trailing effect, or production rule is inferred.


## Broker timestamp alignment

The analyzer preserves each broker-derived timestamp in `timestamp_raw`. The optional
`--broker-server-offset-hours` argument subtracts the explicitly supplied offset from
broker entry/exit deal timestamps only. It never shifts Runner `ts_utc` events.
For the archived run whose runner configuration pinned server offset `2`, use
`--broker-server-offset-hours 2` as shown above. Compare the resulting broker rows
against Runner lifecycle timestamps before treating the alignment as validated.
The default remains `0` (no adjustment); the analyzer does not infer an offset.
