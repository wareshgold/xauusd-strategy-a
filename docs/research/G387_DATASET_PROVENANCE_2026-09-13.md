# G387 — Dataset Provenance & Snapshot Lock

Date: 2026-09-13

## Status

**PROVENANCE RECORDED; IMMUTABLE SNAPSHOT LOCK PENDING RAW-FILE HASH CAPTURE.**

The repository already contains an audited XAU/USD historical snapshot. The audit report records 50,000 M1 candles and 50,000 M5 candles with zero duplicates, zero invalid OHLC records, zero non-chronological records, and zero suspicious gaps. M5 has four ordinary gaps, with the largest 65 minutes.

## Snapshot identity

- Provider: Twelve Data
- Symbol: XAU/USD
- Timezone: UTC
- M1 coverage: 2026-08-03 13:44 → 2026-09-07 07:03
- M5 coverage: 2026-03-17 15:15 → 2026-09-07 07:05
- Candle count: 50,000 per timeframe
- Audit status: PASS

These values are recorded in `G387_DATASET_SNAPSHOT_MANIFEST_2026-09-13.json`.

## Integrity rule

The raw dataset is treated as immutable for a research run. Any refresh creates a new dataset version rather than silently replacing an existing snapshot. A production or validation result must identify its exact provider, timeframe, coverage and dataset version.

## Important limitation

The current repository evidence did not expose a verified SHA-256 for the large raw JSON snapshots in this pass. Therefore G387 does **not** invent or claim a raw-file hash. The snapshot is provenance-identified, but the cryptographic lock remains pending until the exact raw bytes are available for hashing.

## Strategy gate

This provenance work does not resolve P-Gap geometry, A/B/C/D anchors, entry/fill semantics, SL boundary, or TP mapping. Consequently **Frozen Geometry remains BLOCKED** and no canonical Strategy A DEV/backtest is authorized.
