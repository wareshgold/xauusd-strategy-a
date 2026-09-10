# SP2L G235 — P-Gap Rejected-Example Negative Evidence

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `NEGATIVE_EVIDENCE_STRENGTHENED_GEOMETRY_STILL_UNRESOLVED`

## Objective

Continue the B1 P-Gap source-resolution pass by examining the explicitly rejected example shown beside the three positive P-Gap examples in the raw SP2L teaching frame around 36:07.

The purpose is to determine whether the rejected example provides negative evidence against the research candidate `High[t-2] < Low[t]`, without reverse-engineering an exact predicate from a low-resolution schematic.

## Raw source observation

The source frame presents four schematic outcomes in one teaching panel:

- a leftmost example marked with a red X;
- three subsequent examples numbered 1, 2, and 3;
- the text `Valid BO = P-Gap` positioned between the rejected and accepted examples.

The three accepted examples contain visibly shaded gap regions. The rejected example does not show the same clearly separated shaded P-Gap region.

In the rejected sequence, the candles form a directional progression, but the visible candle extremes do not provide a clean, unambiguous positive separation equivalent to the shaded regions in the accepted examples. At source resolution, exact OHLC values cannot be recovered.

## Negative-evidence interpretation

The rejected example is consistent with the proposition that **directional movement alone is insufficient** and that a qualifying separation/gap condition is required for the source's `Valid BO = P-Gap` classification.

This is useful negative evidence because it distinguishes:

`directional move`  !=  `valid P-Gap breakout`

However, the frame does not uniquely identify which precise geometric predicate causes rejection.

## Relation to H1

Research hypothesis H1 remains:

`High[t-2] < Low[t]`

The rejected example is visually compatible with H1 failing because the relevant earlier upper extreme and later lower extreme appear not to have the same clean positive separation seen in the accepted examples.

**Important:** this is a compatibility assessment, not an OHLC proof. The image resolution and schematic nature prevent reliable numerical reconstruction of the relevant wick endpoints.

## What this evidence strengthens

1. P-Gap is not simply synonymous with any directional Spike candle.
2. A qualifying gap/separation is materially relevant to the source's valid-breakout classification.
3. The generic Gap candidate remains a strong source-correlated interpretation.
4. The rejected example gives a concrete negative fixture target for future source testing.

## What remains unresolved

The rejected example does not establish:

- exact candle indexing;
- exact wick-versus-body boundaries;
- strict inequality versus equality/touch treatment;
- minimum gap size;
- whether an additional Spike condition is mandatory;
- whether Breakout-Gap context is an additional requirement;
- whether the bearish mirror is exact;
- whether any other SP2L-specific P-Gap condition exists.

## Explicit non-inferences

This pass does not infer:

- `P-Gap = generic Gap` as a frozen production rule;
- `P-Gap = Breakout Gap`;
- `P-Gap = Pressure Gap`;
- `P-Gap = FVG`;
- body-only geometry;
- any tolerance selected from backtest performance;
- any liquidity/BOS/MSS/displacement/retest/session rule.

No historical optimization or profitability result is used to interpret the source.

## Synthetic-fixture implication

The rejected example should be represented as a negative fixture class in the research suite:

**PG-NEG-01 — directional sequence without a qualifying P-Gap separation**

Expected behavior should remain hypothesis-specific:

- H1: expected FAIL if the source-derived endpoint relationship is later confirmed;
- body-only: independently evaluated;
- H2: independently evaluated;
- H3: unresolved until additional source evidence identifies an SP2L-specific condition.

The fixture must not be used to force H1 into production.

## Gate decision

**Source Resolution:** improved through negative evidence, but **BLOCKED at final executable P-Gap geometry**.

**Synthetic Fixtures:** PASS; add PG-NEG-01 as a research target only after its OHLC representation is explicitly defined from source evidence.

**Frozen Geometry:** BLOCKED.

**DEV / VAL / Fresh Holdout / Production:** unchanged and not authorized.

## Next source task

Inspect another independent raw SP2L example where the P-Gap shaded region and the actual candle wicks are simultaneously visible, preferably at a larger source resolution or during a teaching sequence in which the endpoint marks are drawn live. The goal is to resolve whether the positive examples and rejected example share one exact endpoint predicate.
