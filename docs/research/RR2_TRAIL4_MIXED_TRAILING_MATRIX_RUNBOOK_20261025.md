# RR2/TRAIL4 Mixed Trailing Matrix — Research Runbook (2026-10-25)

## Purpose

Compare trailing-management variants while holding the RR2/TRAIL4 candidate generation, theoretical entry, initial SL, and fixed initial TP constant. Includes a **no-trailing fixed-SL/TP baseline** evaluated on the same candidate set.

This is research-only. It does not change the live runner or make any parameter canonical.

## Matrix

The default grid produces **26 scenarios**:

- Baseline: no trailing, fixed initial SL and TP (1 scenario).
- Activation threshold (favorable XAUUSD price move): `0.00, 0.05, 0.10, 0.20, 0.40`.
- Trailing distance from completed-bar favorable extreme: `0.02, 0.04, 0.10, 0.20, 0.40`.
- Trailing combinations: 5 × 5 = 25, plus the baseline.

All distances are **XAUUSD price units**, not pips or broker points. With the RR2/TRAIL4 config's display convention (1 pip = 0.10 price), 0.04 price is 0.4 of that pip convention; 0.40 price is 4.0 pips. The MT5 point is 0.01, so 0.04 and 0.40 correspond to 4 and 40 broker points respectively.

Activation 0.00 means the first eligible completed-bar check can create a trail; the stop derived from a bar is eligible only from the next bar. It does not mean tick-by-tick trailing.

## Frozen / held constant

- Config module: `sp2l_v3_rr2_trail4_config`.
- Signal detection and primary-entry selection are unchanged.
- The same candidate's theoretical entry, initial SL, initial TP, and risk are reused in every scenario.
- One primary entry per candidate; 2X secondary entries remain excluded.
- TP remains fixed at the initial RR2 target.
- SL/TP hits are evaluated using levels active before the bar. If both are touched on the same bar, the trade is marked ambiguous and excluded from decisive metrics.
- A newly calculated trail applies starting on the next completed M1 bar.
- If a bar opens beyond an active stop, the simulator fills at the adverse bar open rather than assuming a fill at the stop level. The gap count and aggregate adverse price difference are reported.
- Intrabar tick sequence, broker-specific execution, spread, commissions, swap, non-gap slippage, rejection, account sizing and margin are not modeled.

## Run

Run from the RR2/TRAIL4 research worktree on Windows, with the configured MT5 terminal and Python environment available. The script obtains M1 bars from MT5; it does not alter orders or the live runner.

```powershell
$ErrorActionPreference = "Stop"
$Repo = (Get-Location).Path
$Python = Join-Path $Repo "..\xauusd-strategy-a\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$Script = Join-Path $Repo "scripts\run_sp2l_v3_xauusd_trailing_matrix.py"
$Terminal = "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"

& $Python $Script `
  --mt5-path $Terminal `
  --symbol "XAUUSD.ecn" `
  --start "2026-07-13T00:00:00+00:00" `
  --end "2026-10-15T00:00:00+00:00" `
  --config-module "sp2l_v3_rr2_trail4_config" `
  --activation-prices "0.00,0.05,0.10,0.20,0.40" `
  --trail-distances "0.02,0.04,0.10,0.20,0.40"
if ($LASTEXITCODE -ne 0) { throw "Mixed trailing matrix failed with exit code $LASTEXITCODE" }
```

The script creates new timestamped JSON, matrix CSV, trade CSV and snapshot files under `artifacts\v3`; it does not overwrite prior matrix artifacts.

## Data identity gate

The prior 2026-10-15 matrix reported 93,628 M1 bars and SHA-256 beginning `d5d339c` (full hash recorded in its original snapshot). Before comparing the new run with that historical matrix, verify that the full bar count and SHA-256 match the prior snapshot. If either differs, label the result a **new data snapshot** and do not attribute differences solely to trailing parameters.

## Readout / interpretation

For each scenario compare decisive trades, ambiguous rows, unresolved/open rows, win rate, gross R/PF, max consecutive losses, max concurrency, drawdown in exit-time order, gap-through-stop count, and aggregate gap slippage. A stop gap can still be worse than the modeled stop; this change only avoids assuming a fill at an already-crossed stop price. The reported drawdown is not portfolio drawdown because independent candidates can overlap.

The baseline is included once rather than duplicated for every distance. Never rank scenarios on net R alone; inspect unresolved/ambiguous counts, time stability, direction/exit-reason breakdowns, costs and broker execution limitations. A single historical window is exploratory, not proof of a statistically validated edge. Reserve an untouched fresh holdout after source rules and parameters are frozen.

## Authority boundary

This matrix compares implementation assumptions. It cannot resolve source meaning for trailing activation, distance, step size, tick-vs-bar evaluation, fill semantics, or Strategy A geometry. No scenario is canonical or authorized for production from this report alone.
