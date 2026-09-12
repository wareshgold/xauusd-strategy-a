# SP2L G237 — B1 P-Gap Source Decision Record

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision:** `LEADING_HYPOTHESIS_RETAINED_NOT_FROZEN`

## Scope

This record consolidates the source evidence reviewed through G236 and makes a deliberately narrow B1 decision. It does not freeze a production P-Gap rule.

## Source evidence chain

The current evidence chain is:

1. Same-author comprehensive Gap material defines a bullish generic Gap from the distance between the high of the candle two bars earlier and the low of the current candle, consistent with `High[t-2] < Low[t]`.
2. Raw SP2L teaching around 31:00–32:10 explicitly marks the earlier and later participating candles with one large directional/spike candle between them and labels the construction `P-GAP`.
3. The same teaching section distinguishes `P-GAP` from `GAP / Common`.
4. The later SP2L teaching panel shows three numbered positive examples with shaded gap regions and states `Valid BO = P-Gap`.
5. The same panel contains a red-X directional example that lacks the clearly separated qualifying region visible in the positive examples.

Together these sources strongly support a gap/separation interpretation and make the generic three-candle relation a leading candidate.

## Leading executable hypothesis — H1

Bullish candidate:

`High[t-2] < Low[t]`

Interpretation for research only:

- candle `t-2` supplies the earlier upper endpoint;
- candle `t-1` is the intervening directional/spike candle in the illustrated construction;
- candle `t` supplies the later lower endpoint;
- a positive separation is required.

This hypothesis is **not yet a canonical Strategy A rule**.

## Why H1 is not frozen

The source does not provide sufficiently precise numerical semantics for all production decisions. The following remain unresolved:

- exact wick versus body endpoint semantics;
- whether the shaded P-Gap region is exactly the endpoint-to-endpoint interval;
- equality/touch behavior;
- minimum gap distance, if any;
- whether the intervening candle must satisfy a separate Spike definition;
- whether a Breakout-Gap close-location condition is mandatory in SP2L;
- exact bearish mirror;
- exact event timing for breakout/P-Gap validation.

The schematic evidence is intentionally not converted into pixel-estimated numerical thresholds.

## Research disposition

H1 is promoted only within the **research hypothesis layer** from `candidate` to `leading candidate`.

Competing hypotheses remain active for comparison:

- body-only endpoint relation;
- full-extrema relation with equality allowed;
- generic Gap plus Breakout-Gap context;
- generic Gap plus an SP2L-specific Spike condition;
- other source-defined combinations if later evidence appears.

No backtest performance may be used to choose among these source interpretations.

## Synthetic fixture disposition

The existing fixture matrix should continue to test the hypotheses independently. The rejected source example should remain a qualitative negative-control class until its exact OHLC representation can be established without visual guesswork.

Priority fixtures:

- strict full-extrema gap;
- body-only gap with overlapping wicks;
- exact-touch equality;
- directional movement without qualifying separation;
- generic gap with Breakout-Gap context;
- SP2L-specific Spike-condition variants if source evidence later requires them.

## Gate status

**SOURCE RESOLUTION:** `B1_LEADING_HYPOTHESIS_IDENTIFIED`  
**SYNTHETIC FIXTURES:** PASS / research-only  
**FROZEN GEOMETRY:** BLOCKED  
**DEV:** NOT AUTHORIZED for canonical P-Gap geometry  
**UNTOUCHED VALIDATION:** NOT AUTHORIZED  
**FRESH HOLDOUT:** NOT AUTHORIZED for strategy interpretation  
**PRODUCTION:** NOT AUTHORIZED

## Explicit prohibition

Do not implement H1 as the production P-Gap predicate solely because it is the leading interpretation. Do not add tolerances, body/wick substitutions, breakout filters, or minimum-gap thresholds to improve historical performance.

## Next gate candidate

If no higher-resolution source evidence is available, the next controlled step is to finalize the synthetic fixture specification for the competing B1 hypotheses and document exactly which source evidence each fixture represents. Historical DEV testing must remain blocked until the project explicitly freezes the B1 geometry and its semantics.
