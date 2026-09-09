# SP2L G41 — Strategy-Neutral Market Data Adapter Contract

Date: 2026-09-09

## Purpose

Prepare reproducible XAUUSD market-data ingestion without implementing or selecting unresolved Strategy A geometry.

## Canonical raw record

Every raw bar must contain:

- symbol
- timeframe
- timestamp
- open
- high
- low
- close

Timestamps are normalized to UTC at the ingestion boundary. The original provider timestamp/timezone metadata must remain in provenance.

## Integrity requirements

A dataset is usable only when deterministic checks pass:

1. timestamps are parseable and UTC-normalizable;
2. rows are chronologically ordered;
3. duplicate timestamps are detected and resolved only by an explicit provider rule, never silently;
4. OHLC satisfies `high >= max(open, close)` and `low <= min(open, close)`;
5. `high >= low`;
6. gaps/missing bars are measured and reported rather than silently fabricated;
7. symbol and timeframe are consistent with the manifest;
8. the exact dataset bytes/content used for research can be fingerprinted.

## Provenance

The manifest must capture provider, symbol, timeframe, UTC start/end, row count, source/version identifier, retrieval metadata where available, and SHA-256 fingerprint. Any transformation must produce a new deterministic artifact with a traceable parent dataset.

## Aggregation

M1 is the preferred raw research granularity when available. Fixed-timeframe bars such as M5 may be derived deterministically from UTC-aligned M1 buckets. Aggregation must define:

- bucket boundary convention;
- open = first source open;
- high = maximum source high;
- low = minimum source low;
- close = last source close;
- handling of incomplete buckets;
- handling/reporting of missing source bars.

No timezone/session filter is implied by this contract.

## Quality states

Use explicit states rather than silently proceeding:

- `PASS` — all required integrity checks pass;
- `WARN` — usable but with documented non-fatal quality observations;
- `BLOCKED` — deterministic research use is unsafe until corrected or explicitly reviewed.

## Provider neutrality

A provider adapter may map provider-specific fields into the canonical record, but must not alter price values, infer missing bars, or apply Strategy A interpretation. Feed differences between providers are research data, not reasons to silently normalize one feed into another.

## Boundary

This contract supports the DEV/data-readiness infrastructure only. It does not freeze P-Gap, Entry, SL, Trigger, AB=CD, Leg2/TP, session filters, or any other Strategy A geometry.

## Gate

G41 is complete only when adapter contract tests cover UTC normalization, OHLC validity, duplicate/missing-bar detection, deterministic aggregation, manifest linkage, and explicit quality-state behavior.
