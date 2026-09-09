# SP2L G44 — Real XAUUSD Sample Acquisition

Date: 2026-09-09
Branch: `research/sp2l-real-sample-g44-2026-09-09`

## Status

**EXECUTION-READY / REAL-SAMPLE-PENDING**

The repository now contains a one-shot acquisition harness. It requires the runtime environment variable `TWELVE_DATA_API_KEY`; no credential is stored in source control.

## Execution contract

The harness requests `XAU/USD`, `1min`, explicit UTC bounds and explicit UTC timezone. It preserves the raw response, computes a raw SHA-256, parses through the existing Twelve Data-shaped provider adapter, normalizes candles deterministically, computes a normalized SHA-256, runs the strategy-neutral quality audit, and writes a canonical manifest.

## Artifact set

A successful run produces:

- `raw_response.json`
- `raw_sha256.txt`
- `normalized.json`
- `normalized_sha256.txt`
- `manifest.json`

The artifact directory is an external research artifact and must not contain API credentials.

## PASS criteria

- non-empty response;
- provider metadata matches `XAU/USD` and `1min`;
- explicit source timezone;
- deterministic UTC timestamps;
- zero duplicate timestamps;
- monotonic timestamps;
- valid OHLC invariants;
- cadence anomalies explicitly reported;
- requested and actual coverage recorded;
- raw and normalized fingerprints reproducible.

A cadence gap is reported rather than repaired. An OHLC or timestamp invariant failure blocks the quality result.

## Important limitation

This document does **not** claim that a real sample has been successfully acquired. That claim requires execution in a runtime with a valid provider credential and preservation of the resulting immutable artifacts.

## Strategy boundary

No Strategy A detector, P-Gap interpretation, Entry/SL geometry, AB=CD anchor, Leg2 projection, session filter, or BUY/SELL decision is executed by G44.

## Next gate

If the real sample passes, scale the same acquisition contract to the chronological DEV historical window. If it fails, resolve the data-path defect first; do not alter Strategy A semantics to accommodate the feed.
