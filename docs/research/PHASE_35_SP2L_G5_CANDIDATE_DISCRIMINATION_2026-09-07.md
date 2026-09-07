# Phase 35 — SP2L G5 Candidate Discrimination

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Purpose

Convert the newly strengthened G5 source evidence into a deterministic research fixture without pretending that the exact OHLC C coordinate has already been recovered.

The source establishes the semantic sequence:

```text
PARENT LEG 1
    -> DEEP / INTERVENING CORRECTION
    -> PARENT LEG 2
```

The unresolved question is narrower:

> Which exact source-selected price/candle inside that correction is the executable Leg 2 projection origin?

## Candidate classes

The current candidates are deliberately represented as distinct concepts:

1. **CORRECTION_EXTREME** — the relevant correction high/low.
2. **STRUCTURAL_HL_LH** — a source-selected higher-low/lower-high reference inside the correction.
3. **PENDING_LIMIT** — the price used for the pending order.
4. **ACTUAL_FILL** — the price at which the pending order is touched.
5. **OTHER_VISUAL_POINT** — another chart point explicitly selected by the source.

None is selected as canonical by this phase.

## Fixture rule

Synthetic prices are fixture-only values. They are not source measurements and must never be interpreted as strategy thresholds.

Example semantic fixture:

```text
A = 2500  (Leg 1 structural start; fixture only)
B = 2520  (Leg 1 structural end; fixture only)
correction region begins at index 13
pending entry = 2500
fill = index 15 / 2500

candidate C points may be represented independently:
- correction-region point at index 14
- structural HL/LH point at index 14
- pending-limit concept at index 13
- fill event at index 15
- another source-selected visual point at index 14
```

The important property is **identity separation**, not the chosen numbers.

## Required invariants

### Invariant 1 — correction ordering

A Leg 2 origin cannot precede the beginning of the intervening correction.

### Invariant 2 — origin/fill non-equivalence

A filled order must not silently populate `leg2ProjectionOrigin`.

### Invariant 3 — unresolved C is legal

The semantic model may classify the origin as source-confirmed at the semantic level while keeping its exact price as `null`/TBD.

### Invariant 4 — candidate identity is preserved

If a candidate is recorded, its rationale must state what concept it represents. The engine must not normalize every candidate into `fillPrice`.

### Invariant 5 — no equality fitting

G6 remains separate. No numerical Leg 2 / Leg 1 tolerance is inferred here.

## What this phase resolves

- G5 semantic origin is constrained to the completed/intervening correction of the parent scenario.
- Pending order creation and fill remain execution events, not automatic definitions of C.
- The semantic engine has an explicit representation for an unresolved exact C coordinate.

## What remains unresolved

- exact candle index of C;
- exact OHLC field used for C;
- whether C is the correction extreme, selected HL/LH, pending level, another visual point, or another source-defined point;
- whether the source uses the same C rule for bullish and bearish cases;
- numerical Leg 2 equality tolerance.

## Gate discipline

Do **not** use historical outcomes, DEV/VAL performance, Fresh Holdout, or optimization to choose among these source-semantic candidates.

Do **not** introduce ATR/tick/percentage thresholds to force a candidate to fit.

Fresh Holdout remains LOCKED.

## Next gate

The next legitimate step is source discrimination of the exact visual C point. Until that evidence exists, G5 remains:

```text
SEMANTIC RESOLVED / EXECUTABLE OHLC TBD
```
