# SP2L V3.1 Partial-Close Matrix — Factory Run Guide

## Scope

This is an offline, research-only Tick replay. It does not import MetaTrader5,
connect to a terminal, access the forward runner, send orders, or change live
configuration.

The partial family contains **27 variants**:

- **3 fixed-volume references:** one 0.02-lot position, with 0.01 lot closed at
  1R and the remaining 0.01 lot closed at 2R, 3R, or 4R with the V3.1
  0.40/0.40 completed-M1 trailing profile.
- **24 risk-normalized variants:** 4 risk levels (0.25%, 0.50%, 0.75%, 1.00%)
  × 2 sizing modes (Compound, Fixed Base) × the same 3 exit policies.

For normalized sizing, the *aggregate* requested risk budget applies to the
whole position. Total volume is rounded **down** in 0.02-lot increments so it
can be split into two equal legs. Each leg must be at least the broker minimum
0.01 lot. If two valid legs cannot fit inside the budget, the run is marked
infeasible; volume is never rounded up.

## Exit semantics

- One pending entry and one position, not two independently submitted orders.
- Initial position consists of two equal legs.
- TP1 closes the first leg at 1R.
- The second leg closes at 2R or 3R, or has a 4R target with V3.1 trailing
  activation 0.40 and distance 0.40.
- The initial SL is retained; no break-even move is introduced.
- For the Runner variant, trailing is updated on completed M1 bars and applies
  to the still-open position before and after TP1.
- BUY exits use Bid; SELL exits use Ask. If SL and TP conditions conflict on
  the same quote, SL is prioritized.
- Partial close is modeled as two 0.01-lot legs on one entry. It is not a
  broker-specific API validation and does not prove that a live broker will
  accept a particular partial-close request.

## Factory PC command

Run in PowerShell. This creates a new evidence directory, runs the 2-second
latency scenario, and copies a concise summary to the clipboard. Tick replay
streams the 31.8-million-row source.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\Mirzaei\Private\1\xauusd-capital-matrix-20261119'
$Branch = 'research/capital-management-matrix-20261119'
$Python = 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe'
$Evidence = 'D:\Mirzaei\Private\1\sp2l-evidence\development\v31-three-month-population-gap-isolated'
$Raw = 'D:\SP2L_RESEARCH_DATA\20261109'
$Out = 'D:\Mirzaei\Private\1\sp2l-evidence\development\partial-matrix-replay-v1-2s'
$Log = Join-Path $env:TEMP 'sp2l_partial_matrix_replay.log'

Set-Location $Repo
if ((git branch --show-current) -ne $Branch) { throw 'STOP: wrong branch.' }
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'STOP: fast-forward failed; local work was not overwritten.' }
if (-not (Test-Path $Python)) { throw 'STOP: research Python environment not found.' }
if (Test-Path $Out) { throw "STOP: output directory already exists: $Out" }

& $Python -u -m research.capital_matrix.replay_v31_partial_matrix `
  --population "$Evidence\SP2L_V31_THREE_MONTH_FROZEN_ENTRIES.csv" `
  --population-manifest "$Evidence\SP2L_V31_THREE_MONTH_FROZEN_ENTRIES_MANIFEST.json" `
  --m1-csv-gz "$Raw\XAUUSD_ecn_20260809_20261110_M1.csv.gz" `
  --ticks-csv-gz "$Raw\XAUUSD_ecn_20260809_20261110_ticks.csv.gz" `
  --symbol-specs "$Raw\XAUUSD_ecn_20260809_20261110_symbol_specs.json" `
  --output-dir $Out *> $Log
$Exit = $LASTEXITCODE

if ($Exit -eq 0) {
    $Summary = Import-Csv "$Out\SP2L_PARTIAL_MATRIX_RUN_SUMMARY.csv" |
      Select-Object run_id,closed_trades,closed_legs,gross_net_usd,profit_factor,win_rate,average_r,max_drawdown_fraction
    $Manifest = Get-Content "$Out\SP2L_PARTIAL_MATRIX_REPLAY_MANIFEST.json" -Raw | ConvertFrom-Json
    $Report = @(
      "REPLAY_EXIT=0"
      "STATUS=$($Manifest.status)"
      "RUNS=$($Manifest.partial_matrix_runs)"
      "FIXED_REFERENCES=$($Manifest.fixed_volume_references)"
      "RISK_NORMALIZED=$($Manifest.risk_normalized_variants)"
      "TICKS=$($Manifest.tick_stats.tick_rows)"
      "LATENCY_SECONDS=$($Manifest.tick_stats.latency_seconds)"
      "OUTPUT=$Out"
      ($Summary | Format-Table -AutoSize | Out-String -Width 240)
    ) -join "`r`n"
} else {
    $Report = "REPLAY_EXIT=$Exit`r`n" + ((Get-Content $Log -Tail 80) -join "`r`n")
}
$Report | Set-Clipboard
$Report
```

## Latency sensitivity

After auditing the 2-second run, repeat with new output directories and
explicit `--latency-seconds 0` and `--latency-seconds 5`. Do not overwrite or
delete existing evidence. Keep the three latency runs separate until their
manifests and input/code hashes have been compared.

## Important limitations

- Gross-only: commission, swap, and calibrated slippage are absent.
- Submission timing is an explicit approximation: first Tick at or after the
  trigger bar close plus declared latency.
- Broker minimum stop distance is unavailable; trailing placement assumes zero.
- Tick gaps over 60 seconds are flagged; open/pending positions at end of Tick
  coverage are censored, not force-closed.
- These are modeled historical fills, not proof of actual broker fills.
- This is not a winner selection. Validation and locked Fresh Holdout remain
  pending. No live runner settings are changed.
