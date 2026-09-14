# SP2L Frozen-Geometry Contract — 2026-09-14

## Purpose

This contract is the boundary between source-resolution research and deterministic-engine development.
It freezes only what the authoritative SP2L source supports at semantic level. It does **not** promote unresolved price geometry into Strategy A.

The governing rule is:

> Source meaning outranks backtest performance. No unresolved geometry may become canonical because it improves a test result.

## Evidence basis

Primary textual evidence is the timestamped SP2L transcript artifact `پورصمدیSP2L TRANSCIBE.txt`, cross-resolved against the source video. The transcript confirms the following concepts, while exact OHLC geometry still requires source discrimination where noted.

## SOURCE_CONFIRMED_SEMANTICS

- SP2L is organized around a Spike → correction → Second Leg sequence.
- Breakout is described through a close followed by a follow-through candle that does not return/overlap the prior area; P-GAP is presented as a sign associated with a valid breakout.
- The source distinguishes P-GAP from E-GAP.
- Two observed P-GAP orderings are treated as the same strategy family in the source material.
- The source discusses one-, two-, and three-candle structural/trend constructions; the exact acceptance classifier is not fixed.
- Correction is a distinct phase and a corrective/pending Buy Limit can be placed during the early correction sequence.
- A return to the cited lower/higher structural level can invalidate the scenario; the exact price boundary is unresolved.
- Stop-loss is structurally associated with the candle from which the spike originated; the exact OHLC/wick/body boundary is unresolved.
- A secondary/2X position and TP1/TP2 are source concepts; their complete executable formulas are unresolved.
- The source describes Leg 2 as matching Leg 1 in magnitude at candle/price-action level; exact A/B/C/D anchors and equality tolerance are unresolved.
- Bearish examples exist and demonstrate a directional counterpart, but the deterministic bearish mirror is unresolved.

## FROZEN_FOR_ENGINE

The following may be frozen now as **semantic contracts only**:

1. State sequence vocabulary: `SPIKE → CORRECTION → LEG_2`.
2. Breakout/follow-through and P-GAP may be represented as source-level evidence states, without an invented P-GAP formula.
3. P-GAP and E-GAP must remain distinct labels.
4. Entry, structural invalidation, and risk stop must remain separate concepts.
5. Leg-2 magnitude may be represented as a measured quantity that can be compared with Leg-1 magnitude, without freezing an anchor or tolerance.
6. Bullish and bearish direction are distinct states; no automatic sign-inversion rule is implied.
7. Research fixtures may assert these relationships and must preserve unresolved fields explicitly.

No numeric price anchor, candle index, tolerance, buffer, fill rule, or execution threshold is frozen by this contract.

## UNRESOLVED — MUST REMAIN UNRESOLVED

| Dimension | Required discriminator before canonicalization |
|---|---|
| P-GAP geometry | Exact OHLC fields and candle indexing/boundaries for the source's P-GAP |
| Entry anchor | Exact corrective entry price and its candle/level mapping |
| Leg-2 start | Exact boundary separating entry from Leg-2 origin |
| Structural invalidation | Exact OHLC/wick/body boundary for spike-origin invalidation |
| Pending refresh | Exact deterministic retain/replace/delete condition and threshold |
| Trigger classifier | Exact acceptance logic across 1/2/3-candle constructions |
| AB=CD anchors | Exact A/B/C/D source anchors and equality/tolerance rule |
| 2X / TP1 / TP2 | Exact executable formulas, sequencing, and any source-defined constraints |
| Bearish mirror | Exact deterministic bearish geometry and execution mapping |

These are not implementation TODOs to be solved by inference. They are evidence blockers.

## FORBIDDEN_INFERENCE

The following are explicitly prohibited from becoming canonical without Tier-1/Tier-2 source evidence:

- Substituting a generic three-candle imbalance definition for the source's P-GAP.
- Choosing wick, body, structural-pivot, or mixed A/B/C/D anchors by convention or backtest performance.
- Importing internet-standard Fibonacci/AB=CD definitions when the source has not specified those anchors.
- Inventing equality tolerances, point/pip buffers, spread adjustments, or execution offsets.
- Assuming a candle index or close/high/low boundary that is not source-discriminated.
- Treating a visually convenient level as the canonical entry level.
- Converting a source illustration into a universal order-fill or intrabar semantics without evidence.
- Assuming the bearish rule is simply the bullish rule with signs inverted.

## FIXTURE_RULE

Synthetic fixtures are allowed to test interpretation boundaries, invariants, and evidence-state integrity. They must **not** select among unresolved geometric candidates.

A valid fixture may:

- prove that unresolved fields are represented as unresolved;
- prove that source-confirmed semantic relationships remain stable;
- compare explicitly named hypotheses as hypotheses;
- fail closed when a caller attempts to mark an unresolved geometry field canonical.

A fixture must not:

- choose a production trigger;
- choose an AB=CD anchor model;
- choose a Leg-2/TP formula;
- encode a guessed P-GAP formula;
- encode fill semantics, thresholds, or buffers that the source does not define.

## PROMOTION_GATE

A geometry field can move from `UNRESOLVED` to canonical only when all of the following are true:

1. A Tier-1/Tier-2 source artifact provides a discriminator that uniquely supports the field's meaning.
2. The discriminator is documented with timestamp/frame evidence where applicable.
3. Competing interpretations are recorded and rejected for a source-grounded reason.
4. Manual research approval explicitly promotes the field.
5. Only after promotion may deterministic engine behavior consume that field.

Backtest performance, statistical convenience, implementation simplicity, or symmetry alone can never satisfy the promotion gate.

## Current gate state

`SOURCE_RESOLUTION_STOPPED_PENDING_NEW_TIER1_TIER2_DISCRIMINATOR`

Therefore this contract establishes **Frozen-Geometry Readiness**, not a frozen production geometry.
