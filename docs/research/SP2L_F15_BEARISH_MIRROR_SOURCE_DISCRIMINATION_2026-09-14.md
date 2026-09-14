# SP2L F15 — Bearish Mirror Source-Discrimination Fixture

Date: 2026-09-14  
Status: BLOCKED  
Canonical status: NOT CANONICAL

## Purpose

F15 tests whether the bullish source semantics can be mirrored into a deterministic bearish Strategy A implementation, or whether the source requires an independently evidenced bearish construction.

This is a synthetic source-discrimination fixture, not historical evidence, optimization data, or a production rule. Source meaning outranks backtest performance.

## Synthetic construction

Create a bearish counterpart to the demonstrated bullish SP2L sequence while preserving only semantic concepts already supported by source evidence:

1. context/range;
2. directional Spike;
3. breakout/follow-through and source-relevant P-Gap semantics;
4. structural correction;
5. pending-Limit entry;
6. structural invalidation distinct from Entry;
7. second-leg continuation and approximate Leg-2/Leg-1 magnitude relationship.

The fixture must not assume that every bullish OHLC anchor, trigger condition, refresh behavior, or target formula automatically inverts.

## Competing interpretations

### Candidate A — exact geometric mirror

Every bullish semantic and executable geometry is reflected by price-direction inversion.

### Candidate B — semantic mirror only

High-level concepts mirror, but exact OHLC anchors, trigger classifier, pending-order refresh, invalidation, and target geometry require separate bearish evidence.

### Candidate C — asymmetric bearish construction

The source may define materially different bearish geometry that cannot be inferred from bullish inversion.

### Candidate D — no bearish canonicalization

Until direct bearish evidence exists, bearish executable geometry remains unresolved.

## Source-discrimination questions

1. Does the source directly demonstrate bearish SP2L examples?
2. If so, does it explicitly use the same structural sequence in reverse?
3. Are Entry and invalidation anchored to mirrored structural points?
4. Are trigger, refresh, P-Gap, AB=CD, and 2X/TP1 semantics explicitly mirrored?
5. Does the source establish any bearish-specific exception?

## Adjudication

Current evidence is insufficient to establish a complete, deterministic bearish executable mirror across all unresolved dimensions.

Therefore F15 remains:

`BLOCKED`

A bearish implementation must not be created merely by sign-flipping a bullish hypothesis. Semantic symmetry may be a research hypothesis, but it is not canonical without sufficient source evidence.

## Negative controls

Do not invent:

- automatic bullish-to-bearish sign inversion;
- mirrored wick/body assumptions;
- mirrored P-Gap OHLC formula;
- mirrored AB=CD anchors/tolerance;
- mirrored pending-order replacement threshold;
- mirrored 2X/TP1 formula;
- bearish rules selected by backtest performance.

## Gate impact

- SOURCE RESOLUTION: incomplete for bearish executable geometry.
- SYNTHETIC FIXTURES: F15 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for bearish Strategy A geometry.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

Documentation only. No engine, simulator, replay, or production changes. No backtest/optimization selection. Manual approval by Ali remains required for any future CANONICAL promotion.
