# SP2L P-Gap / Entry Boundary Cross-Check — 2026-09-08

## Objective

Resolve whether the source video's P-Gap visual can be mapped to an exact OHLC boundary and whether that boundary is the pending-limit entry level.

## Evidence hierarchy

1. Original SP2L source video and its timestamped transcript.
2. Source frames around 34:00–37:00 and 46:00–50:00.
3. TradingView/TradingFinder page as external secondary evidence only.
4. No third-party implementation is promoted to canonical source meaning.

## Source-video observations

The source slide around 35:40–36:10 explicitly states `Valid BO = P-Gap` and shows three accepted-looking bullish constructions plus one rejected construction.

The blue/grey P-Gap rectangles are not machine-precise OHLC markings. In the closest frame inspection, the highlighted rectangle can overlap candle bodies/wicks rather than sitting entirely in an empty visual gap. Therefore the rectangle itself cannot establish a body-gap or wick-gap formula.

The transcript is stronger than the rectangle geometry: around 34:25 the instructor explains that when the relevant high and low do not overlap, a gap occurs in the context of a breakout and follow-through. This supports a non-overlap semantic but does not safely establish a fixed candle index, equality convention, or minimum size.

The three accepted constructions also demonstrate that P-Gap timing is relational to the breakout/spike sequence rather than necessarily tied to one absolute candle index.

## Candidate boundary interpretations

| Candidate | Result | Reason |
|---|---|---|
| Previous candle High -> next candle Low, bullish; previous Low -> next High, bearish | STRONGEST CANDIDATE | Directly matches source language about a high and low not overlapping and the bullish/bearish mirror semantics. Still not frozen because exact candle pairing is unresolved across all variants. |
| Body top -> next body bottom | UNRESOLVED | Visual rectangles do not establish body-only boundaries. |
| Wick-to-wick range non-overlap | UNRESOLVED / plausible | Consistent with literal high/low wording, but the exact pair is not frozen. |
| Generic three-candle FVG | REJECTED AS CANONICAL | Not source-confirmed; source discusses P-Gap and breakout variants without providing the generic FVG rule. |
| Entry = P-Gap boundary | REJECTED AS ASSUMPTION | Source separately describes correction and a pending limit at the prior/relevant candle Low/High. |
| Entry = prior/relevant Low/High | STRONG SEMANTIC CANDIDATE | Supported by source transcript and official/source-aligned material, but exact relevant-candle selection remains unresolved across all variants. |

## External TradingView cross-check

The TradingView page for `SP2L Pour Samadi Indicator [TradingFinder]` is a protected/closed-source script. Its public description states that the spike creates imbalance/FVG and that bullish entries use previous lows while bearish entries use previous highs; it also states that SL is placed below/above the candle where the spike originated. It exposes a configurable Gap Filter but does not expose the protected formula.

This is useful as corroboration/hypothesis generation, not canonical proof. In particular, its explicit FVG terminology cannot be used to redefine the source video's P-Gap as generic FVG.

## Current deterministic semantic model

The safest current model is:

`source-defined breakout/spike context`
`-> source-defined P-Gap occurrence (non-overlap semantics; exact formula unresolved)`
`-> correction`
`-> correction reaches the relevant prior candle Low (BUY) / High (SELL)`
`-> pending-limit order in spike direction

P-Gap and Entry remain separate concepts.

## What remains unresolved

- Exact P-Gap candle pair for every accepted source variant.
- Whether `high/low` means wick extrema or body boundaries.
- Equality/touch behavior.
- Minimum gap size, if any.
- Exact timing of P-Gap recognition (intra-sequence vs close-confirmed).
- Exact identity of the `relevant prior candle` for the pending limit across all spike variants.
- Exact executable SL price despite the origin-candle semantic.

## Gate decision

**SOURCE RESOLUTION: advanced but incomplete.**

**FROZEN GEOMETRY: BLOCKED.**

No P-Gap formula, FVG equivalence, body percentage, spike threshold, Fibonacci anchor, or market-close substitute is promoted to production.

## Next discriminating action

Use synthetic fixtures that hold the source-defined breakout/follow-through sequence constant while varying only:

1. wick non-overlap,
2. body non-overlap,
3. equality/touch,
4. candle-pair timing,
5. entry-level independence.

Only a source visual or explicit source wording that discriminates one candidate should freeze the corresponding geometry.
