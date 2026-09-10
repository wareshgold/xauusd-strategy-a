# SP2L G236 — P-Gap Cross-Example Endpoint Review

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `REPEATED_ENDPOINT_COMPATIBILITY_STRONG_GEOMETRY_NOT_FROZEN`

## Objective

Continue B1 P-Gap source resolution by reviewing the independent schematic panel containing the rejected example and three numbered positive examples around 35:50–36:16. The goal is to determine whether the positive examples repeatedly support the same two-candle endpoint relationship and whether the rejected example provides a meaningful negative control.

## Source frame reviewed

The reviewed panel contains:

- one directional sequence marked with a red X;
- three positive examples numbered 1, 2, and 3;
- shaded regions associated with the positive P-Gap examples;
- the explicit annotation `Valid BO = P-Gap`.

The positive examples repeatedly show a directional candle sequence in which the visually relevant gap region is associated with the candle two positions apart from the later candle, consistent with the previously observed SP2L teaching construction.

## Cross-example endpoint observation

Across the three positive examples, the shaded P-Gap region is visually consistent with a separation between an earlier upper extreme and a later lower extreme, with one intervening directional candle.

This repeated structure is compatible with the research candidate:

`High[t-2] < Low[t]`

for the bullish construction.

The strongest source interpretation remains the combination of:

1. the same-author Gap-course definition of a generic bullish Gap using `High[t-2]` versus `Low[t]`;
2. the raw SP2L teaching sequence where the author explicitly marks the earlier and later participating candles with the spike between them;
3. repeated positive SP2L examples showing the same visual separation pattern;
4. the rejected example showing that directional progression without the same qualifying separation is not accepted as `Valid BO = P-Gap`.

## Wick/body determination

The source panel is still not sufficiently precise to freeze the shaded rectangle edges as exact wick extrema. In particular:

- the schematic candles are low-resolution;
- the shaded regions are teaching annotations rather than a numerical chart scale;
- hand-drawn marks overlap candle bodies/wicks in places;
- the rectangle boundaries cannot be measured as exact OHLC levels without introducing visual-estimation error.

Therefore the evidence strongly favors a full-extrema interpretation but does not prove that the production rectangle must equal the exact wick-to-wick interval.

## Negative control

The red-X example is useful as a qualitative negative control. It shows directional movement but lacks the same clearly separated P-Gap region visible in the accepted examples.

This supports the distinction:

`directional Spike != Valid BO`

and strengthens the requirement that a qualifying gap/separation be present.

It does not uniquely establish whether the source predicate is:

- generic three-candle Gap;
- generic Gap plus breakout context;
- generic Gap plus an SP2L-specific spike condition;
- or another source-defined combination.

## What is now source-supported

The following research statements are now strongly supported:

- P-Gap is a first-class condition associated with valid breakout in the SP2L teaching material.
- P-Gap is visually associated with a gap/separation, not merely a directional candle.
- The relevant positive constructions repeatedly use an earlier candle, one intervening spike/directional candle, and a later candle.
- The same-author generic Gap definition makes `High[t-2] < Low[t]` a strong candidate for the bullish endpoint relation.
- The negative example is consistent with failure of the qualifying separation condition.

## What remains unresolved

This pass does **not** freeze:

- wick versus body as executable boundary semantics;
- strict inequality versus equality/touch;
- minimum positive gap size;
- exact rectangle/shaded-zone boundaries;
- mandatory spike magnitude/shape condition;
- mandatory breakout close-location condition;
- exact bearish mirror;
- exact event timing for P-Gap validity;
- any entry, stop, target, session, liquidity, BOS/MSS, displacement, FVG, or retest rule.

No backtest result is used to choose among these interpretations.

## Research decision

B1 should remain in `SOURCE_CORRELATED_CANDIDATE` rather than `FROZEN`.

The evidence is now sufficient to prioritize the full-extrema H1 hypothesis in synthetic testing, while retaining competing hypotheses as independently testable alternatives.

No candidate is promoted to production from this source pass.

## Synthetic-fixture implication

Prioritize fixtures covering:

1. full-extrema strict inequality;
2. body-only gap with overlapping wicks;
3. exact-touch equality;
4. directional move without qualifying gap;
5. gap with source-described Breakout-Gap context;
6. any later-discovered SP2L-specific additional condition.

The negative control should remain qualitative until its source geometry can be encoded without visual guesswork.

## Gate decision

**Source Resolution:** STRONGER; repeated cross-example compatibility established.  
**Synthetic Fixtures:** PASS for the existing research matrix.  
**Frozen Geometry:** BLOCKED.  
**DEV / VAL / Fresh Holdout / Production:** unchanged and not authorized.

## Next source task

Move one level deeper into the raw SP2L teaching material: inspect another independent P-Gap construction where the author draws endpoint marks during the explanation, preferably before/after the schematic panel, and determine whether those marks explicitly terminate at wick extrema. If no clearer source geometry exists, prepare a narrowly scoped B1 decision record documenting `High[t-2] < Low[t]` as the leading source-correlated hypothesis while preserving unresolved semantics explicitly.
