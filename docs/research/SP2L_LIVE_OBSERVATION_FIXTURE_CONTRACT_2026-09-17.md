# SP2L Live Observation Fixture Contract — 2026-09-17

## Purpose

Freeze the research-only data-observation contract as deterministic synthetic fixtures before any MT5 live adapter implementation.

This document tests transport/observation behavior only. It does not define Strategy A geometry, signal rules, execution semantics, or production BUY/SELL authorization.

## Fixture model

Each synthetic provider observation contains:

- provider/server identity;
- symbol identity;
- timeframe;
- UTC timestamp for the bar open;
- OHLC values;
- completion state;
- optional monotonic provider sequence;
- stable provider bar identity;
- source metadata.

The fixture harness must preserve the supplied price and identity fields exactly.

## Deterministic scenarios

### F1 — Single completed bar

Input: one completed M1 bar.

Expected:

- exactly one observation event;
- event is research-only;
- bar identity is preserved;
- no SP2L signal is inferred.

### F2 — Duplicate completed bar

Input: the same provider bar identity delivered twice.

Expected:

- exactly one effective observation;
- second delivery is idempotently ignored or recorded as a duplicate diagnostic;
- no second research event for the same bar identity.

### F3 — Out-of-order delivery

Input: completed bars delivered in non-chronological order.

Expected:

- deterministic ordering/handling according to the adapter contract;
- no mutation of supplied timestamps;
- no invented or rewritten candle data;
- repeated execution of the same fixture produces the same event sequence.

### F4 — Timestamp normalization

Input: equivalent provider timestamps represented with an explicit timezone offset.

Expected:

- normalized UTC timestamp is deterministic;
- the underlying instant is unchanged;
- equivalent instants resolve to the same normalized identity.

### F5 — Missing bar

Input: completed bars with a gap in the expected M1 sequence.

Expected:

- a data-quality event is emitted;
- the missing candle is not fabricated;
- subsequent real bars retain their original OHLC and timestamps.

### F6 — In-progress bar

Input: a bar marked incomplete/current.

Expected:

- no confirmed research observation is emitted for that bar;
- no signal is inferred from the incomplete bar;
- later completed delivery of the same bar may be processed as a new completed state only under an explicitly deterministic identity/state rule.

### F7 — Research notification boundary

Input: a valid research observation event passed to a future notification adapter.

Expected:

- notification preserves research/observation classification;
- notification transport does not calculate SP2L geometry;
- notification transport does not alter direction or create a trade signal;
- output cannot be represented as production authorization.

### F8 — Production execution boundary

Input: any research observation, diagnostic, or data-quality event.

Expected:

- no direct path to production order execution;
- no production BUY/SELL event is generated;
- unresolved strategy semantics remain untouched.

## Required invariants

1. Same fixture input produces the same normalized output.
2. Duplicate provider bar identity is idempotent.
3. No candle is fabricated to repair a data gap.
4. Closed-bar confirmation is required for research observation.
5. Provider/server/symbol/timeframe identity is retained.
6. UTC normalization preserves the instant represented by the provider timestamp.
7. Research transport cannot promote an event to production authorization.
8. Fixture behavior must not depend on SP2L P-Gap, AB=CD, entry, SL, TP, Round Level, or lifecycle rules.

## Promotion boundary

Passing these fixtures would establish only a deterministic observation/transport boundary. It would not establish Frozen Geometry, Strategy A validity, statistical edge, or production readiness.

The next implementation step is to encode these scenarios in tests using repository-native test tooling, without connecting to a live MT5 terminal and without changing canonical SP2L geometry.
