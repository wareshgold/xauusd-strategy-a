# Monthly trailing stability audit — runbook (2026-10-25)

## Purpose

This is the next research step after the initial approximately 30-day OHLC proxy comparison: inspect **daily and weekly stability**, UTC exit-day contribution, results by direction and exit reason, and chronological candidate-sequence drawdown for the three A scenarios:

- fixed SL/TP proxy,
- V1 trailing proxy (updates after any favorable excursion),
- V3 trailing proxy (activation gate at 0.40 price units).

It does not choose a canonical rule. The 0.40 distance and V3 activation gate remain research assumptions until primary-source evidence resolves them.

## Inputs

Use the immutable trade CSVs already produced by the local V1/V3 runs. Expected paths in the monthly-matrix audit worktree:

- Fixed SL/TP: `artifacts\monthly_ohlc_activated_sensitivity_20261024_162125_400\a_fixed_sl_tp_trades.csv`
- V1: `artifacts\monthly_ohlc_activated_sensitivity_20261024_162125_400\a_trail_0_40_activated_proxy_trades.csv`
- V3: `artifacts\monthly_ohlc_activated_sensitivity_v3_20261024_162634_105\a_trail_0_40_activated_proxy_v3_trades.csv`

If the fixed CSV is not present at that exact path, do not create or overwrite it. Locate the existing fixed CSV and verify its SHA256 matches the previously reported fixed-trade hash before running.

## PowerShell invocation

Run from the repository worktree root. The output folder must be new or empty; the script refuses to overwrite a non-empty directory.

```powershell
$ErrorActionPreference = "Stop"
$Out = ".\artifacts\monthly_trailing_stability_20261025"
if (Test-Path $Out) {
    if ((Get-ChildItem -LiteralPath $Out -Force | Measure-Object).Count -gt 0) {
        throw "Output directory is not empty; preserve it and choose a new timestamped folder: $Out"
    }
} else {
    New-Item -ItemType Directory -Path $Out | Out-Null
}
python .\scripts\research\monthly_matrix_trailing_stability_audit.py `
  --fixed-csv ".\artifacts\monthly_ohlc_activated_sensitivity_20261024_162125_400\a_fixed_sl_tp_trades.csv" `
  --v1-csv ".\artifacts\monthly_ohlc_activated_sensitivity_20261024_162125_400\a_trail_0_40_activated_proxy_trades.csv" `
  --v3-csv ".\artifacts\monthly_ohlc_activated_sensitivity_v3_20261024_162634_105\a_trail_0_40_activated_proxy_v3_trades.csv" `
  --out $Out
if ($LASTEXITCODE -ne 0) { throw "Stability audit failed with exit code $LASTEXITCODE" }
Get-ChildItem -LiteralPath $Out | Select-Object Name,Length
Get-Content -LiteralPath (Join-Path $Out "report.md")
```

Before running, check the input hashes and path names against the immutable snapshot manifest. Do not stage or modify the source CSVs.

## Outputs

- `summary.json`: input hashes, definitions, per-scenario summary and guardrails.
- `fixed_daily.csv`, `v1_daily.csv`, `v3_daily.csv`: closed proxy outcomes grouped by UTC exit date.
- Corresponding `*_weekly.csv` files: grouped by ISO week of UTC exit.
- Corresponding `*_by_direction.csv` and `*_by_exit_reason.csv` files.
- `report.md`: concise scenario comparison.

## Interpretation rules

- Unresolved trades are counted but excluded from closed-trade R totals.
- Daily and weekly buckets use **exit time**, not setup time or entry time.
- Chronological candidate-sequence drawdown sorts closed candidate rows by exit time. If candidate intervals overlap, this is **not** portfolio drawdown.
- Period-end drawdown is computed on cumulative daily/weekly R, not intraday equity.
- Costs are not added by this tool. It must not imply realized cash P&L or broker fills.
- One approximately 30-day sample can describe concentration and instability, but cannot establish a robust edge. Preserve a fresh untouched holdout after any rule freeze.

## Validation status

The script and focused unit tests are committed on the research branch. They must be run in the target Windows worktree before treating the generated report as validated output. No production code or runner settings are changed.
