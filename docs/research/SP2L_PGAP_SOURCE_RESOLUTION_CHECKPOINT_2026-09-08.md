# SP2L P-Gap Source Resolution Checkpoint — 2026-09-08

## Scope

Research-only inspection of the uploaded authoritative SP2L video around the P-Gap teaching sequence (~34:00–36:30). Production is unchanged.

## Direct visual observations

1. The source explicitly labels the slide **“Valid BO = P-Gap”**.
2. One spike construction is marked with a red X while three constructions are presented as valid-looking variants.
3. The three accepted-looking variants do not place the apparent gap marker at one universal candle index. The source therefore supports temporal variation in where the gap appears within the spike construction.
4. The grey/blue highlighted P-Gap zones are illustrative regions. Their visible boundaries do not uniquely identify a machine-readable formula such as:
   - previous High → next Low;
   - body-top → body-bottom;
   - wick-to-wick range;
   - a fixed candle pair;
   - or another manually defined zone.
5. The earlier teaching frames show horizontal annotations around the spike construction, but the available resolution and hand-drawn nature do not establish a universal wick/body convention.
6. The source later writes **AB=CD**, but the P-Gap teaching frames do not establish classical A/B/C/D anchors.

## Combined source interpretation

The strongest deterministic meaning that can safely be promoted at this stage is:

`valid breakout/spike context + source-defined P-Gap occurrence`

where P-Gap is a distinct source-defined gap associated with the breakout/spike. A generic three-candle imbalance is not an acceptable substitute.

## What is now stronger

### Temporal placement

The source demonstrates multiple accepted-looking spike constructions, including constructions where the gap appears at different points in the sequence. Therefore a fixed rule such as “P-Gap must occur between candles N and N+1” is not source-safe.

### Context

P-Gap is not merely “any gap anywhere.” The source ties it to a valid breakout/spike construction and separately discusses different gap types. Therefore a standalone gap detector without breakout/spike context is insufficient.

### Generic imbalance

A generic three-candle FVG/imbalance implementation remains **REJECTED AS CANONICAL** because it would import an external definition of P-Gap.

## What remains unresolved

1. Exact P-Gap boundary convention.
2. Wick-vs-body treatment.
3. Equality/touch behavior when the two candidate boundaries are equal.
4. Minimum gap size, if any.
5. Exact candle-index/timing predicate across all accepted spike variants.
6. Whether the highlighted source zone represents the executable gap boundaries or only a visual teaching aid.

No threshold, buffer, tolerance, or body/wick rule is invented.

## Synthetic discrimination matrix

| Fixture | Question | Canonical result now |
|---|---|---|
| PG-R-01 | Prior High < next Low with separated bodies | Source-compatible candidate; formula unresolved |
| PG-R-02 | Wick separation but body overlap | Unresolved |
| PG-R-03 | Body separation but wick overlap | Unresolved |
| PG-R-04 | Exact touch/equality | Unresolved |
| PG-R-05 | Gap occurs immediately at breakout | Source-supported variant |
| PG-R-06 | Higher lows precede later gap | Source-supported variant |
| PG-R-07 | Later continuation gap without breakout context | Not automatically P-Gap |
| PG-R-08 | Generic three-candle imbalance without source context | Rejected as canonical |
| PG-R-09 | Breakout/follow-through but no visible non-overlap | Insufficient P-Gap evidence |

## Gate decision

**P-Gap is not frozen.**

The source-resolution pass has narrowed the interpretation to a source-defined breakout-associated gap/non-overlap concept with multiple supported temporal constructions, but it has not established an executable boundary formula.

Therefore:

- FROZEN GEOMETRY: **BLOCKED**
- DEV: **LOCKED**
- VAL: **LOCKED**
- HOLDOUT: **LOCKED**
- PRODUCTION: **UNCHANGED**

## Important correction

The grey/blue rectangles in the teaching slide must not be treated as proof of a precise wick or body formula. They are evidence that a gap region is being highlighted, not sufficient evidence for its exact numerical boundaries.

## Next source-resolution target

The remaining highest-value task is to inspect the source's entry/SL diagram jointly with the three P-Gap variants and determine whether one candle-level boundary is consistently reused for both P-Gap identification and the correction/entry reference. Until that relationship is directly established, P-Gap and Entry must remain separate unresolved geometry variables.
