# SP2L Last-Spike-Candle Breakout Hypothesis — 2026-09-08

## Objective

Discriminate the secondary implementation hypothesis that SP2L entry requires a breakout/reclaim of the last Spike candle against the source-video semantic model of a pending-limit order during correction.

## Hypothesis under test

**H-LSCB:** after a valid Spike and correction, entry requires a subsequent breakout/reclaim of the last Spike candle in the Spike direction.

This hypothesis is secondary corroboration only. It is not a canonical Strategy A rule.

## Source baseline

The source video explicitly demonstrates placing a manual or pre-set limit order during correction, with the bullish correction reference described around the previous/relevant Low and the bearish mirror around the previous/relevant High. Therefore a correction-without-reclaim scenario is materially discriminative: the source semantics can make the pending order available before a later reclaim event.

## Synthetic discrimination matrix

| Fixture | Source pending-limit semantics | H-LSCB | Value |
|---|---|---|---|
| LSCB-BUY-CORRECTION-NO-RECLAIM | ENTRY_AVAILABLE | NOT_TRIGGERED | HIGH |
| LSCB-BUY-CORRECTION-THEN-RECLAIM | ENTRY_AVAILABLE | TRIGGERED | HIGH |
| LSCB-SELL-CORRECTION-NO-RECLAIM | ENTRY_AVAILABLE | NOT_TRIGGERED | HIGH |
| LSCB-SELL-CORRECTION-THEN-RECLAIM | ENTRY_AVAILABLE | TRIGGERED | HIGH |
| LSCB-BOTH-AGREE | ENTRY_AVAILABLE | TRIGGERED | LOW |

## Interpretation

The high-value fixtures demonstrate that the two interpretations are not equivalent:

- A pending-limit interpretation can make an order available during correction even when no later last-Spike-candle reclaim occurs.
- H-LSCB cannot trigger in that same event sequence.
- Bullish and bearish mirrors are both required.
- Agreement cases are low-value for discrimination because they cannot distinguish the hypotheses.

## Gate decision

**H-LSCB remains a SECONDARY RESEARCH HYPOTHESIS.**

The synthetic tests establish that it is a distinct executable interpretation, not that it is the source rule.

No historical optimization or profitability comparison is permitted to promote H-LSCB to canonical Strategy A.

## Required evidence for promotion

Promotion would require first-party evidence showing that the source's pending-limit order is contingent on a subsequent last-Spike-candle breakout/reclaim, or an equivalent authoritative executable specification.

Absent that evidence, the source-aligned semantic contract remains the authority.

## Production impact

None. No production Strategy A logic is changed.
