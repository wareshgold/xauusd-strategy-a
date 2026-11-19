# V3.1 Three-Month Frozen Population Builder

Research-only offline builder for the audited three-month XAUUSD.ecn M1 source.

## What it does

- Requires exact audited source SHA-256 `daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402`.
- Accepts the observed CSV header (`time`, `time_utc`, `spread_points`) and maps it explicitly to the pinned V3.1 config schema.
- Validates 89,866 rows and audited first/last UTC timestamps.
- Splits the M1 series at every timestamp delta other than exactly 60 seconds. Setup detection and first-entry search operate inside one contiguous segment only; no search can cross a gap.
- Preserves every gap in the manifest. It does not interpolate, repair, or infer session calendars.
- Pins a copy of `sp2l_v3_1_rr4_act40_config.py` from branch `feat/v31-monitor-control-center-20261116`.
- Writes a new CSV and manifest with exclusive-create semantics. A non-empty output directory is rejected.

This is a research replica, not canonical Strategy A source confirmation. The population freezes entries only; exits remain blank for later management replay.

## Local run

After pulling the branch into the capital-matrix worktree:

```powershell
Set-Location D:\\Mirzaei\\Private\\1\\xauusd-capital-matrix-20261119
$py = "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe"
$src = "D:\\SP2L_RESEARCH_DATA\\20261109\\XAUUSD_ecn_20260809_20261110_M1.csv.gz"
$out = "D:\\Mirzaei\\Private\\1\\sp2l-evidence\\development\\v31-three-month-population-gap-isolated"

& $py -m unittest tests.research.test_v31_population_builder -v
if ($LASTEXITCODE -ne 0) { throw "Builder tests failed: $LASTEXITCODE" }

& $py .\\research\\capital_matrix\\build_v31_three_month_population.py `
  --m1-csv-gz $src `
  --m1-sha256 daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402 `
  --symbol XAUUSD.ecn `
  --output-dir $out
if ($LASTEXITCODE -ne 0) { throw "Population build failed: $LASTEXITCODE" }

Get-Content "$out\\SP2L_V31_THREE_MONTH_FROZEN_ENTRIES_MANIFEST.json" -Raw | Set-Clipboard
```

Do not reuse an existing output directory. Keep the generated CSV and manifest immutable.

## Acceptance gate after local execution

1. Confirm `status=COMPLETE`, source SHA, 89,866 rows, first/last timestamps.
2. Confirm reported gap count and segment count; compare the gap count with the earlier acquisition audit (66) and investigate any discrepancy.
3. Review monthly/direction population counts for empty months or unexpected concentration.
4. Independently hash both output files and retain them with the run record.
5. Do not run the 89 capital-management configurations until the population output and manifest have been reviewed and accepted.

## Safety

The builder imports only the pinned local research config. It does not import MetaTrader5, connect to a terminal, inspect runner processes, access live state, send orders, or modify source data. It only writes into the explicitly supplied output directory.
