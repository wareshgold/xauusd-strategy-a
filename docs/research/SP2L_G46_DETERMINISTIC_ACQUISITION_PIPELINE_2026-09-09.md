# SP2L G46 — Deterministic Acquisition Pipeline

Date: 2026-09-09
Gate: G46
Status: CONTRACT PASS / IMPLEMENTATION READY

## Objective

Move real XAU/USD acquisition from an ad-hoc URL into a reproducible, strategy-neutral request contract.

## Contract

The acquisition request explicitly records:

- symbol;
- interval;
- outputsize;
- optional start/end bounds;
- optional source timezone;
- API credential supplied at runtime only.

The request builder refuses an empty credential and exposes a redacted query for logs. Credentials must never be committed, printed, or embedded in dataset artifacts.

## Twelve Data sample compatibility

The contract supports the previously audited XAU/USD 1min sample and its explicit `Australia/Sydney` timezone provenance.

The existing provider parser remains responsible for converting provider payloads into canonical UTC candles. The dataset artifact layer records fingerprints and provenance independently from Strategy A logic.

## Required runtime sequence

1. Build an `AcquisitionRequest` from explicit configuration.
2. Obtain API key from environment/secret store.
3. Request provider data without logging the key.
4. Preserve the exact raw response locally.
5. Calculate raw fingerprint.
6. Normalize timestamps using explicit source timezone when required.
7. Calculate normalized fingerprint.
8. Run the strategy-neutral quality audit.
9. Write the acquisition manifest/artifact identity.
10. Refuse downstream research use if quality status is BLOCKED.

## Non-goals

This gate does not:

- select a feed based on Strategy A performance;
- resolve P-Gap or any Strategy A geometry;
- generate BUY/SELL signals;
- optimize parameters;
- claim a trading edge.

## Gate decision

G46 is complete as a deterministic acquisition contract. The next permitted implementation step is provider I/O plus a local end-to-end acquisition/audit command, followed by independent feed comparison. Frozen Geometry remains blocked.
