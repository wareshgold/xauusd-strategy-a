# SP2L P-Gap / Entry / SL Triangulation

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION — progressing; FROZEN GEOMETRY remains blocked  
**Production impact:** none

## Objective

Triangulate three source elements together rather than resolving them independently:

1. P-Gap / valid breakout geometry;
2. pending-limit entry during the correction;
3. structural invalidation / stop placement.

The source transcript is authoritative for semantics. Visual frames are supporting evidence for what is actually drawn. No historical profitability result is used to define meaning.

## Source evidence

### P-Gap / breakout

At 30:53–31:29 the instructor distinguishes spike from channel movement and defines breakout using a close beyond a prior level plus a follow-through/key bar that cannot return into the prior range.

At 31:43–32:12 P-Gap is explicitly named and distinguished from E-Gap/Common-Gap; the instructor states that gap location matters.

At 34:14–35:37 P-Gap is described as the visual marker for where breakout occurred. At 34:25 the instructor states that when the referenced high and low do not overlap, a gap occurs together with breakout and follow-through. Two constructions are treated as conceptually equivalent: breakout-first followed by higher lows, and higher lows first followed by a later gap. A third construction is also included in the spike family.

**Inference status:** strong evidence for *non-overlap in breakout/spike context*; exact candle boundaries, wick/body semantics, and timing remain unresolved.

### Entry

At 38:38 the instructor defines the start of correction as price moving below the first low in the bullish example and says an order can be placed manually or as a pre-set limit.

At 39:11–39:26 he explicitly says there is no need to wait for the next candle and demonstrates a Buy Limit already placed. The SL distance is known before activation; a return to the invalidation area cancels the scenario.

At 46:15–46:36 he again describes three-candle situations where price returns to the low of the candle and the first pullback creates the opportunity to continue toward Leg 2.

**Inference status:** pending-limit execution during correction is source-confirmed; exact limit price is not yet frozen.

### Stop / invalidation

At 39:26 the instructor ties invalidation to return to the structural area that would invalidate the trend scenario. At 39:48–40:16 an existing pending order may be deleted/replaced if the subsequent candle materially changes the stop distance.

At 41:18 the activated order is shown with an SL. The source does not provide a machine-readable OHLC anchor in the transcript.

**Inference status:** structural invalidation is source-confirmed; exact executable SL anchor remains unresolved.

## Visual triangulation

The 35:40 slide is especially useful because it places the rejected construction beside three accepted-looking constructions and draws blue shaded rectangles at the gap locations. The drawing supports the semantic statement that P-Gap is a visual marker of breakout location, but the rectangle is not sufficiently precise to establish whether the boundaries are:

- prior High → current Low;
- prior body top → current body bottom;
- wick-to-wick extremes;
- another candle pair;
- or a broader manually highlighted zone.

The same slide therefore supports **candidate family PG-NONOVERLAP**, but does not justify a production formula.

The 38:20–40:10 diagram sequence separately confirms Buy Limit, an order line, SL, and delete/replacement handling. It does not prove that the order line equals a specific AB=CD anchor.

## Triangulation matrix

| Candidate | P-Gap evidence | Entry evidence | SL evidence | Status |
|---|---|---|---|---|
| Prior High → next Low non-overlap; entry at prior Low/High | strong | strong candidate | unresolved | **candidate A** |
| Body-only gap; entry at prior body extreme | weak | weak | unresolved | candidate B |
| Wick-only gap; entry at prior wick extreme | weak | weak | unresolved | candidate C |
| Generic 3-candle imbalance | not source-specific | none | none | reject as canonical |
| Gap anywhere after trend extension | conflicts with P/E-Gap location distinction | none | none | reject as canonical |
| Entry = geometric C | no direct source proof | contradicted by unresolved mapping | none | unresolved / do not assume |
| Entry = prior-candle Low/High | strong transcript + official-page support | strong | independent | **strong candidate, not frozen** |

## Important geometry correction

The real XAUUSD chart around 62:00–64:30 must **not** be interpreted as containing authoritative A/B/C/D labels. The visible annotations are predominantly numeric/management annotations such as `1`, `2`, `2X`, `E`, and `0.0`. The transcript itself explicitly contrasts classical internet A/B/C/Fibonacci treatment with the source's candle-level method at 36:31–36:46.

Therefore the current working geometry is:

`source-defined Spike → source-defined Correction → source-defined Leg 1 magnitude → source-defined Leg 2 of equal magnitude`

not a classical harmonic A/B/C/D implementation.

## Synthetic fixtures required before freeze

### PG-ENTRY-01
Bullish breakout where prior High < breakout-candle Low. Correction reaches prior-candle Low. Candidate pending-limit equals prior Low.

Purpose: tests the strongest combined interpretation.

### PG-ENTRY-02
Same P-Gap geometry, but correction reaches prior Low while a hypothetical limit is placed elsewhere.

Purpose: prevents silently equating correction trigger, limit price, and arbitrary geometric point.

### PG-ENTRY-03
Prior High < next Low by wick extremes, while bodies overlap.

Purpose: distinguish wick-based from body-based P-Gap.

### PG-ENTRY-04
Bodies separate, but wick extremes overlap.

Purpose: distinguish body-based from wick-based P-Gap.

### PG-ENTRY-05
Breakout-first P-Gap followed by higher lows.

Purpose: preserve the source's accepted first construction.

### PG-ENTRY-06
Higher lows first, P-Gap later.

Purpose: preserve the source's statement that this is conceptually equivalent in the current strategy.

### PG-ENTRY-07
Gap appears only after a substantial extension.

Purpose: test P-Gap versus E-Gap/location distinction.

### PG-ENTRY-08
Correction crosses candidate entry intrabar and closes back above it.

Purpose: leave intrabar fill ordering explicitly unresolved until execution semantics are sourced.

### LEG-SL-01
Same visual Spike but three competing Leg-1 anchors: Spike origin, breakout candle, first structural low/high.

Purpose: force exact Leg-1 endpoint resolution from source evidence rather than backtest fit.

### LEG-SL-02
Same Spike with shallow and deep corrections; structural invalidation unchanged versus dynamically moved.

Purpose: test whether SL follows the original structure or is recalculated with correction depth.

## Current decision

**Do not freeze P-Gap yet.**

The strongest source-aligned candidate is a breakout-context non-overlap relationship, with the bullish entry strongly suggesting return to the relevant prior candle Low (bearish mirror: prior High). However, exact P-Gap boundary semantics, exact pending-limit price, exact SL anchor, and intrabar ordering remain open.

## Next gate action

1. Run the synthetic fixtures above against competing interpretations.
2. Inspect the 34:14–35:37 visual sequence frame-by-frame for boundary identity, not just the final shaded rectangle.
3. Cross-check the 38:38–40:16 entry drawings against the same candle-level anchors.
4. Only if one interpretation is explicitly supported by source evidence should the geometry be frozen.
5. Keep DEV/VAL/production locked until that freeze.

**Conclusion:** meaningful progress, but no canonical P-Gap formula is authorized yet.
