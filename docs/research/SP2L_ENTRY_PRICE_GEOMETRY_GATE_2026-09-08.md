# SP2L Entry Price Geometry Gate — 2026-09-08

## Objective

Resolve the exact executable pending-limit price without promoting an invented candle index, wick/body convention, or management rule to Strategy A.

## Source-confirmed semantic baseline

The primary source video establishes that the base entry is a pending limit placed during correction. In the bullish example, correction is described by price moving below the first/relevant Low; the bearish case is mirrored around the relevant High. The source also states that the order can be prepared before activation and that there is no requirement to wait for a later candle close/reclaim.

This gate therefore treats the following as fixed semantic constraints:

`SPIKE → CORRECTION → PENDING LIMIT → FILL`

and rejects using a later last-Spike-candle breakout/reclaim as the canonical entry trigger.

## Candidate executable interpretations

The fixture matrix intentionally separates:

1. previous/relevant candle extreme;
2. first correction candle extreme;
3. Spike-origin candle extreme;
4. previous/relevant candle body edge;
5. first correction candle body edge.

These are hypotheses only. The matrix does not select a winner.

## Discrimination fixtures

The fixtures deliberately make candidate anchors numerically/structurally distinct in principle:

- BUY and SELL mirrored cases with all candidate extremes separated;
- wick-vs-body cases where the previous candle's extreme differs from its body edge;
- a multi-candle correction where a later correction candle makes a new extreme.

The purpose is to ensure future source annotations can eliminate hypotheses rather than merely confirming cases where all hypotheses agree.

## Current evidence assessment

The source wording strongly favors a previous/relevant Low/High semantic reference, but the visual material reviewed so far does not uniquely establish:

- exact candle identity in every Spike variant;
- wick vs body edge;
- whether the level is fixed at first recognition or can be revised as correction evolves;
- exact fill semantics when price touches/crosses the pending level;
- any buffer or offset.

Therefore the executable entry price remains **UNRESOLVED**.

## Guardrails

- Do not set `entryPrice = geometric C`.
- Do not set `entryPrice = P-Gap boundary`.
- Do not set `entryPrice = 50% retracement`.
- Do not replace pending-limit semantics with market close-reclaim.
- Do not choose the most profitable hypothesis using historical data.
- Do not enter DEV/VAL/Fresh Holdout with an unresolved geometry assumption.

## Next source-resolution action

Inspect the clearest real trade examples from the primary video at the moment the limit is drawn and at the first activation. For each example, record the candidate previous/relevant candle, its wick/body boundaries, the correction candle, the order line, and the activation candle. Only a repeated source-consistent relationship may advance a hypothesis from unresolved to source-confirmed.

## Gate status

- Pending-limit semantic: **SOURCE-CONFIRMED**
- Previous/relevant Low/High semantic: **SOURCE-CONFIRMED SEMANTIC**
- Exact entry candle identity: **UNRESOLVED**
- Wick/body convention: **UNRESOLVED**
- Fixed-vs-revised order level: **UNRESOLVED**
- Fill/touch semantics: **UNRESOLVED**
- Exact entry price formula: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- Historical optimization: **LOCKED**
- Production: **UNCHANGED**
