# Phase 36 — SP2L G5 Candidate Identity

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Objective

Strengthen G5 so candidate concepts cannot be silently collapsed into the pending-limit fill price or into a generic correction extreme.

## Source boundary

The preserved Pour Samadi evidence establishes:

```text
PARENT LEG 1
    -> DEEP / INTERVENING CORRECTION
    -> PARENT LEG 2
```

It does **not** yet establish the exact OHLC coordinate of the Leg 2 projection origin.

Therefore the research engine must preserve the semantic concept and the unresolved price independently.

## Candidate taxonomy

The semantic model now represents the unresolved origin concept explicitly as one of:

- `CORRECTION_EXTREME`
- `STRUCTURAL_HL_LH`
- `PENDING_LIMIT`
- `ACTUAL_FILL`
- `OTHER_VISUAL_POINT`

This is a taxonomy of hypotheses/evidence classes, **not a canonical selection**.

## Invariants added

1. A candidate may carry an explicit concept without carrying an exact price.
2. `ACTUAL_FILL` is not automatically assigned when `LIMIT_TOUCHED` occurs.
3. A pending-limit price is not automatically treated as the Leg 2 origin.
4. A correction-origin semantic classification may be source-confirmed while its exact OHLC coordinate remains null/TBD.
5. A candidate cannot precede the beginning of the intervening correction.
6. G6 equality tolerance remains completely independent.

## Why this matters

The source language is visual/structural: the teacher identifies the deep leg and chart points visually. The transcript does not provide a universal candle-field formula for C.

A deterministic system must therefore fail closed rather than silently choosing:

```text
C = fillPrice
```

or:

```text
C = correction.low/high
```

without source evidence.

## Current G5 state

```text
semantic origin: SOURCE-CONFIRMED
exact OHLC coordinate: TBD
candidate identity: explicit
canonical candidate: NOT SELECTED
```

## Next step

Continue source discrimination using any already-preserved source evidence that can distinguish the visually selected C point from the correction extreme, HL/LH reference, pending-limit level, or fill event.

If the available source text cannot distinguish them, G5 remains executable-geometry TBD. Do not use DEV/VAL/Fresh performance to force a selection.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–30 historical evidence remains immutable.
- Production Strategy A remains unchanged.
- No P-GAP threshold is introduced.
- No Leg 2 equality tolerance is fitted.
- 2X remains separate.
