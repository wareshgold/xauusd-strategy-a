# Factory DEVELOPMENT Tick Receipt Tool Contract — 2026-10-28

## Purpose

The script scripts/audit_factory_dev_tick_dataset.py is a read-only integrity and basic Bid/Ask audit for one fixed DEVELOPMENT artifact. It creates a new JSON receipt from the existing compressed tick file and its acquisition manifest.

It is not a generic dataset importer, a strategy engine, or a canonical-rule authority. It does not touch MT5, trading runners, the source dataset, or the source manifest.

## Fixed input contract

- Artifact: xauusd-ecn-ticks-20260821_20260919.csv.gz
- Manifest: xauusd-ecn-ticks-20260821_20260919.manifest.json
- Dataset ID: xauusd-ecn-tick-bidask-20260821-20260919
- Role: DEVELOPMENT
- Interval: [2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)
- Required schema: time_msc,time_utc,bid,ask,last,volume,flags

The tool refuses unexpected filenames, manifest identity/interval/purpose mismatches, hash/size/row-count mismatches, invalid numeric/timestamp data, observed timestamps outside the declared half-open UTC interval, nonpositive or missing Bid/Ask, crossed quotes, and out-of-order rows. Duplicate millisecond timestamps are reported, not removed. Gaps are reported, not filled or automatically attributed to a cause.

The tool computes the compressed file SHA-256, manifest SHA-256, row count, timestamp consistency, quote checks, duplicate groups, large gaps, and basic spread summaries. It refuses to overwrite an existing receipt or either input path. The receipt output is created exclusively at the requested path.

## Example PowerShell invocation

Run from the repository worktree after installing its declared Python dependencies:

~~~powershell
$Repo = "D:\Mirzaei\Private\1\xauusd-strategy-a-factory-candidate-lab"
$Python = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$Data = Join-Path $Repo "data\raw\ticks"
$Receipt = Join-Path $Repo "artifacts\factory\receipts\DEV_XAUUSD_TICKS_20260821_20260919.json"

& $Python (Join-Path $Repo "scripts\audit_factory_dev_tick_dataset.py") --dataset (Join-Path $Data "xauusd-ecn-ticks-20260821_20260919.csv.gz") --manifest (Join-Path $Data "xauusd-ecn-ticks-20260821_20260919.manifest.json") --output $Receipt

if ($LASTEXITCODE -ne 0) { throw "Factory development tick audit failed" }
~~~

The receipt directory is only created if absent; if the chosen receipt filename already exists, the command fails rather than replacing evidence. Choose a new explicitly reviewed receipt path for a rerun; do not delete or overwrite prior receipts.

## Output and gate meaning

The JSON receipt carries input identities, observed counts/checks, limitations, and gate statuses. Its successful status means only that the fixed artifact passes the encoded integrity and basic quote checks.

- Gate A is approved for limited DEVELOPMENT tooling use only. The receipt must explicitly retain `UNANCHORED_OBSERVED_DIGEST` provenance; the approval does not authenticate acquisition provenance or permit strategy-performance backtests.
- Gate B remains blocked until executable geometry and semantics are source-confirmed. Strategy-performance backtests and Fresh Holdout use remain prohibited under the limited approval.
- Gate C remains blocked until the adapter/execution contract and required synthetic/reproducibility tests are approved.
- Gate D remains blocked until all prerequisite gates pass.

The tool only recognizes the fixed DEVELOPMENT interval [2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z) and rejects every observed tick timestamp before the inclusive start or at/after the exclusive end, as well as a manifest interval extending beyond the Fresh Holdout boundary 2026-09-19T00:00:00Z. It does not open, hash, parse, or otherwise read holdout data. The current data source is not modified or transformed, and the tool does not authorize backtests, production, or BUY/SELL decisions.


## Duplicate timestamp group diagnostics

The receipt includes these deterministic, aggregate-only fields:

- `duplicate_timestamp_groups_size_2`: consecutive timestamp groups containing exactly two rows.
- `duplicate_timestamp_groups_size_3_plus`: consecutive timestamp groups containing three or more rows.
- `max_rows_in_timestamp_group`: maximum number of consecutive rows sharing one millisecond timestamp, including singleton groups in the maximum calculation.
- `duplicate_groups_with_different_bid_ask`: duplicate groups containing more than one distinct Bid/Ask pair.
- `duplicate_groups_with_same_bid_ask`: duplicate groups containing exactly one distinct Bid/Ask pair.

These are descriptive counts, not diagnoses of feed corruption, ordering semantics, quote validity, executable prices, or trade events. The audit preserves source row order and all duplicate rows; it does not sort, deduplicate, choose a preferred quote, or infer why repeated timestamps occur. The aggregate fields are intended to guide a later source-evidence review, not to authorize strategy-performance backtests or rule selection.
