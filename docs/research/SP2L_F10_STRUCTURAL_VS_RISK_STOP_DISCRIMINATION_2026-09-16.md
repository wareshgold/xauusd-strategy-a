# SP2L F10 — Structural Invalidation vs Risk-Budget Stop

## Purpose

Formalize the current F10 research boundary exposed by the 125R forensic reconstruction.

F10 is a source-discrimination fixture, not a canonical rule definition.

## Competing interpretations kept explicit

For a correction/invalidation region, the research fixture must keep distinct:

1. Wick extreme
2. Body extreme
3. Base/original swing
4. Relevant/latest opposite swing
5. Risk-budget stop derived separately from structural invalidation

The fixture must not select among these interpretations using profitability, backtest performance, or parameter optimization.

## Current evidence

The 2026-08-20 20:54:00 persisted SELL observation reconstructs to:

- Entry: `4521.5838`
- current implementation invalidation: `4521.61331`
- risk distance: approximately `0.02951`

The current implementation can reproduce these values, but this does not establish that the source requires the same OHLC anchor or wick/body semantics.

## Acceptance boundary

F10 may become `SOURCE_DISCRIMINATED` only when source evidence uniquely identifies the relevant structural anchor and distinguishes it from risk-budget stop calculation.

If source evidence permits multiple interpretations, status remains `UNRESOLVED`.

## Prohibited promotions

Until source discrimination exists, do not introduce any of the following merely to suppress extreme-R observations:

- minimum stop-distance filter
- stop buffer/offset
- wick-to-body substitution
- alternate swing selection
- spread adjustment
- replacement Entry anchor
- risk-budget stop as a substitute for structural invalidation

## Gate status

- F10: `UNRESOLVED`
- Source Resolution: `PARTIAL PASS`
- Frozen Geometry: `BLOCKED`
- Untouched Validation: `LOCKED`
- Robustness/Stability: `LOCKED`
- Fresh Holdout: `LOCKED`
- Production: `OFF`
