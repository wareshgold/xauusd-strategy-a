# PHASE 33 — SP2L G6 Leg2 Equality Semantics

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Scope:** research-only; no production Strategy A changes

## Objective

Resolve what is source-established about the relationship between Leg 2 and Leg 1, without inventing a numerical tolerance.

## Source-grounded result

The preserved Poorsamadi SP2L material establishes the conceptual relationship that the second directional leg completes at approximately the size of the first directional leg. The relationship is therefore represented semantically as:

```text
abs(Leg2) ~= abs(Leg1)
```

The source examples also distinguish the directional legs from the correction between them. This is not a statement that Leg2 must equal Leg1 tick-for-tick.

## What is NOT source-resolved

The preserved text does not provide a universal numerical equality band that can safely be encoded as a Poorsamadi rule. In particular, no ±5%, ±10%, ±20%, ATR multiple, tick count, point count, or fixed price-distance tolerance is promoted here.

Historical performance must not be used to decide which tolerance Poorsamadi meant.

## Deterministic research representation

Until visual/source evidence resolves a tolerance, G6 is represented as a semantic predicate with an explicit unresolved tolerance:

```text
leg2Magnitude = abs(leg2End - leg2Origin)
leg1Magnitude = abs(leg1End - leg1Origin)

G6 = EQUALITY_TOLERANCE_TBD
```

A fixture may therefore verify the measured magnitudes and preserve the comparison as `TBD`, but must not label a trade valid/invalid using an invented percentage.

## Required order of work

1. Resolve G4 A/B and G5 C from visual source evidence.
2. Freeze the geometry representation.
3. Inspect all source examples for any explicit numerical equality criterion.
4. If no universal numeric criterion exists, keep G6 as a source-semantic concept and define a separate, documented simulator/research tolerance policy rather than attributing it to the teacher.
5. Build positive/negative synthetic fixtures around the chosen research policy only after the source semantics are frozen.
6. Then proceed to G7 execution semantics.

## Decision

**G6 semantic core: SOURCE-ESTABLISHED.**  
**Universal numerical tolerance: TBD.**

No backtest optimization was performed and no production code was changed.
