# Phase 31 — SP2L Source Excavation v3

**Date:** 2026-09-06  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Source/codification audit only — no production Strategy A changes

## Purpose

Complete the next source-first pass before writing SP2L V2 code.

The preserved raw source is the semantic authority. The current implementation is evidence of what the machine does, not evidence of what the teacher meant. The existing codification documents and alignment audit were re-read against the raw SP2L source and the separate gap lesson.

## Source assets inspected

- `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
- `docs/strategy/source/POORSAMADI_TIME_ANALYSIS_SOURCE.txt`
- `docs/strategy/STRATEGY_A_POORSAMADI_P0_RULES_V1_2026-09-05.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_GEOMETRY_RESEARCH_V1_2026-09-05.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_GAP_GEOMETRY_RESEARCH_V1_2026-09-05.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_CODIFICATION_SPEC_V2_2026-09-05.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_ALIGNMENT_AUDIT_2026-09-05.md`
- current `SpikeDetector`, `CorrectionDetector`, `EntryTrigger`, and LegProjection implementation

## Confirmed semantic facts

### 1. SP2L is not a close-reclaim entry pattern

The source demonstrates that after the strong-movement/spike sequence begins correcting, the trader can place a pending order before the correction candle completes. The intended lifecycle is therefore:

`SPIKE → CORRECTION BEGINS → PENDING LIMIT → FILL`

not:

`CORRECTION → CLOSE RECLAIM → MARKET ENTRY`.

This is the largest confirmed semantic conflict with the current baseline.

### 2. First structural low/high is a real semantic reference

Bullish examples use the first relevant low as the correction/entry reference; bearish symmetry uses the first relevant high. The exact structural algorithm is still not numerically specified.

### 3. Stop is structural and known before activation

The source treats the entry-to-stop distance as known before the pending order is activated and does not endorse simply widening the stop after adverse movement. Exact price/touch mechanics remain simulator policy/TBD.

### 4. Leg 2 is approximately Leg 1

The central SP2L relationship is preserved:

`abs(Leg2) ≈ abs(Leg1)`

The source describes this as an AB=CD-like candle-level relationship. Exact endpoints, projection origin, and tolerance are not source-complete.

### 5. TP1 is the base single-position target

The source treats TP1 as the practical base target in the demonstrated setup. TP2/Leg3/2X must remain separate modules rather than being silently merged into the baseline.

### 6. 2X is a separate position concept

The source gives a second-position example after progress toward the first target. This must not contaminate the single-position baseline until its complete rule set is codified.

### 7. P-GAP is contextual pressure evidence

The separate gap lesson establishes that P-GAP is not just a geometric candle pattern. Interpretation depends on market location, session/time, trend/cycle context, and whether the movement is pressure/continuation versus exhaustion. Exact P-GAP geometry remains TBD.

The gap lesson therefore strengthens the architecture requirement that context metadata exist before classifying gap evidence.

## What the source still does NOT resolve

The following remain explicitly unknown and must not be fitted from historical performance:

1. Exact first structural low/high algorithm.
2. Exact breakout reference level.
3. Exact FT no-return/overlap predicate.
4. Exact spike grammar and minimum structural sequence.
5. Exact P-GAP OHLC boundaries.
6. Exact pending-limit price if it is not literally the first structural low/high.
7. Exact structural SL price/buffer.
8. Exact Leg 1 endpoints.
9. Exact Leg 2 projection origin.
10. Exact Leg 2 equality tolerance.
11. Exact order-replacement/risk-distance threshold.
12. Exact intrabar/same-candle execution policy.
13. Exact timeframe-specific differences.

## Current implementation conflicts confirmed

### SpikeDetector

Current implementation uses implementation-only parameters such as `maxCandles`, directional body fraction, and overlap fraction and derives the spike window from breakout + FT. It does not prove the preceding range/context or distinguish source-described spike variants. `hasPGAPEvidence` is currently false by construction.

### CorrectionDetector

The correction boundary is tied to `spike.startPrice`. This is only semantically valid if `spike.startPrice` is the first structural low/high, which the current SpikeDetector does not prove.

### EntryTrigger

The current `CORRECTION_EXTREME_RECLAIM` close-entry event is explicitly not canonical under the source-grounded pending-limit model.

### LegProjection

The current Leg 1 endpoint convention is an implementation assumption and must not be optimized into canonical meaning.

### Invalidation / execution

Current close-based invalidation is not automatically equivalent to a price-level structural stop. Entry/SL/TP touch ordering must be a separate deterministic simulator policy.

## V3 semantic contract — safe to use as architecture, not yet as a trading rule

```text
RANGE / CONTEXT
      ↓
BREAKOUT or OTHER SOURCE-DESCRIBED STRONG-MOVE INITIATION
      ↓
IMMEDIATE FOLLOW-THROUGH / KEY-BAR BEHAVIOR
      ↓
SPIKE FAMILY
  ├─ breakout → FT → structure
  ├─ structure → P-GAP
  └─ other source-described strong-move variant
      ↓
FIRST STRUCTURAL LOW/HIGH
      ↓
CORRECTION BEGINS
      ↓
PENDING LIMIT CREATED
      ↓
PRICE TOUCH / FILL
      ↓
FIXED STRUCTURAL INVALIDATION
      ↓
LEG 1 REFERENCE
      ↓
CORRECTION / LEG 2
      ↓
LEG 2 ≈ LEG 1
      ↓
TP1
      ↓
OPTIONAL SEPARATE 2X
```

This is the semantic architecture. It is **not** permission to implement guessed numeric formulas.

## Deterministic fixture plan

Before V2 detector implementation, fixtures must exist for:

- valid bullish structural sequence;
- valid bearish structural sequence;
- breakout + immediate FT;
- FT returning into prior area → reject;
- first structural low/high identified;
- correction begins before fill;
- pending order exists before fill;
- limit touch fills;
- limit not touched → no trade;
- structural invalidation before fill → order cancelled;
- same candle touches entry and SL → explicit simulator policy;
- same candle touches entry and TP → explicit simulator policy;
- Leg 1 endpoint candidate represented explicitly;
- Leg 2 projection origin represented explicitly;
- 2X kept separate from position 1.

Fixtures should be source-shaped and deterministic. They must not be selected because they produce attractive historical results.

## Decision

**PHASE 31 SOURCE EXCAVATION: COMPLETED FOR CURRENT SOURCE MATERIAL.**

The source material is now sufficiently clear to justify a **semantic V2 architecture**, but not sufficiently complete to justify final numeric geometry.

Therefore the next step is:

**build the non-production SP2L V2 semantic state model + fixture suite, with unresolved geometry represented explicitly as TBD/candidate fields.**

Only after that model is internally deterministic and source-consistent should historical candles be used to test candidate geometry.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–30 reports remain immutable historical evidence.
- Production Strategy A remains untouched.
- No EMA50/EMA100 rule is promoted.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result is allowed to decide source meaning.
