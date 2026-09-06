# Phase 31 — SP2L Geometry Resolution Protocol

**Date:** 2026-09-06
**Branch:** `research/phase12-preentry-geometry-robustness`
**Status:** Research protocol only — no production Strategy A changes

## Objective

Stop adding filters to the current baseline and resolve the semantic/geometry mismatch between the current Strategy A implementation and the preserved Poorsamadi source.

The raw source remains authoritative. Current code is implementation evidence, not teacher intent.

## Phase 30 decision carried forward

Directional EMA context was rejected as a promoted rule.

The Phase 30 audit tested EMA50/EMA100 alignment at entry. Neither produced a temporally stable aligned BUY/SELL edge, and the apparent SELL-under-EMA performance was dominated by the same unstable DEV_2 regime seen in earlier phases.

Therefore:

- no EMA50 filter;
- no EMA100 filter;
- no trend-alignment rule;
- no Fresh Holdout unlock;
- no production change.

## Semantic finding

The current baseline is not yet proven to implement canonical SP2L semantics.

The strongest known source-grounded lifecycle is:

```text
RANGE / CONTEXT
  -> BREAKOUT / STRONG MOVE
  -> FOLLOW-THROUGH
  -> SPIKE FAMILY
  -> FIRST STRUCTURAL LOW/HIGH
  -> CORRECTION BEGINS
  -> PENDING LIMIT
  -> FILL
  -> STRUCTURAL SL
  -> LEG 2 ~= LEG 1
  -> TP1
```

This lifecycle is explicitly documented in the current codification specification. The existing close-reclaim entry model is an implementation assumption and must not be treated as canonical.

## P0 geometry questions

### G1 — First structural low/high

Need to resolve:

- exact structural-low/high algorithm;
- single-candle low/high vs pivot;
- minimum structural sequence;
- whether the first structural point must occur after breakout/FT;
- relation to P-GAP.

Source-grounded concept:

```text
Bullish: L1 < L2 < L3 ...
Bearish: H1 > H2 > H3 ...
```

### G2 — Limit-entry price

Need to resolve the exact price level represented by the pending order.

Current research candidate:

```text
BUY  LIMIT ~= first structural low
SELL LIMIT ~= first structural high
```

But this remains a research candidate until source examples prove the exact relation.

### G3 — Structural stop

Need to resolve whether the stop is:

- exactly beyond first structural low/high;
- beyond another structural point;
- buffered by a source-defined amount;
- or otherwise defined.

Do not optimize a buffer from historical data at this stage.

### G4 — Leg 1 endpoints

Current code uses `first.open -> last.close`, but this is not source-proven.

Candidate semantic models to document and compare against source examples:

1. first structural low/high -> spike extreme;
2. breakout level -> spike extreme;
3. spike start -> spike end;
4. first relevant candle open -> spike extreme;
5. structural point -> structural point.

These are candidate interpretations only. Historical performance must not choose the endpoint formula before source review.

### G5 — Leg 2 projection origin

Need to resolve whether Leg 2 begins from:

- correction extreme;
- actual limit-entry/fill;
- first structural low/high;
- another A/B/C/D structural point.

Current code projection from correction extreme is not canonical by default.

### G6 — Leg 2 equality

Semantic relationship is established:

```text
abs(Leg2) ~= abs(Leg1)
```

Exact tolerance remains TBD.

No arbitrary ±10%, ±20%, etc. is permitted without source support or an explicitly frozen research hypothesis.

### G7 — Execution semantics

Need a frozen deterministic policy for:

- limit touch/fill;
- stop touch;
- TP touch;
- same-candle entry + SL/TP ambiguity;
- spread/slippage;
- whether the correction candle can create and fill the order.

These are simulator policies and must remain separate from source semantics.

## P1 geometry/context questions

After P0:

- exact P-GAP geometry;
- exact range definition;
- exact breakout level algorithm;
- exact FT no-return/non-overlap rule;
- order-replacement/risk-distance threshold;
- timeframe-specific differences.

The latest gap lesson already establishes that P-GAP is contextual pressure evidence, not merely candle geometry, and that session/location/trend-cycle context affect gap interpretation. Exact P-GAP geometry remains TBD.

## Research method

This phase is **source-first**, not performance-first.

For every unresolved geometry item:

1. identify source timestamp/example;
2. write faithful semantic statement;
3. separate semantic fact from implementation assumption;
4. define deterministic candidate only where necessary;
5. build positive/negative chart fixtures;
6. test the candidate against source examples;
7. only after semantic acceptance, run chronological DEV/VAL research;
8. only after DEV/VAL survives, consider Fresh Holdout.

Historical performance must never be used to decide which semantic interpretation is “what the teacher meant.”

## Protected research boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–30 historical reports remain immutable evidence.
- Current Strategy A production implementation remains unchanged.
- No EMA rule is promoted.
- No threshold mining.
- No optimization against VAL/Fresh.
- No rewriting historical conclusions.

## Current conclusion

The highest-value next work is **not another filter**.

It is to resolve the actual SP2L geometry, especially:

```text
first structural low/high
        ↓
pending limit price
        ↓
structural SL
        ↓
Leg 1 endpoints
        ↓
Leg 2 projection origin
        ↓
execution semantics
```

Only after this chain is semantically frozen should a new SP2L V2 detector be implemented and compared with the existing baseline.
