# SP2L Research Gate — P-Gap Hypothesis Stage — 2026-09-08

## Gate purpose

Record the transition from semantic freeze into controlled synthetic geometry research.

## Completed in this stage

1. Frozen semantic contract encoded as `SP2L_SEMANTIC_CONTRACT_VERSION = 2026-09-08.v1`.
2. Research-only P-Gap hypothesis evaluators isolated outside the production domain.
3. Synthetic discrimination tests added for adjacent/three-candle and wick/body candidate families.
4. Exact-touch behavior is represented as a hypothesis property only; it is not source-confirmed.
5. Bullish and bearish mirror behavior is covered.

## Candidate status

| Candidate | Status |
|---|---|
| H1 adjacent wick gap | RESEARCH HYPOTHESIS |
| H2 three-candle outer wick gap | RESEARCH HYPOTHESIS |
| H3 adjacent body gap | RESEARCH HYPOTHESIS |
| H4 three-candle outer body gap | RESEARCH HYPOTHESIS |
| Generic FVG = P-Gap | REJECTED AS CANONICAL |

## What synthetic tests can establish

- whether two candidate definitions are mathematically distinct;
- which fixture shapes cause candidate disagreement;
- whether bullish/bearish implementations are exact mirrors;
- whether an implementation accidentally treats equality as a strict gap.

## What synthetic tests cannot establish

They cannot determine which candidate matches the source unless the source artifact itself discriminates that case. They also cannot establish profitability or production suitability.

## Historical research gate

LOCKED. No DEV/VAL/Holdout backtest may use one of these candidates as if it were canonical Strategy A.

## Next gate

Construct the same type of discriminating fixture matrix for:

- entry-level identity;
- structural invalidation / SL price;
- Leg-1 anchors;
- AB=CD projection tolerance.

The source-aligned semantic constraints must remain fixed while those executable geometries remain unresolved.

## User action

No pull/run is required yet. A local test run will be requested only when a combined research branch is ready for verification.
