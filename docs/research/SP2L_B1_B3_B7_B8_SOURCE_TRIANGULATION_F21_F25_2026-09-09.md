# SP2L B1-B3-B7-B8 Source Triangulation — F21-F25 — 2026-09-09

## Gate

**SOURCE RESOLUTION: PARTIAL PASS — narrowed further.**

**SYNTHETIC DISCRIMINATION: PASS.**

**FROZEN GEOMETRY: BLOCKED.**

No historical profitability was used to select source meaning.

## Primary evidence

Primary evidence is the creator's SP2L video `7HEC5mO3d3U`, recovered transcript blob `47f867385338738a23b2d06dc48e67b852127243`, and direct frame inspection.

Key source passages:

- 31:43-32:21: P-Gap as a pressure gap, distinct from E-Gap/Common-Gap; valid breakout remains a breakout.
- 33:37-35:50: three source constructions; breakout + follow-through + P-Gap, higher-low sequence + P-Gap, and the third candle-count construction.
- 38:18-39:26: higher lows, correction below the first low, manual/Limit order, pre-positioned Buy Limit, structural invalidation.
- 39:48-40:16: pending order may be deleted/replaced when subsequent structure changes risk distance materially; no numeric threshold supplied.
- 41:18-42:37: triggered Buy + SL, 2X/second-position concept, TP1/TP2 distinction.
- 49:47-50:56: clean higher-low trend, breakout, trigger, P-Gap versus late/extended E-Gap condition.
- 55:02-56:20: clean bearish example with `SL`, `Enter`, and `leg 2` separated; lower-high/lower-low structural progression and R1 discussion.
- 57:05-58:22: additional trigger, Buy Limit activation, 2X and TP1 examples.

## B1 — P-Gap geometry

### Newly resolved source-safe structure

The source gives two materially distinct but accepted construction orders:

1. breakout → follow-through → P-Gap;
2. higher-low structural sequence → P-Gap.

At 34:25 the teacher describes a gap where the prior high and next low do not overlap, associated with breakout + follow-through. At 34:35 he explicitly shows another case where the gap occurs on the following candle. At 34:44-35:02 he contrasts the order of events: breakout first versus higher lows first, then gap, and states their concept/nature is treated as the same for this strategy.

### Decision

**P-Gap is a first-class, context-dependent source concept.**

The evidence supports using adjacent candle range separation as a *candidate geometric primitive* for research, but does not authorize a single universal OHLC formula or a generic three-candle FVG detector.

### Status

- Concept: **CONFIRMED**
- Context/order variants: **CONFIRMED**
- Generic three-candle imbalance substitution: **REJECTED**
- Exact universal OHLC boundaries: **UNRESOLVED**

## B2 — Entry anchor

### Source evidence

At 38:38 the teacher says that when the next candle begins the correction below the first low, the order can be placed manually or as a Limit in advance. At 39:11 he explicitly says there is no need to wait for the next candle and that the Limit can already be placed.

The direct frame sequence around 38:40-39:50 shows a separate Buy Limit level and a deeper structural SL level. As structure develops, the demonstrated order level can be moved upward rather than being mechanically fixed to the original Spike low.

### Decision

The source supports the abstraction:

`Correction → relevant structural Low/High → pending Limit`

Competing exact anchors remain:

- first structural Low/High;
- evolving/current relevant HL/LH;
- other source-specific structural reference.

`Entry = Leg2Start` remains rejected as a universal rule.

### Status

- Pending Limit mechanism: **CONFIRMED**
- Market-close reclaim substitution: **REJECTED**
- Fixed original low/high for every variant: **NOT PROVEN**
- Evolving relevant HL/LH: **STRONG CANDIDATE in demonstrated variant**
- Exact price edge (wick/body): **UNRESOLVED**

## B3 — Structural invalidation / SL

The source explicitly ties invalidation to a structural return level and shows Entry and SL as distinct levels. The 55:02 example is particularly useful because the teacher narrates and visually separates `SL`, `Enter`, and `leg 2`.

### Decision

The canonical semantic boundary is:

`Source structural invalidation → Stop Price`

The exact OHLC anchor remains unresolved. Wick, body edge, pivot and buffer are not selected.

### Status

- Structural invalidation: **CONFIRMED**
- Fixed-distance stop: **REJECTED as source meaning**
- Wick/body/pivot exact anchor: **UNRESOLVED**
- Arbitrary buffer: **UNRESOLVED / not authorized**

## B7 — Pending-order replacement

At 39:48-40:16 the teacher permits deleting/replacing the pending order if a later candle changes the distance to SL materially. He then says that in the demonstrated case the distance is not large enough to damage money management, so he keeps/moves the order; if it were large, he would place a new order with new sizing.

### Decision

The source establishes a qualitative state transition:

`material structural/risk-distance change → replacement may be required`

but supplies no deterministic numerical threshold.

Therefore the following remain prohibited until source-confirmed:

- percentage threshold;
- point/pip threshold;
- ATR multiple;
- fixed candle count;
- risk-percent threshold used as a geometry substitute.

### Status

**QUALITATIVE RULE CONFIRMED; EXACT REPLACEMENT THRESHOLD UNRESOLVED.**

## B8 — Bearish mirror

The direct source examples and narration provide strong evidence for directional mirroring. The source discusses lower highs for bearish structures and later demonstrates a bearish setup where the structural sequence produces `SL` above, `Enter` separately below, and the second bearish leg continuing downward. The source also describes the clean bearish progression and R1 objective.

### Safe abstraction

Bullish:
`Higher Lows → Breakout/P-Gap → Correction → Buy Limit → SL below structural invalidation → Leg 2`

Bearish:
`Lower Highs → Breakout/P-Gap → Correction → Sell Limit → SL above structural invalidation → Leg 2`

### Important boundary

This establishes the **directional structural mirror**, not every exact bearish OHLC anchor. Exact bearish Entry/SL wick-body semantics remain unresolved until a sufficiently clear mirrored frame is source-triangulated.

## Combined resolution

The uncertainty has now concentrated into five geometry items:

1. exact P-Gap OHLC boundary;
2. exact Entry structural anchor and wick/body edge;
3. exact SL OHLC anchor and any source-defined buffer;
4. deterministic pending-order replacement condition;
5. exact bearish mirrored candle-level geometry.

## Production boundary

Still prohibited:

- historical optimization to choose among source interpretations;
- generic FVG as P-Gap;
- market reclaim instead of pending Limit;
- fixed-distance SL;
- invented replacement threshold;
- invented wick/body rule;
- invented bearish anchor rule.

## Next research action

Use a final targeted frame pass on the clearest P-Gap constructions and the clearest bullish/bearish entry/SL examples. The goal is not to search indefinitely; it is to determine whether the source contains enough evidence for a unique geometry. If not, mark the item `UNRESOLVED` and freeze only the semantics that are actually source-supported.
