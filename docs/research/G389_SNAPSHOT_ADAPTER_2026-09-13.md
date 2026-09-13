# G389 — Read-only Snapshot Adapter

Date: 2026-09-13

## Status

**READ-ONLY ADAPTER READY; CANONICAL STRATEGY DEV BLOCKED.**

G389 maps the audited repository snapshot schema into the common G386/G388 candle contract and routes it through the same deterministic dataset runner.

## Invariants

- source metadata is preserved;
- dataset version is explicit;
- no mutation of raw snapshot is performed;
- DEV/VAL/HOLDOUT use the existing chronological policy;
- the adapter cannot create canonical trades;
- identical snapshot/config inputs use the same runner path.

## Real snapshot reference

The repository audit report identifies the current Twelve Data XAU/USD snapshots as 50,000 M1 candles and 50,000 M5 candles, with audit status PASS. M5 has four ordinary gaps and a largest gap of 65 minutes; none are classified suspicious.

## Boundary

G389 does not infer Strategy A geometry and therefore does not open canonical backtesting. Frozen Geometry remains BLOCKED.
