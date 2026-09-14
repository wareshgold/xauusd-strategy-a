# G406 — Source-Critical Resolution Consolidation

## Purpose

G406 consolidates the source-critical executable-geometry blockers identified by G400 and the five dedicated source-resolution gates G401–G405.

This is a **readiness/consolidation gate**, not a geometry-freeze gate and not a source-evidence result.

## Current state

G401–G405 each remain `UNRESOLVED` by design:

- G401 — P-Gap executable OHLC geometry/formula
- G402 — A/B/C anchors, wick/body semantics, and D construction
- G403 — pending-limit price, activation, persistence, fill, and pre-fill invalidation
- G404 — structural invalidation boundary and executable stop price
- G405 — TP1/TP2 target mapping to executable prices

G400 therefore remains `BLOCKED` across the seven source-critical dimensions, including AB=CD tolerance as a separate unresolved dimension.

## Seven source-critical dimensions

1. `UNRES-PGAP-GEOMETRY`
2. `UNRES-ABCD-ANCHORS`
3. `UNRES-ABCD-TOLERANCE`
4. `UNRES-ENTRY-PRICE`
5. `UNRES-ENTRY-TIMING`
6. `UNRES-STOP-BOUNDARY`
7. `UNRES-TARGET-MAPPING`

## Non-promotion rule

G406 does not promote any candidate formula, anchor, threshold, tolerance, entry price, stop boundary, or target mapping.

Backtest performance, implementation convenience, generic price-action conventions, or synthetic hypothesis results cannot clear these source blockers.

## Required next evidence

The next productive step is source-evidence acquisition/review targeted specifically at the seven unresolved dimensions, using the authoritative transcript/source artifact and source visual frames. Where evidence cannot discriminate a dimension, the dimension remains unresolved.

## Gate decision

**G406 = BLOCKED**

Executable geometry is not frozen. Historical optimization and production signal generation remain unauthorized until the source-critical dimensions are actually resolved and the downstream freeze/validation gates are satisfied.
