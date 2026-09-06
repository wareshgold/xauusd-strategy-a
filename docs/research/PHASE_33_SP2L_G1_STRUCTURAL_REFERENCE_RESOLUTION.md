# Phase 33 — SP2L G1 Structural Reference Resolution

**Date:** 2026-09-06  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Candidate geometry resolution — research only

## Objective

Resolve the first unresolved SP2L geometry question from Phase 31:

> What price reference does the corrective move have to reach before the second-leg entry becomes valid?

This phase resolves only G1. It does not define the final spike detector, entry model, stop buffer, Leg 1, Leg 2 projection, equality tolerance, or historical trading rule.

## Source evidence

The public SP2L description states that after the spike, the corrective candle should reach:

- the **low of the previous candle** in a bullish setup;
- the **high of the previous candle** in a bearish setup.

The same source describes the SL as being behind the candle from which the spike originated. This supports a candle-structure reference, but it does **not** prove that the project should identify a generic multi-candle swing/pivot called “the first structural low/high”.

Therefore we must not silently equate “previous candle low/high” with a generic swing algorithm.

## G1 candidate

For the current source-shaped research model:

```text
Bullish correction reference = LOW of the candle immediately preceding the corrective candle.
Bearish correction reference = HIGH of the candle immediately preceding the corrective candle.
```

The candidate implementation is:

`src/domain/research/sp2l-v2/StructuralReferenceCandidate.ts`

It intentionally returns `status: CANDIDATE`.

### Why candidate, not source-confirmed?

The source statement establishes the relationship between the correction candle and the previous candle. It does not fully establish:

1. which candle is the canonical “previous candle” when the correction spans multiple candles;
2. whether the reference is created on the first correction candle only;
3. whether an earlier structural point can replace it;
4. whether the reference is identical to the spike-origin candle in every valid setup;
5. whether the P-GAP/context changes the reference selection.

Those questions remain open and must not be answered from historical performance.

## Deterministic fixture contract

The candidate fixture suite requires:

- bullish → previous candle low;
- bearish → previous candle high;
- non-finite candle geometry → reject;
- no fallback to close price;
- no generic pivot search;
- no historical threshold.

These fixtures are deliberately synthetic and contain no XAUUSD historical data.

## Decision

**G1 candidate accepted for further source review, not promoted to `SOURCE_CONFIRMED`.**

This is enough to proceed to G2 only as a dependent candidate, while preserving the distinction between:

```text
SOURCE FACT
previous candle low/high

vs.

IMPLEMENTATION CANDIDATE
previous-candle structural reference resolver
```

## Next step

G2 — resolve the exact pending-limit entry price.

The next question is whether the pending limit is exactly this G1 reference, the spike-origin level, or another source-defined level. No historical backtest should be used to choose between those interpretations.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–32 reports remain immutable historical/architectural evidence.
- Production Strategy A remains untouched.
- No EMA50/EMA100 rule is promoted.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result decides source meaning.
