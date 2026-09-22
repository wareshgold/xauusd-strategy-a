# SP2L Correction / Fill / Leg-1 Discriminator — 2026-09-22

## Result of source-first audit

The repository's source-resolution record from 2026-09-09 provides the strongest currently archived discriminator:

- The demonstrated bullish sequence shows the Buy Limit level moving to the latest completed higher-low as structure extends.
- The correction retraces toward that structural level.
- Structural invalidation remains below the original/base low.
- The teacher permits deleting/replacing the prior pending order when a new candle changes the structure and the distance to SL.
- The source does **not** explicitly label the pending fill price as the AB=CD C point.
- The source does **not** uniquely label A/B/C/D with candle-level OHLC coordinates.

## Important separation

The legacy `EntryTrigger.ts` implementation uses a post-correction close reclaim of a correction extreme. That implementation is not evidence that the teacher's Strategy A uses market-close-reclaim execution.

The source-resolution record instead describes a pending Buy Limit construction. Therefore the legacy reclaim detector remains non-canonical and must not be used to infer C or fill semantics.

## Discriminator outcome

| Question | Source result |
|---|---|
| Is Entry necessarily the correction extreme? | **Not universal; source shows dynamic relevant higher-low** |
| Is Entry necessarily the eventual fill price? | **No — fill is execution outcome, not source geometry anchor** |
| Is C necessarily the fill price? | **UNRESOLVED / do not assume** |
| Is C necessarily the correction extreme? | **UNRESOLVED** |
| Are A/B endpoints uniquely labelled? | **UNRESOLVED** |
| Is Leg2 magnitude related to Leg1? | **SOURCE-CONFIRMED** |
| Is exact AB=CD tolerance known? | **UNRESOLVED** |
| Can legacy reclaim logic become canonical? | **NO** |

## Gate decision

This audit does not produce a canonical A/B/C mapping. That is the correct source-first outcome.

The next discriminating evidence needed is a source example where the teacher's first-leg endpoints and correction/entry reference are simultaneously visible or explicitly named. Without that, selecting a mapping would be implementation convention rather than source reconstruction.

## Frozen Geometry

**BLOCKED**

No Strategy A production geometry was changed by this checkpoint.
