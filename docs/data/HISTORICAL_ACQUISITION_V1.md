# Historical Acquisition v1

## Status

**IMPLEMENTED — NOT YET EXECUTED AS FULL-RANGE ACQUISITION**

The preceding Twelve Data pilot and coverage sampling passed bounded tests. The
next data gate is a resumable historical acquisition process for raw XAU/USD M1.

## Evidence already established

- Bounded 24-hour acquisition completed with 1,441 rows, zero reported gaps and zero invalid OHLC rows.
- Five historical sampling windows (2020, 2022, 2024, 2025, 2026) returned successfully with zero sampled gaps and zero invalid OHLC rows.
- These tests do **not** prove continuous coverage across the entire historical interval.

## Acquisition contract

The v1 downloader uses:

- provider: Twelve Data
- instrument: `XAU/USD`
- interval: `1min`
- timezone: `UTC`
- maximum provider page size: 5,000 rows
- API key source: `TWELVE_DATA_API_KEY` environment variable only
- no API key persistence
- exact timestamp de-duplication
- OHLC validation
- 60-second continuity validation
- checkpoint after each successful page
- final CSV + JSON manifest only after exact requested boundaries are covered

The downloader deliberately does not interpret gaps as market closures. A later
session/calendar layer must establish whether any discontinuity is expected from
the provider feed.

## Resume semantics

A checkpoint contains the requested range, next backward cursor, accumulated raw
rows, request provenance, and update timestamp. If a run stops because of the
request budget or a transient provider failure, the checkpoint remains and the
same requested range can be resumed.

Completed CSV/manifest artifacts are not overwritten unless `--force` is used.

## Important limitation

The project must not infer complete 2020-present M1 coverage from the sampling
probe. Full-range acquisition is an empirical dataset operation. Its result must
be recorded with a manifest, request log, row count, continuity diagnostics, and
SHA-256 hash.

## Research boundary

This layer is **raw market-data acquisition only**. It does not:

- resample M1 into M5;
- detect ranges, breakouts, spikes, P-Gaps, entries, stops or targets;
- optimize parameters;
- generate signals;
- determine Strategy A meaning from profitability.

The resulting dataset may enter strategy research only after its acquisition
manifest and integrity checks are accepted.

## Next gate

Run a bounded multi-day acquisition first to validate checkpoint/resume behaviour
before committing to a large historical extraction. Then perform the full planned
range in controlled daily credit budgets.
