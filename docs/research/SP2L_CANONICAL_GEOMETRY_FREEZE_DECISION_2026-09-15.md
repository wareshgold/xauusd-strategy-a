# SP2L Canonical Geometry Freeze Decision — 2026-09-15

## Status

`GOVERNANCE_CONTRACT_ONLY`

This document defines the separate decision gate that may follow `READY_FOR_FREEZE_REVIEW`. It does not adjudicate source meaning and does not freeze any geometry by itself.

## Required sequence

`C01–C08 human adjudication (#175)` → `Frozen Geometry Readiness (#179)` → `Separate Freeze Decision (#180)` → `deterministic development`.

## Preconditions

Canonical Strategy A geometry may be frozen only if all ten executable dimensions have valid human `SOURCE_DISCRIMINATED` records and the readiness gate reports `READY_FOR_FREEZE_REVIEW`.

Required safeguards:

- complete Tier-1/Tier-2 provenance for every canonical field;
- reproducible source discriminator;
- no invented formula, threshold, buffer, candle indexing, fill/execution semantics, or inferred symmetry;
- no unresolved dimension hidden by a partial freeze;
- no backtest or optimization used to resolve source ambiguity.

## Freeze decision record

A future decision record must explicitly enumerate:

1. canonical field/dimension;
2. exact source evidence reference;
3. human adjudication record ID;
4. reproducibility confirmation;
5. source-backed rule text, without implementation embellishment;
6. remaining unresolved hypotheses, if any;
7. explicit decision: `FREEZE` or `BLOCK`.

A `FREEZE` decision is valid only when all ten dimensions are source-discriminated and reproducible. If any dimension is blocked, the entire freeze decision remains `BLOCKED`.

## Hard boundary

`READY_FOR_FREEZE_REVIEW` is not equivalent to canonical freeze. This gate also does not authorize execution, BUY/SELL generation, backtesting-based promotion, or production deployment.

## Post-freeze engineering gate

Only after an explicit canonical freeze decision may deterministic Strategy A implementation consume the frozen geometry. Implementation must remain traceable to the frozen source-backed rule package and must not add undocumented behavior.
