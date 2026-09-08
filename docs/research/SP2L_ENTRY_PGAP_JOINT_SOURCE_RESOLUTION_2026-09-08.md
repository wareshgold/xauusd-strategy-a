# SP2L Entry / P-Gap Joint Source Resolution — 2026-09-08

## Objective
Resolve the remaining Entry-candle ambiguity and test whether the source visuals support an exact P-Gap boundary without importing FVG or harmonic geometry.

## Evidence reviewed
- Source-video frames around 34:00–36:40: `Valid BO = P-Gap`, three accepted-looking constructions and one rejected construction.
- Source-video frames around 46:00–47:10 and 2760–2790s: clean Entry/TP1/TP2/SL diagram.
- Source transcript: bullish correction reaches the first/prior Low; bearish mirror uses High; order can be placed manually or as a pre-set limit.
- Public TradingView description: previous lows/highs are described as potential entry levels; gap filter is separate. This remains secondary evidence.

## Entry-candle cross-check

The clean source diagram shows the Entry horizontal level independently from P-Gap and SL. In the bullish drawing, the Entry level visually aligns with a candle-level low in the corrective structure, consistent with the transcript's prior/first-low wording. The drawing is not precise enough to prove a universal absolute candle index across every Spike construction.

### Resolution

**SOURCE-CONFIRMED SEMANTIC:** bullish correction reaches a source-relevant prior Low and bearish correction reaches the mirrored prior High; execution is a pending limit in the Spike direction.

**STRONGEST CANDIDATE:** immediate/relevant preceding candle extreme (Low for BUY, High for SELL).

**NOT FROZEN:** a universal `i-1` rule. The source examples contain multiple Spike constructions and do not expose enough exact indexing information to prove that one fixed candle index applies to all of them.

Forbidden imports remain: generic swing detector, HL/LH algorithm, `entry=C`, 50% retracement, close-reclaim substitute.

## P-Gap boundary cross-check

Frames 2140–2170 explicitly label the concept `Valid BO = P-Gap`. Three constructions are treated as valid while one is rejected. The highlighted P-Gap regions are not sufficiently geometrically exact to map their boundaries to one unique OHLC pair. Importantly, the valid examples differ in the temporal placement of the gap relative to the directional sequence, so a fixed candle index cannot be assumed from the slide.

### Resolution

**SOURCE-CONFIRMED SEMANTIC:** P-Gap is a breakout-associated gap/non-overlap condition used to validate the breakout/Spike.

**STRONGEST CANDIDATE:** wick-range non-overlap in the breakout context.

**UNRESOLVED:** exact boundary pair, wick/body choice, candle timing, equality/touch handling, minimum gap size.

`P-Gap = generic three-candle FVG` remains rejected as a canonical rule.

## Joint dependency result

The safest deterministic research contract remains:

`valid breakout + source-defined P-Gap → Spike → correction → relevant prior Low/High → pending-limit entry`

with independent structural risk:

`Spike-origin candle → SL/invalidation`

and independent projection:

`source-defined Leg-1 magnitude → Leg-2 equal/approximately equal magnitude`

No source evidence establishes an identity among P-Gap boundary, Entry price, SL price, or classical A/B/C/D anchors.

## Gate decision

SOURCE RESOLUTION: advanced.

FROZEN GEOMETRY: BLOCKED.

Reason: P-Gap exact OHLC boundary and executable Entry/SL price conventions remain unresolved. Entry semantics are strong enough for a research interface but not enough for a canonical universal candle-index rule.

DEV / VAL / Fresh Holdout: locked.

PRODUCTION: unchanged.

## Next action

The highest-value remaining source artifact is an original indicator/template/settings view that exposes the P-Gap boundary and order-price construction. Historical performance must not be used to choose among these unresolved interpretations.
