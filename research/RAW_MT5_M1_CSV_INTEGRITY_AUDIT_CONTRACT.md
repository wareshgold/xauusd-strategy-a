# Raw MT5 M1 CSV Integrity Audit Contract

## Purpose
The read-only audit validates raw M1 CSV bytes and structure before research uses them. It reports the exact working-copy SHA-256 and separately checks the manifest SHA-256 against bytes normalized from CRLF to LF. This accommodates Git's configured Windows checkout conversion without modifying the source CSV. It also checks the required MT5 bar columns, UTC minute timestamps, strict ordering, duplicates, OHLC bounds, non-negative volume fields, row count, artifact identity, and declared request interval. The normalized hash is only a line-ending compatibility check; any other byte/content difference remains a hash failure.

## Non-goals
- It does not infer broker session hours, market closures, holidays, UTC offsets, DST, or whether an observed timestamp gap is expected.
- Timestamp gaps are emitted as `UNCLASSIFIED_TIMESTAMP_GAP`; they are never automatically accepted as session closures.
- Manifest `expected_active_bar_count` is diagnostic only when historical applicability of the session calendar is unverified. It cannot override source evidence or turn this audit into session approval.
- A structural pass does not establish data completeness, canonical Strategy A geometry, or trading readiness.

## Invocation
```powershell
python scripts/sp2l_raw_m1_csv_integrity_audit.py data/mt5-acquisition/xauusd-ecn-m1-2026-07.csv --manifest data/mt5-acquisition/xauusd-ecn-m1-2026-07.manifest.json --output artifacts/research/raw-m1-audit-2026-07.json
```

The source CSV and manifest are read-only. The optional output is a separate research report. `csv_sha256` records exact bytes as found in the working copy; `csv_sha256_lf_normalized` records the hash used for manifest comparison. CRLF normalization is performed in memory only.
