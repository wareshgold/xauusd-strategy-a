# SP2L P-Gap Boundary Resolution

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Status:** `BOUNDARY NOT FROZEN`  
**Production impact:** none

## Objective

Resolve the P-Gap boundary semantics from the primary source video by combining transcript evidence with frame-by-frame inspection of the teaching diagrams. The target ambiguity is whether the gap boundary is defined by wick High/Low, candle body Open/Close, or another manually selected candle-level boundary.

## Source material inspected

Primary video:
`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Relevant teaching interval:
`34:10–35:40`

Supporting interval:
`38:20–40:20`

Primary transcript:
`docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`

## 1. 34:10–35:40 P-Gap teaching slide

The slide explicitly displays `Valid BO = P-Gap` and presents multiple accepted constructions beside a rejected construction. The accepted constructions are illustrated with translucent rectangular regions near the breakout structure.

### What the frames establish

1. P-Gap is being used as a **visual marker associated with valid breakout**.
2. The source intentionally presents more than one temporal construction rather than one fixed candle index.
3. The shaded regions are drawn around the breakout/gap area, not as a generic gap anywhere later in the trend.
4. The drawings are schematic and do not expose enough pixel-precise information to establish whether the rectangle boundaries correspond to wick extremes, body extremes, or a manually selected teaching zone.
5. The rejected example is marked by a red X, but the exact rejection predicate is not machine-readable from the drawing alone.

### Boundary decision

**No boundary type is source-proven by this slide.**

The visual evidence is compatible with a wick-range non-overlap interpretation, but it is also compatible with a body-based or manually highlighted candle-level interpretation. The rectangle should therefore not be reverse-engineered into a numeric formula merely from its apparent pixel alignment.

## 2. Transcript cross-check

The transcript at approximately 34:14–35:37 says that P-Gap is an easy visual marker for where breakout occurred and describes a case where the relevant high and low do not overlap, producing a gap together with breakout/follow-through. It also describes a second construction where the gap appears on the next candle, while both are treated as the same concept for this strategy.

This gives strong semantic support for:

`P-GAP = breakout-context non-overlap relationship`

but does not specify:

- wick versus body;
- exact candle pair in every construction;
- equality/touch handling;
- minimum gap size;
- tick tolerance;
- a numeric early-trend threshold.

## 3. 38:20–40:20 entry diagram cross-check

The follow-up diagram shows the Spike structure with a horizontal order level, a `Limit` annotation, and an SL/invalidation level. Additional annotations show that an order can be deleted/replaced when the subsequent candle changes the effective stop distance.

The diagram strengthens the following source-aligned semantics:

`correction → pending limit → structural invalidation`

It does **not** prove that the limit price is:

- geometric C;
- the P-Gap boundary;
- the prior candle Low/High in every variant;
- a fixed retracement percentage.

The prior-candle Low/High interpretation remains a strong candidate because it is directly supported by the transcript/official explanation, but the teaching drawing alone does not provide a universal numeric mapping.

## 4. Boundary discrimination matrix

| Candidate | Source transcript | Visual slide | Decision |
|---|---|---|---|
| Wick High → next Low non-overlap | Strongly compatible | Compatible | **Strong candidate, not frozen** |
| Body top → next body bottom | Not explicitly stated | Compatible | Candidate only |
| Wick/body hybrid | Not explicitly stated | Cannot exclude | Candidate only |
| Any visible gap | Contradicted by P-Gap/E-Gap distinction | Contradicted by contextual placement | **Rejected** |
| Generic 3-candle imbalance | Not stated | Not shown as a generic 3-candle rule | **Rejected as canonical** |
| Manually highlighted P-Gap zone | Compatible with drawings | Visually possible | Research hypothesis only |

## 5. Important negative result

The source visual evidence does **not** contain enough information to safely promote `wick-to-wick` into a canonical formula.

This is a successful research result rather than a failure: the primary source has narrowed the family of valid interpretations but has not uniquely resolved the executable boundary.

No backtest result is used to choose among the remaining candidates.

## 6. Freeze rule

P-Gap may only be frozen when at least one of the following becomes available from primary source evidence:

1. an explicit verbal definition of the two boundary prices;
2. a sufficiently precise source diagram where the boundary candles/prices are unambiguous;
3. a second independent source frame/example that disambiguates wick versus body and candle timing;
4. an explicit source example with OHLC values or an order/indicator marking tied to the gap boundary.

Until then:

`SourceConfirmedGap` remains an externally confirmed semantic input in the source-aligned scaffold.

## 7. Current canonical-status table

| Rule | Status |
|---|---|
| P-Gap is required for valid Spike/breakout | SOURCE-CONFIRMED |
| P-Gap is distinct from generic visible gap | SOURCE-CONFIRMED |
| P-Gap marks breakout/early-trend location | STRONG SOURCE EVIDENCE |
| Non-overlap relationship | STRONG SOURCE EVIDENCE |
| Wick High/Low formula | NOT FROZEN |
| Body Open/Close formula | NOT FROZEN |
| Consecutive-candle requirement | NOT FROZEN |
| Equality/touch handling | NOT FROZEN |
| Minimum gap/tick tolerance | NOT FROZEN |
| Generic 3-candle imbalance | REJECTED AS CANONICAL |

## 8. Gate decision

**SOURCE RESOLUTION:** progressing, but P-Gap boundary remains unresolved.  
**FROZEN GEOMETRY:** blocked.  
**DEV:** not authorized.  
**VAL:** untouched.  
**Fresh Holdout:** locked.  
**Production:** unchanged.

## Next action

The next highest-value source task is not backtesting. It is to locate an **explicit numeric/price-linked P-Gap example** in the source material, especially in the real XAUUSD section or any order/indicator frame where the gap zone can be tied to actual OHLC levels. If no such evidence exists, record P-Gap as a source-confirmed semantic prerequisite but keep its executable formula unresolved.
