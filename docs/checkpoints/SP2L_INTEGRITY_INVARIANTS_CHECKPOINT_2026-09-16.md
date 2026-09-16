# SP2L Integrity Invariants Checkpoint — 2026-09-16

## Completed

Added a research-only integrity layer covering three non-geometry invariants:

1. Research harness objects cannot expose BUY/SELL trading-decision fields.
2. Performance cannot promote geometry whose provenance is not source-confirmed.
3. The 125R observation must retain both its exact `125` R value and `UNTOUCHED` classification.

## Tests added

`tests/sp2l-integrity-invariants.test.ts`

Six deterministic tests cover positive and fail-closed cases.

## Scope boundary

These invariants do not define entry, invalidation, refresh, trigger, 2X, AB=CD, or P-Gap geometry. They do not execute trades and do not generate BUY/SELL decisions.

## Current gate state

Frozen Geometry remains `BLOCKED` at `0/7 SOURCE_CONFIRMED`.

Downstream validation, robustness, fresh holdout, and production remain locked/off.

## Integrity

No source meaning was promoted. No performance result was used to resolve geometry. The 125R observation remains untouched, unmodified, unclipped, and unreclassified.
