# Dataset Provenance Gate — 2026-09-14

## Objective

Turn the existing GitHub-hosted XAUUSD historical datasets into auditable replay inputs without changing Strategy A semantics.

## Existing source

The repository already contains:

- `data/historical/xauusd-1min.json`
- `data/historical/xauusd-5min.json`

The acquisition script identifies Twelve Data as the provider, uses `XAU/USD`, and writes UTC timestamps. The provenance audit independently verifies those metadata fields before accepting the dataset.

## Gate checks

For each dataset the audit records:

- source/provider;
- symbol and timeframe;
- timezone;
- schema version;
- row count;
- first/last timestamp;
- canonical OHLC content fingerprint (SHA-256);
- raw-file fingerprint (SHA-256);
- duplicate timestamps;
- invalid OHLC rows;
- non-chronological rows;
- gap count and suspicious non-weekend gaps.

The gate PASS condition currently covers structural integrity: no duplicate timestamps, invalid OHLC rows, or non-chronological rows. Gaps are reported rather than silently repaired or discarded.

## Important boundary

A PASS does **not** mean the feed is complete, authoritative, broker-equivalent, or suitable for production. It establishes reproducible dataset identity and basic structural integrity only.

No candles are modified, interpolated, or gap-filled by this audit.

## Strategy-A boundary

This gate does not resolve P-Gap geometry, A/B/C/D anchors, entry-fill semantics, structural stop boundary, target mapping, or any other unresolved source geometry.

Only after this gate is reproducibly executable should the dataset enter DEV replay/backtest work.
