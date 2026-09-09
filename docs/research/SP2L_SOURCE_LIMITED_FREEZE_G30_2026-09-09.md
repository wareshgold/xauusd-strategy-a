# SP2L Source-Limited Freeze — G30 — 2026-09-09

## Purpose

Freeze the maximum executable meaning that is justified by the primary SP2L source without inventing unresolved OHLC geometry. This document is a controlled boundary, not a production strategy specification.

## Primary evidence basis

Primary source: SP2L video, recovered transcript and direct source-frame review.

Key source regions:

- 31:43–32:21: P-Gap is explicitly associated with breakout and distinguished from E-Gap/Common-Gap.
- 34:25–35:50: multiple P-Gap constructions are shown; breakout-first and higher-lows-first variants are treated as the same concept for the current strategy.
- 36:15–37:57: SP2L is explicitly framed as Spike → 2 Leg; AB=CD links the second leg magnitude to the first leg magnitude.
- 38:18–39:26: higher-lows sequence, correction, pending Limit placement, and structural invalidation are explicitly described.
- 39:48–40:16: pending order may be deleted/replaced when the structural/risk distance changes materially; no numeric threshold is supplied.
- 40:42–41:37: entry confirmation/trigger examples and 2X are discussed.
- 42:26–42:48: TP1/TP2 are discussed; TP1 is the teacher's usual choice and TP2 is presented as something to backtest.
- 53:16–54:29: one-, two-, and three-candle trigger examples; pullback to the beginning of Leg 2; reduced-risk treatment for lower-probability cases; renewed Buy Limit opportunity.
- 55:02–57:34: clean bullish/bearish examples with structural SL, Entry, Leg 2 and Buy/Sell Limit annotations.
- 58:04–58:32: bearish trigger/stop example and explicit warning to include losing examples rather than confirmation bias.
- 1:02:31–1:04:32: deeper discussion of first/second leg decomposition and another Sell Limit / structural sequence.

## Decision rule

A geometry is frozen only if the primary source uniquely supports the coordinate/indexing rule. If two or more interpretations remain source-consistent, the item remains unresolved. Backtest performance cannot select among source interpretations.

## G1 — P-Gap

### Frozen meaning
P-Gap is a source-specific pressure-gap concept associated with a valid breakout/follow-through sequence. The source explicitly describes a construction in which adjacent candle ranges do not overlap and also shows variants where the gap appears after the initial breakout.

### Not frozen
- universal candle indices;
- exact OHLC inequality/equality;
- whether the relevant boundary is wick, body, or another source-defined coordinate;
- minimum gap size;
- tolerance;
- generic three-candle FVG substitution.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G2 — Entry anchor

### Frozen meaning
The execution mechanism is a pending Limit order during correction. The demonstrated order is associated with the relevant structural Low/High created by the directional sequence.

### Not frozen
- exact wick/body/pivot anchor;
- whether the line uses the latest structural pivot in every construction;
- candle indexing;
- any price buffer;
- universal equivalence to Spike extreme or Leg-2 start.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G3 — Stop / invalidation

### Frozen meaning
The stop is a structural invalidation level distinct from Entry. The source explains that returning through the relevant structural level invalidates the scenario.

### Not frozen
- exact wick/body/pivot coordinate;
- buffer/spread rule;
- universal candle index;
- execution/slippage convention.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G4 — Trigger

### Frozen meaning
The source demonstrates a trigger family involving one-, two-, and three-candle formations and also uses key-bar/follow-through terminology.

### Not frozen
- exact Boolean acceptance condition;
- whether every trigger variant is equivalent;
- close/wick/body requirements;
- exact activation timestamp;
- intrabar versus close-of-candle semantics.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G5 — AB=CD

### Frozen meaning
Leg 2 is expected to have approximately the same magnitude as Leg 1; the source explicitly names AB=CD.

### Not frozen
- A/B/C/D anchors;
- wick/body/structural-pivot model;
- tolerance band;
- rounding/precision convention;
- whether the target is measured from Entry, Leg-2 start, or another source coordinate.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G6 — Leg 2 / TP1

### Frozen meaning
The strategy seeks continuation into a second leg after correction, with TP1 generally preferred by the teacher. The source also explicitly distinguishes the beginning of Leg 2 from the entry concept in the narrated example.

### Not frozen
- executable projection origin;
- exact TP1 coordinate formula;
- exact relation between Leg-2 start and AB=CD anchors;
- tolerance and execution semantics.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G7 — Pending replacement

### Frozen meaning
A pending order can be deleted/replaced when a new candle materially changes the structural/risk distance. If the change is not materially large, the teacher keeps the existing order in the demonstrated case.

### Not frozen
- numeric materiality threshold;
- exact event timing;
- sizing formula after replacement beyond the general risk-management principle.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## G8 — Bearish mirror

### Frozen meaning
The bearish construction is the directional mirror of the bullish structure: Lower Highs → bearish continuation → Sell Limit → structural invalidation above the relevant structural High → Leg 2.

### Not frozen
- exact bearish OHLC anchor;
- universal wick/body/pivot rule;
- candle indexing and trigger acceptance.

### Status
**SOURCE-LIMITED / NON-EXECUTABLE**.

## What can be frozen safely now

The following semantic contract is frozen and may be used for documentation, fixture generation, and source-traceable research scaffolding:

`Context → Directional structure → Breakout + Follow-through → P-Gap → Correction → Pending Limit at relevant structural Low/High → Structural invalidation → Leg 2 continuation → AB=CD magnitude relationship → TP1 preference`

The contract is intentionally not an executable detector because its critical coordinates remain source-limited.

## Gate decision

- SOURCE RESOLUTION: **semantic PASS / source-limited geometry**
- SYNTHETIC FIXTURES: **PASS for discrimination**
- FROZEN GEOMETRY: **NOT PASSED**
- DEV: **LOCKED**
- VALIDATION: **LOCKED**
- ROBUSTNESS: **LOCKED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **LOCKED**

This freeze prevents future research or optimization from silently turning an unresolved source concept into a canonical formula.