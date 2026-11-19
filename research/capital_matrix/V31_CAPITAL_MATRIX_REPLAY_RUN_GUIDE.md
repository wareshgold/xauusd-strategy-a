# Run the V3.1 capital matrix replay on the Factory PC

This is an offline, read-only historical replay. It does not import MetaTrader5, connect to a terminal, send orders, or modify the forward runner.

## Scope and assumptions

- Replays the 40 Fixed-TP and 9 Runner configurations (49 total).
- Keeps all 40 Dual configurations in the 89-run matrix definition but marks them unexecuted because the V3.1 gateway's default one-exposure guard cannot submit two independent legs.
- Uses the audited frozen 1,518-entry population and exact SHA-pinned M1/Tick inputs.
- Baseline submission time is the first available Tick at or after the trigger M1 bar close plus 2 seconds. This is a declared approximation, not a recorded historical order timestamp.
- BUY limit fill condition: Ask <= theoretical limit. SELL limit fill condition: Bid >= theoretical limit. Fill price is the executable quote on the first eligible tick.
- Pending orders expire after 30 minutes. Each portfolio has one exposure slot, counting both pending and open positions.
- BUY exits use Bid; SELL exits use Ask. Theoretical SL/TP levels remain fixed as submitted by the V3.1 runner.
- Runner trailing is updated only on completed M1 bars, activation 0.40 and distance 0.40. Historical broker minimum stop distance is unavailable and is assumed zero in this initial replay; treat trailing results as conditional on that assumption.
- Commission, swap and slippage are not included. Results are gross-only. Trades spanning any Tick gap >60 seconds are flagged.
- Open positions/pending orders at the end of Tick coverage are censored, not force-closed.
- These are modeled fills, not proof of actual historical broker fills. No ranking or Fresh Holdout promotion is performed.

## Factory PC command

Run in PowerShell. It verifies the branch, fast-forwards it without overwriting local edits, creates a new output directory, runs the replay, and copies a concise result to the clipboard. It can take a while because it streams 31.8 million ticks.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\Mirzaei\Private\1\xauusd-capital-matrix-20261119'
$Branch = 'research/capital-management-matrix-20261119'
$Python = 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe'
$Evidence = 'D:\Mirzaei\Private\1\sp2l-evidence\development\v31-three-month-population-gap-isolated'
$Raw = 'D:\SP2L_RESEARCH_DATA\20261109'
$Out = 'D:\Mirzaei\Private\1\sp2l-evidence\development\capital-matrix-replay-v1-2s'
$Log = Join-Path $env:TEMP 'sp2l_capital_matrix_replay.log'

Set-Location $Repo
if ((git branch --show-current) -ne $Branch) { throw 'STOP: wrong branch; no files changed.' }
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'STOP: fast-forward update failed; local work was not overwritten.' }
if (-not (Test-Path $Python)) { throw 'STOP: research Python environment not found.' }
if (Test-Path $Out) { throw "STOP: output directory already exists: $Out" }

& $Python -u "$Repo\research\capital_matrix\replay_v31_tick_matrix.py" `
  --population "$Evidence\SP2L_V31_THREE_MONTH_FROZEN_ENTRIES.csv" `
  --population-manifest "$Evidence\SP2L_V31_THREE_MONTH_FROZEN_ENTRIES_MANIFEST.json" `
  --m1-csv-gz "$Raw\XAUUSD_ecn_20260809_20261110_M1.csv.gz" `
  --ticks-csv-gz "$Raw\XAUUSD_ecn_20260809_20261110_ticks.csv.gz" `
  --output-dir $Out *> $Log
$Exit = $LASTEXITCODE

if ($Exit -eq 0) {
    $Summary = Import-Csv "$Out\SP2L_CAPITAL_MATRIX_RUN_SUMMARY.csv" |
      Select-Object run_id,closed_trades,gross_net_usd,profit_factor,win_rate,average_r,max_drawdown_fraction
    $Manifest = Get-Content "$Out\SP2L_CAPITAL_MATRIX_REPLAY_MANIFEST.json" -Raw | ConvertFrom-Json
    $Report = @(
      "REPLAY_EXIT=0"
      "STATUS=$($Manifest.status)"
      "TICKS=$($Manifest.tick_stats.tick_rows)"
      "LATENCY_SECONDS=$($Manifest.tick_stats.latency_seconds)"
      "DUAL_RUNS=$($Manifest.dual_status)"
      "OUTPUT=$Out"
      ($Summary | Format-Table -AutoSize | Out-String)
    ) -join "`r`n"
} else {
    $Report = "REPLAY_EXIT=$Exit`r`n" + ((Get-Content $Log -Tail 60) -join "`r`n")
}
$Report | Set-Clipboard
$Report
```

## Latency sensitivity

After the baseline output is audited, rerun into a *different new directory* with `--latency-seconds 0` and `--latency-seconds 5`. Never overwrite an existing run. Compare fill rates, rejected orders, gross results, and gap-exposed trades. Do not combine the three runs into one ranking without recording the latency assumption.

## Outputs

- `SP2L_CAPITAL_MATRIX_TRADE_REPLAY.csv`: trade/candidate lifecycle rows.
- `SP2L_CAPITAL_MATRIX_RUN_SUMMARY.csv`: one summary row per executable configuration.
- `SP2L_CAPITAL_MATRIX_REPLAY_MANIFEST.json`: assumptions, source hashes, output hashes, data coverage and limitations.
- PowerShell log: `%TEMP%\sp2l_capital_matrix_replay.log`.
