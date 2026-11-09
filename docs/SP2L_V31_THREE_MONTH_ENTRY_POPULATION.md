# V3.1 Three-Month Frozen Entry Population

Research-only preparation step for the three-month management matrix.

## Why this step exists

The 462-row frozen V3 entry CSV currently documented by the 30-day Discovery gate covers only 2026-09-24 through 2026-10-23. It cannot be relabeled as a three-month population.

This builder creates a new, byte-bound entry population from the preserved three-month M1 CSV.GZ using the declared V3.1 RR4/ACT40/TRAIL40 configuration. The V3.1 config inherits the prior V3 signal/entry functions; its RR4 target is carried as source metadata but prior exit outcomes are left blank. Every later management variant must use this one generated CSV and its exact SHA-256.

This does not resolve canonical P-Gap, AB=CD, stop-anchor, pending-fill, or intrabar execution semantics. The output remains a research population, not a canonical Strategy A claim.

## Input already audited

Expected M1 CSV.GZ SHA-256:

`daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402`

The audited source contains 89,866 M1 bars, from 2026-08-10T01:00:00Z through 2026-11-09T07:43:00Z. It is not a complete Aug 09-Nov 10 interval. The acquisition report identified 66 timestamp gaps; they must remain visible and be session-reviewed. No interpolation or gap repair is performed here.

## Offline command

Run from the research worktree after pulling this branch. Replace only the input path with the actual preserved M1 CSV.GZ location. Keep output in a new, empty evidence directory.

```powershell
Set-Location D:\Mirzaei\Private\1\xauusd-strategy-a
$py = ".\.venv\Scripts\python.exe"
$src = "D:\PATH\TO\XAUUSD_ecn_20260809_20261110_M1.csv.gz"
$out = "D:\Mirzaei\Private\1\sp2l-evidence\development\v31-three-month-entry-population"
& $py .\scripts\build_sp2l_v3_1_frozen_population_from_m1.py `
  --m1-csv-gz $src `
  --m1-sha256 daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402 `
  --symbol XAUUSD.ecn `
  --output-dir $out
if ($LASTEXITCODE -ne 0) { throw "Population build failed: $LASTEXITCODE" }
Get-Content "$out\SP2L_V3_1_FROZEN_ENTRY_POPULATION_MANIFEST.json" -Raw | Set-Clipboard
```

The builder is deliberately offline: it imports no MetaTrader5 package, makes no MT5 connection, reads the compressed source without modifying it, and uses exclusive-create output mode so an existing artifact cannot be overwritten. It does not start or inspect the forward runner or dashboard.

## Required acceptance checks

1. Source SHA-256 must equal the audited value above.
2. Manifest source row count and first/last UTC must match the acquisition audit.
3. Output population CSV and manifest SHA-256 values must be retained.
4. Every matrix run must bind the same population CSV SHA and the same M1 data SHA; no exit variant may rebuild or filter entries.
5. Record signal counts by month and direction before running management variants.
6. Preserve all 66 M1 gaps. Trades exposed to unresolved gaps remain ambiguous under the later replay policy; gaps are not silently filled.
7. Keep spread, commission, and slippage modeling separate from the raw entry population and calibrate costs from the audited tick data.
8. Do not rank/promote a candidate until chronological validation, robustness, and a genuinely untouched Fresh Holdout are complete.

## Safety boundary

This script contains no order API and does not import or initialize MT5. It does not alter runner code, runtime state, dashboard files, or any existing evidence.
