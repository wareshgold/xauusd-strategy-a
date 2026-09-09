# SP2L G33 — Dataset Manifest + Regime Reporting

Date: 2026-09-09
Branch: `research/sp2l-infra-regime-g33-2026-09-09`

## Purpose
Build research infrastructure in parallel with unresolved Strategy A geometry.

## Added
- immutable `DatasetManifest` with provider, symbol, timeframe, UTC bounds, row count, source version and SHA-256 fingerprint;
- strategy-neutral rolling range descriptors for regime reporting;
- synthetic tests for manifest reproducibility and descriptive regime slices.

## Boundary
The regime descriptor is **descriptive only**. It is not a Strategy A session filter, entry filter, or optimization selector. No threshold here may be promoted into Strategy A without source confirmation and a separate research decision.

## Gate status
- SOURCE RESOLUTION: semantic PASS / executable geometry unresolved
- SYNTHETIC FIXTURES: PASS / ongoing
- FROZEN GEOMETRY: BLOCKED
- DEV and later: LOCKED

## Reproducibility
Dataset manifests are intended to be stored alongside every historical research run so a result can be traced to an exact provider/symbol/timeframe/source-version combination and candle-content hash.

No profitability result is used to infer source meaning.
