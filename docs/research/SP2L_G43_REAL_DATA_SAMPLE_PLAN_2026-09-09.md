# SP2L G43 — Real XAUUSD M1 Sample Plan

Date: 2026-09-09

## Gate

Real-data acquisition validation, strategy-neutral.

## Objective

Validate the G42 acquisition contract against a small real XAU/USD M1 response before requesting the full DEV historical window.

## Provider status

Twelve Data is a provider candidate only. This gate does not establish it as canonical and does not compare providers using Strategy A performance.

## Required sample artifact

The acquisition run must preserve:

- exact request parameters;
- retrieval timestamp in UTC;
- provider response metadata;
- raw payload or byte-for-byte canonical serialization;
- normalized candle representation;
- acquisition manifest;
- raw SHA-256 and normalized SHA-256.

Secrets must remain outside the repository.

## Quality audit

The sample is accepted for infrastructure testing only when:

1. requested symbol and interval match;
2. source timezone is explicit;
3. timestamps normalize deterministically to UTC;
4. timestamps are monotonic after normalization;
5. duplicate timestamps are reported;
6. cadence is measured rather than assumed;
7. missing bars are reported rather than fabricated;
8. OHLC invariants hold for every accepted row;
9. requested versus actual coverage is recorded;
10. the manifest fingerprints reproduce exactly.

Any failed invariant is a BLOCKED quality result, not a reason to repair the source silently.

## Coverage limitation

A small sample is not evidence of complete historical availability. Actual first/last timestamps and row count from the response are the only accepted coverage evidence for this gate.

## No Strategy A usage

The sample must not be passed to a Strategy A detector, optimized geometry candidate, or profitability test. This gate validates the data path only.

## Next decision

PASS: scale the same immutable acquisition process to the DEV historical window.

BLOCKED: correct the acquisition/data contract without changing Strategy A semantics, then repeat the sample audit.
