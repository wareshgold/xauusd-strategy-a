# G354 — P-Gap / Pressure Gap geometry cross-reference

Date: 2026-09-12  
Gate: SOURCE RESOLUTION  
Status: **PASS for semantic/event-timing resolution; BLOCKED for executable P-Gap geometry freeze**

## Objective

Cross-reference the new Poursamadi `PriceAction (Gaps)` lesson with the SP2L source to determine whether the Pressure Gap examples visibly establish the same candle-boundary geometry as the generic gap explanation, and whether that geometry can be promoted to canonical SP2L P-Gap logic.

## Source inputs

1. `gap پورصمدی دوره جامع.mp4`
   - SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`
   - Duration: ~32:35.79
2. `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
   - SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
   - Duration: ~69:15.72
3. SP2L transcript `پورصمدیSP2L TRANSCIBE.txt`

## 1. Generic Gap geometry is source-confirmed

The Gap lesson explicitly teaches the displayed bullish gap as a distance between the **high of the candle two bars before** and the **low of the current candle**. The accompanying chart uses a highlighted region to show the gap location.

This is strong source evidence for a generic bullish gap relation of the form:

`High[i-2] < Low[i]`

with the existence of a positive distance indicating a gap in the displayed bullish orientation.

The source does not, in this lesson segment, establish a universal executable minimum gap size, tolerance, overlap policy, or wick/body/open/close substitution rule.

## 2. Pressure Gap example: visual cross-reference

At approximately 23:30–24:30 of the Gap lesson (source-local time around 1410–1440 s), the slide is explicitly titled **گپ فشار / Pressure Gap**. The chart contains a blue highlighted pressure region and red hand annotations around the transition into the continuing bearish movement.

The visual evidence is consistent with a directional gap occurring inside a broader pressure sequence, but the annotated rectangle is not a machine-readable declaration of exact OHLC endpoints. In particular, the frame does not label the two boundary prices as `Low[i-2]` and `High[i]`, nor does it specify whether wick extremes or candle bodies are intended.

Therefore:

- Pressure Gap is source-confirmed as a distinct gap category.
- The Pressure Gap example is visually compatible with the generic gap concept.
- The frame is **not sufficient by itself** to promote the generic `High[i-2] ↔ Low[i]` / symmetric bearish relation into a canonical P-Gap formula.

## 3. SP2L directly identifies P-GAP with Pressure Gap

The SP2L transcript states at ~31:43 that the breakout candle contains **P-GAP / گپ فشار**, and explicitly distinguishes it from E-GAP. It also says P-GAP, E-GAP and Common-GAP are different categories and that their formation location/context matters.

At ~35:37 the presenter describes two variants considered in the same SP2L strategy concept:

1. breakout first, then follow-through / higher lows, then P-GAP; or
2. higher lows first, then the gap forms.

The presenter says these have the same underlying concept and are treated as one in the current strategy, while noting they could be separated into different strategies later.

This is a stronger resolution than the prior audit: **P-GAP is not merely a generic gap visual; it is explicitly the Pressure Gap category and can occur at more than one point in the breakout/follow-through sequence.**

## 4. Breakout Gap must remain distinct from P-GAP

The Gap lesson separately defines **Breakout Gap** as a gap at the beginning of a movement. The SP2L source, however, calls the relevant gap `P-GAP / Pressure Gap` and discusses breakout + follow-through as the surrounding Spike sequence.

Therefore we must not collapse:

`Breakout Gap == P-GAP`

The current evidence supports only:

`P-GAP ↔ Pressure Gap`

and separately:

`Breakout Gap` is a source-defined gap category.

A P-GAP may participate in an SP2L breakout/Spike sequence, but that does not make every Breakout Gap a P-GAP.

## 5. Event-timing resolution for P-GAP / Spike

The SP2L transcript gives a useful deterministic ordering constraint without resolving the exact gap formula:

- a breakout can occur;
- the next candle can act as follow-through and fail to overlap the prior range sufficiently to preserve the breakout concept;
- P-GAP is used as a visual marker for this strong movement;
- alternatively, higher lows can appear before the gap;
- both source-described variants are treated as the same current SP2L concept.

This means a future implementation must **not** require `P-GAP` to be the first event before all other Spike evidence. The source explicitly allows at least two sequence variants.

## 6. What is now source-confirmed

| Dimension | Status | Source meaning |
|---|---|---|
| P-GAP semantic identity | **CONFIRMED** | P-GAP = Pressure Gap / گپ فشار |
| E-GAP semantic identity | **CONFIRMED** | E-GAP = Exhaustion Gap / گپ خستگی |
| Gap taxonomy | **CONFIRMED** | Breakout / Pressure / Exhaustion / Common are distinct categories |
| Generic bullish gap example | **CONFIRMED** | Displayed relation uses High[i-2] vs Low[i] |
| P-GAP can appear in SP2L breakout sequence | **CONFIRMED** | Source explicitly says breakout context + P-GAP |
| P-GAP timing variants | **CONFIRMED** | breakout→FT→P-GAP and higher-lows→P-GAP are both treated as one concept |
| P-GAP exact OHLC formula | **UNRESOLVED** | No source text/annotation freezes exact executable endpoints |
| Symmetric bearish formula | **PLAUSIBLE, NOT CANONICAL** | visually consistent but not explicitly labeled as a universal P-GAP formula |
| Minimum gap size | **UNRESOLVED** | no numeric threshold |
| Wick/body convention | **UNRESOLVED** | not labeled |
| Overlap/tolerance rule | **UNRESOLVED** | not specified |
| Universal candle count | **UNRESOLVED** | source gives examples, not a universal count |
| P-GAP = Breakout Gap | **REJECTED** | source taxonomy keeps categories distinct |

## 7. Synthetic-test implications

The source resolution now supports a tighter synthetic discrimination matrix, but **not a frozen formula**. Future fixtures should include at least:

- bullish generic gap satisfying `High[i-2] < Low[i]`;
- bearish mirrored visual candidate;
- a Breakout Gap at movement origin without sufficient evidence to classify it as Pressure Gap;
- a Pressure Gap appearing after sustained pressure/pause;
- SP2L variant A: breakout → follow-through → P-GAP;
- SP2L variant B: higher lows → P-GAP;
- visually similar gaps with wick overlap but body separation;
- visually similar gaps with body overlap but wick separation;
- gaps below/above a candidate minimum-size threshold;
- cases where P-GAP and E-GAP locations are close enough to expose context dependence.

These fixtures are research hypotheses only. No threshold or OHLC field substitution may be promoted from fixture performance.

## 8. Gate decision

**SOURCE RESOLUTION: PARTIAL PASS / GEOMETRY BLOCKED**

Resolved:

- semantic identity `P-GAP ↔ Pressure Gap`;
- taxonomy distinction from Breakout Gap and E-GAP;
- two source-described P-GAP timing variants within SP2L;
- generic bullish gap geometry as taught in the separate Gap lesson.

Still blocked:

- exact executable P-Gap formula;
- wick/body/open/close convention;
- minimum size / tolerance / overlap rule;
- exact P-Gap-to-breakout/follow-through machine event mapping;
- A/B/C/D anchor selection;
- executable entry/SL/TP geometry.

**No production or historical-optimization changes are justified by G354.**
