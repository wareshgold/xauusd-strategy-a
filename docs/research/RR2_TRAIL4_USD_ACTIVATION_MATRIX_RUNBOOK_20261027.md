# RR2/TRAIL4 USD-Activation Trailing Matrix — Research Runbook (2026-10-27)

## Purpose

This is a research-only trade-management matrix. It reuses the existing RR2/TRAIL4 candidate generator, theoretical entry, initial SL and fixed RR2 TP. It does not modify or interrupt the live runner and does not make any setting canonical.

The existing matrix uses favorable price movement, not USD floating profit. This companion matrix converts USD thresholds to XAUUSD price movement using the MT5 symbol contract size and configured volume. It refuses to run unless account currency and symbol profit currency are both USD.

## Frozen dimensions

Activation thresholds in gross USD: 0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3.
Trailing offsets in configured RR2/TRAIL4 pips: 4, 5, 10, 15, 20, 30, 40, 50.

The current config says XAU_PIP_SIZE_PRICE = 0.1. Under this explicit convention, 5 pips = 0.5 price and 50 pips = 5.0 price. This is not the MT5 point size. The run records contract size, account currency, profit currency, volume and the configured pip-price convention.

Default matrix: 66 scenarios (no-trailing baseline, current-runner-equivalent scenario, and 64 threshold/distance combinations). The current-runner equivalent activates when favorable price movement reaches the configured current trail distance and uses that same trailing offset. It is only a bar-model approximation and does not model live bid/ask stop/freeze rejection constraints.

## Simulation semantics and limitations

- Same candidate set, theoretical entry, initial SL, initial TP and risk for every variant.
- One primary entry per candidate; secondary 2X entries remain excluded.
- Trailing is calculated from completed M1 bars and a newly calculated stop is eligible from the next bar.
- TP remains fixed at the initial RR2 level.
- Same-bar SL and TP touches are ambiguous and excluded from decisive metrics.
- USD threshold conversion is gross linear XAUUSD: price move = threshold USD / (contract size × volume). It is not broker-calculated floating profit and excludes spread, commission, swap, slippage and currency-conversion effects.
- MFE/MAE use gross OHLC excursions. Theoretical entry and price-level fills are used; pending-order fills, broker constraints, gaps and stop slippage are not modeled.
- Drawdown is gross USD trade-sequence drawdown ordered by exit time, not portfolio/account drawdown. Independent trades may overlap.

## Local run (MT5 history required)

Run from the RR2/TRAIL4 research worktree using the configured Python environment.

```powershell
$ErrorActionPreference = "Stop"
$Repo = (Get-Location).Path
$Python = Join-Path $Repo "..\xauusd-strategy-a\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$Script = Join-Path $Repo "scripts\run_sp2l_v3_xauusd_usd_activation_matrix.py"
$Terminal = "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"

& $Python $Script `
  --mt5-path $Terminal `
  --symbol "XAUUSD.ecn" `
  --start "2026-09-15T00:00:00+00:00" `
  --end "2026-10-15T00:00:00+00:00" `
  --config-module "sp2l_v3_rr2_trail4_config"
if ($LASTEXITCODE -ne 0) { throw "USD activation matrix failed with exit code $LASTEXITCODE" }
```

This completed historical month is development/diagnostic data, not a fresh holdout. Freeze the experiment after reviewing results and reserve a separate untouched period for validation.

The script writes timestamped JSON, summary CSV, trade-level CSV and Markdown snapshot under artifacts/v3 without overwriting earlier results. Compare bar count and SHA-256 with existing snapshots before attributing result changes to management parameters.

## Interpretation

Review gross net USD, PF, drawdown, positive exits below $1, MFE/MAE, exit reasons, ambiguous/open counts, and trades that reached $1/$2/$3 MFE but later closed below those levels. Do not rank variants by net P&L alone. Results are not net of costs and do not prove a statistical edge.
