# G412 — Transcript Source Geometry Decision Matrix

Date: 2026-09-14
Parent: G411
Status: SOURCE-CONSTRAINED / GEOMETRY NOT FROZEN

## Purpose

Convert the recovered transcript evidence into a strict decision matrix for the remaining G400 geometry blockers. This artifact records what the source establishes, what remains unresolved, and what must not be promoted from interpretation into production logic.

## Source evidence

### P-Gap

At 34:14–34:25 the speaker identifies P-GAP as a sign used to distinguish the breakout and describes a case where the first candle's high and following candle's low do not overlap, producing a gap associated with breakout + follow-through. At 34:35–35:37 the source explicitly treats two event orderings as the same strategy concept: breakout then higher lows then P-Gap, versus higher lows then P-Gap.

Decision:
- SOURCE CONFIRMED: P-Gap is a source-specific pressure-gap concept associated with the valid breakout/spike structure.
- STILL UNRESOLVED: exact OHLC boundary formula, required magnitude, tolerance, and whether the illustrated gap is the sole executable P-Gap test.
- PROHIBITED: promoting a generic three-candle gap, body gap, or wick gap as canonical solely from resemblance.

### AB=CD / Leg 1 = Leg 2

At 36:15 the source explicitly equates 2Leg with AB=CD. At 36:59–37:08 the expected second leg is described as equal to the first leg. At 37:57 the same relationship is repeated.

Decision:
- SOURCE CONFIRMED: second-leg magnitude relationship / AB=CD concept.
- STILL UNRESOLVED: exact A/B/C/D candle anchors, price fields, origin selection, and equality tolerance.
- PROHIBITED: choosing anchors or tolerance by backtest performance.

### Entry

At 38:18–38:38 the bullish correction is described as moving below the first low; the order may be placed manually or as a pre-defined limit there. At 38:53–39:26 the source explains that after gap + breakout + follow-through, the limit can be placed during the first three candles and that the distance to the stop is known before activation. At 39:26–40:07 the scenario can be cancelled/adjusted as subsequent price action changes the setup.

Decision:
- SOURCE CONFIRMED: pending-limit execution is canonical conceptually; it is not a market-close reclaim.
- PARTIALLY RESOLVED: correction reaches below the first low in the illustrated bullish case.
- STILL UNRESOLVED: exact limit price field/level, touch/fill semantics, persistence rule, overshoot handling, and exact pre-fill invalidation algorithm.
- PROHIBITED: assuming fill price equals geometric C.

### Stop

At 39:26 the source explicitly reasons about distance to SL before activation and cancellation if price returns to the invalidating area. At 41:18 the activated position is shown with an SL. The official source corroboration also identifies the spike-origin candle as the stop reference, but the exact executable boundary remains unresolved.

Decision:
- SOURCE CONFIRMED: structural invalidation/stop is tied to the setup's source-defined invalidating area and spike-origin structure.
- STILL UNRESOLVED: exact wick/body price boundary, buffer, and executable stop price.
- PROHIBITED: selecting wick/body or buffer from convention or performance.

### Targets

At 42:26–42:37 the source distinguishes TP1 and TP2 and states that TP1 is the speaker's usual choice; TP2 is relatively large and the strategy's stop is relatively large, so target 1 is preferred. At 1:04:19–1:04:32 the later worked example explicitly places the R=1 target at the illustrated level and notes R=2 as an alternative.

Decision:
- SOURCE CONFIRMED: R=1 is the primary/core target convention; R=2 is an alternative.
- STILL UNRESOLVED: exact geometric mapping of TP1/TP2 from the frozen entry/stop/AB=CD structure.
- PROHIBITED: inventing a TP2 extension or mapping before visual/source resolution.

## Gate consequence

The transcript substantially narrows all seven G400 blockers but does not close them. G400 remains BLOCKED.

No production geometry is frozen by this artifact.

Required next research action: obtain provenance-controlled visual frame artifacts for the five source windows listed in G410 and compare the visible horizontal levels/candle boundaries against the transcript. If a source ambiguity remains after visual reconciliation, retain it as unresolved and do not optimize it.

## Explicit non-promotion list

The following remain research hypotheses only:
- generic three-candle P-Gap;
- body-boundary P-Gap;
- wick-boundary P-Gap;
- arbitrary A/B/C/D selectors;
- fill-as-C;
- arbitrary AB=CD tolerance;
- arbitrary wick/body stop choice;
- arbitrary TP2 extension;
- session/time filters as canonical strategy conditions.

## Gate state

`G412 = PASS — SOURCE DECISION MATRIX`

`G400 = BLOCKED`

`FROZEN_GEOMETRY = NOT AUTHORIZED`

`DEV = NOT AUTHORIZED`

`VALIDATION = PROTECTED`

`PRODUCTION = BLOCKED`
