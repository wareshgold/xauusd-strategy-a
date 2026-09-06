# Phase 32 — SP2L V2 Semantic State Model + Deterministic Fixtures

**Date:** 2026-09-06  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Non-production semantic architecture + fixture suite

## Objective

Convert the Phase 31 source-grounded lifecycle into a deterministic, testable state model without inventing unresolved numeric geometry.

This phase is architectural. Historical XAUUSD performance is not used to choose any semantic definition.

## Implemented

### Non-production semantic state model

`src/domain/research/sp2l-v2/Sp2lSemanticState.ts`

Lifecycle represented explicitly:

```text
CONTEXT
  -> IMPULSE
  -> FOLLOW_THROUGH
  -> SPIKE
  -> CORRECTION
  -> PENDING
  -> FILLED
  -> TP1_REACHED
  -> COMPLETED
```

Explicit rejection/cancellation state:

```text
IMPULSE/FOLLOW_THROUGH -> REJECTED
SPIKE -> REJECTED when structural reference is missing
CORRECTION -> REJECTED when pending order lacks explicit entry/structural stop
PENDING -> INVALIDATED when structural invalidation occurs before fill
```

## Semantic protections

1. Context is required before strong-move classification.
2. Follow-through is an explicit lifecycle state.
3. Follow-through can be rejected for returning into the prior area.
4. First structural reference is explicit and can remain `CANDIDATE`/`TBD`.
5. Correction must begin after the structural reference.
6. Pending order is created during correction, before fill.
7. Entry price must be explicit; no close-reclaim fallback exists in this model.
8. Structural stop must be explicit before a pending order exists.
9. Limit touch only fills at the explicit pending price.
10. Untouched pending orders remain pending until invalidation or fill.
11. Structural invalidation cancels an untouched pending order.
12. Same-candle entry/SL/TP ordering requires an explicit simulator policy.
13. Leg 1 endpoint remains explicitly `TBD` until source-complete.
14. Leg 2 projection origin remains explicitly `TBD` until source-complete.
15. Leg 2 equality tolerance remains unset rather than fitted.
16. Position 2X is permanently disabled in this baseline state model.

## Fixture coverage

`tests/sp2l-v2-semantic-state.test.ts` covers:

- valid bullish lifecycle;
- valid bearish mirror lifecycle;
- context prerequisite;
- follow-through return/rejection;
- structural-reference prerequisite;
- explicit structural stop prerequisite;
- pending-before-fill lifecycle;
- limit-not-touched behavior;
- exact limit touch fill;
- structural invalidation before fill;
- explicit TBD geometry fields;
- separate 2X position boundary;
- explicit same-candle simulator policy;
- preservation of the pending-limit distinction from the old close-reclaim model.

## Important scope boundary

This model is **research-only**. It is not wired into production Strategy A, the canonical baseline backtest, TradingView, live execution, or Telegram publishing.

No historical candle data is consumed by the fixture suite.

## Validation command

```bash
pnpm run test:sp2l-v2
```

The normal project test suite remains available through:

```bash
pnpm test
pnpm run build
```

## Decision

**PHASE 32: COMPLETED — semantic architecture is now deterministic enough to support candidate geometry research.**

The next research step is not optimization of the current baseline. It is source-first candidate geometry work, one unresolved geometry question at a time, using deterministic synthetic fixtures before any historical evaluation.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–30 reports remain immutable historical evidence.
- Phase 31 source excavation remains immutable.
- Production Strategy A remains untouched.
- No EMA50/EMA100 rule is promoted.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result is allowed to decide source meaning.
