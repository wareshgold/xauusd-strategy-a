# V3 Discovery artifact audit

This tool audits an already completed `SP2L_V3_CONTROLLED_DISCOVERY` run and writes a compact evidence manifest beside the run artifacts.

## Run

From the repository root, using the research Python environment:

```powershell
& "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe" `
  scripts\audit_v3_discovery_artifacts.py `
  --run-json "D:\Mirzaei\Private\1\sp2l-evidence\development\v3-exit-discovery-20261101\SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z.json"
```

The command prints one concise `AUDIT=PASS` or `AUDIT=FAIL` line. On success it creates `SP2L_V3_CONTROLLED_DISCOVERY_<timestamp>_EVIDENCE_MANIFEST.json` beside the run artifacts. The manifest is created only if the target does not already exist. Original run artifacts are read-only and are never rewritten.

## Fail-closed checks

- Confirms the run is explicitly research-only and uses the expected V3 Discovery version and M1 timeframe.
- Resolves M1 and frozen-entry source paths from `dataset_provenance.artifact` and `frozen_population.artifact`.
- Re-hashes both source artifacts and checks their recorded SHA-256 values; checks M1 byte size when supplied.
- Requires the frozen V3 entry CSV source and shared-population policy.
- Checks JSON matrix count, Summary CSV rows, Trades CSV rows, and embedded JSON trade count.
- Checks every variant has exactly the frozen number of trades and replays the same unique `(trigger_time, direction, theoretical_entry, initial_sl)` identities.
- Compares summary statistics in CSV against the JSON matrix.
- Verifies the Snapshot embeds the exact SHA-256 of the JSON artifact.
- Writes hashes and byte sizes for all six artifacts into the manifest.

The tool does not upload data, place orders, change strategy rules, choose a production candidate, or establish statistical significance. The manifest records research provenance and structural consistency only. M1 OHLC replay still omits spread, slippage, and commission.
