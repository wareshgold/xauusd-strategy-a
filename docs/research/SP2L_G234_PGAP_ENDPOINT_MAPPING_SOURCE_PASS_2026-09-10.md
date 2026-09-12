# SP2L G234 — P-Gap Endpoint Mapping Source Pass

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `STRONG_SOURCE_CORRELATION_GEOMETRY_STILL_NOT_FROZEN`

## Objective

Continue the source-resolution task from G233 by inspecting the raw SP2L teaching sequence around 31:00–32:10, with particular attention to the moment where the author marks the candles associated with the P-Gap construction.

The objective is to determine whether the same-author generic Gap relation recovered from the comprehensive Gap course can be mapped to the actual SP2L candle sequence without inventing OHLC boundaries.

## Raw SP2L evidence reviewed

The relevant teaching sequence contains a bullish four-candle schematic consisting of:

1. an earlier/small bullish candle;
2. a large bullish directional candle (the spike);
3. a following/small bullish candle;
4. a later continuation candle.

During the source annotation pass, the author visually circles the earlier small candle and the following small candle, with the large directional candle between them. The annotation therefore visually distinguishes the two candles separated by one intervening candle.

The sequence is subsequently labeled with `P-GAP` in the same teaching section. The source later shows the three numbered positive P-Gap examples and the explicit `Valid BO = P-Gap` statement.

## Endpoint-mapping observation

The comprehensive Gap course separately defines a bullish generic Gap using the distance between:

`High[t-2]` and `Low[t]`

with a Gap present when:

`High[t-2] < Low[t]`

The SP2L teaching sequence is visually consistent with the same indexing relationship:

- the earlier circled candle corresponds to the candle two positions before the later circled candle;
- the large spike is the intervening candle;
- the later circled candle is the current/following candle;
- the visual annotation is therefore compatible with comparing the earlier candle's upper extreme with the later candle's lower extreme.

This is materially stronger evidence than the G226 schematic-only comparison because the source annotation explicitly draws attention to the participating candles in the actual SP2L teaching sequence.

## What this pass establishes

The evidence now strongly supports the following research hypothesis:

### H1 — Generic three-candle P-Gap relation

Bullish candidate:

`High[t-2] < Low[t]`

with the intervening candle being the directional/spike candle in the illustrated SP2L construction.

Status: **strong source-correlated candidate**.

The result is consistent across:

- the same-author comprehensive Gap-course definition;
- the raw SP2L teaching sequence;
- the SP2L sequence's explicit P-Gap labeling;
- the three numbered positive P-Gap examples reviewed in G226.

## Important remaining uncertainty

This pass does **not** justify freezing the complete production P-Gap predicate yet.

The following remain unresolved:

- whether `High[t-2]` and `Low[t]` are exactly the canonical wick extrema or simplified teaching references;
- whether the shaded P-Gap rectangle boundaries are exactly those two OHLC levels;
- whether a minimum positive distance is required beyond strict inequality;
- whether the intervening candle must itself satisfy an additional spike/breakout condition;
- whether the source's `P-GAP` label means the generic Gap relation alone or the generic relation plus an SP2L-specific condition;
- exact bearish mirror geometry;
- exact treatment of equality/touch;
- exact timing at which the P-Gap becomes valid relative to breakout/follow-through;
- whether any additional close-location condition from the Gap-course Breakout Gap category is required for SP2L P-Gap.

## Explicit non-inferences

This pass does **not** infer:

- `P-Gap = Breakout Gap`;
- `P-Gap = Pressure Gap`;
- `P-Gap = FVG`;
- body-only boundaries;
- a minimum gap size;
- a tolerance selected from backtests;
- any liquidity/BOS/MSS/displacement/retest rule;
- any session filter;
- any entry/SL/TP geometry from the P-Gap observation.

No historical performance result is used to select the source interpretation.

## Synthetic-fixture implication

The existing G227/G228/G231 fixture matrix remains useful. The new source evidence suggests that the following distinction should receive priority in the next fixture/source review:

1. strict full-extrema relation `High[t-2] < Low[t]`;
2. body-only separation with overlapping wicks;
3. exact-touch equality;
4. generic gap without breakout context;
5. gap with the source-described Breakout-Gap context;
6. an SP2L-specific additional condition, if later source evidence demonstrates one.

The fixture suite must continue to report each hypothesis independently rather than collapsing them into a single production predicate.

## Gate decision

**Source Resolution:** improved, but **BLOCKED at final executable P-Gap geometry**.

**Synthetic Fixtures:** PASS from G233.

**Frozen Geometry:** BLOCKED.

**DEV / VAL / Fresh Holdout / Production:** unchanged and not authorized.

## Next source task

Target the next raw SP2L P-Gap teaching/example sequence and determine whether the same two-candle endpoint relationship is repeated with the same candle indexing and wick/extrema semantics. Priority should be given to frames where the P-Gap region, candle wicks, and any hand-drawn endpoint marks are simultaneously visible.

If repeated source evidence confirms the exact endpoint semantics in multiple independent constructions, the project may then prepare a narrowly scoped B1 source-resolution decision record. Until that occurs, `High[t-2] < Low[t]` remains a research candidate rather than a frozen production rule.
