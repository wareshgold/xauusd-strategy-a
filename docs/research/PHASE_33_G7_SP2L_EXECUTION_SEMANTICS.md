# PHASE 33 — SP2L G7 Execution Semantics

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Scope:** research-only; no production Strategy A changes

## Objective

Freeze only the execution semantics that follow from the already established SP2L lifecycle, while keeping simulator assumptions explicitly separate from teacher semantics.

## Source-established lifecycle

```text
CORRECTION
  -> PENDING LIMIT EXISTS
  -> PRICE TOUCH / FILL
  -> PREDEFINED STRUCTURAL INVALIDATION
  -> LEG 2
  -> TP1
```

The source-backed architecture requires the pending order to exist before activation; a close-reclaim market entry is not the canonical SP2L lifecycle.

## Deterministic simulator policies

These are research/simulator policies, not claims about additional teacher rules:

1. **Pending limit creation:** once the structural entry candidate is available during correction, create the pending order before fill.
2. **Limit fill:** a pending order is filled only when the historical candle range reaches/touches the explicit pending price. Fill price equals the explicit pending price; no invented slippage is applied at this semantic stage.
3. **Pre-fill invalidation:** if the predefined structural invalidation is reached before fill, cancel the pending order and reject the setup.
4. **Post-fill stop:** after fill, the structural stop remains fixed; it is not widened by later adverse movement.
5. **TP1:** TP1 is evaluated after fill and remains the base single-position target.
6. **Same-candle entry + stop/TP:** this remains an explicit simulator ambiguity. OHLC data alone does not reveal intrabar ordering when both levels are touched in the same candle. No optimistic ordering is allowed.
7. **Spread/slippage:** excluded from semantic research fixtures until the geometry and fill model are frozen; introducing them earlier would mix execution-cost assumptions with teacher semantics.
8. **Order creation/fill on same candle:** permitted only when the deterministic state transition can establish that the pending order existed before the touch event under the chosen candle-event model. Otherwise mark the case ambiguous rather than inventing ordering.

## Hard boundary

No G7 policy may be used to repair unresolved G4/G5 geometry. Execution semantics begin only after the source geometry is frozen.

## Status

- Pending-limit-before-fill: SOURCE-ESTABLISHED.
- Structural invalidation before fill: SOURCE-ESTABLISHED concept.
- Fixed structural stop after fill: SOURCE-ESTABLISHED concept.
- TP1 as base target: SOURCE-ESTABLISHED.
- Intrabar/same-candle ordering: RESEARCH POLICY / TBD where OHLC cannot determine order.
- Spread/slippage: RESEARCH POLICY, not teacher semantics.

## Gate

A canonical live/backtest implementation must not be promoted until G4/G5 visual geometry is resolved and G6 equality handling is explicitly frozen.
