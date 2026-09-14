# SP2L F8 — Entry Anchor Source-Discrimination Fixture

Date: 2026-09-14
Status: SOURCE-DOES-NOT-DISCRIMINATE
Canonical status: NOT CANONICAL

## Purpose

F8 isolates the unresolved executable rule for the correction-entry price in the source-aligned SP2L model.

This is a synthetic source-discrimination fixture. It is not historical evidence, optimization data, or a production execution rule.

## Source-aligned invariants

The current source evidence supports all of the following:

- correction is the entry phase;
- execution is a pending Limit, not a mandatory market-close/reclaim replacement;
- Entry is distinct from the start of Leg 2;
- Entry is distinct from structural invalidation;
- the demonstrated bullish example associates the pending Buy Limit with a currently relevant higher-low while deeper/base invalidation remains separate;
- later structure can change the actionable reference before fill.

The source does not yet provide a universal candle-index/OHLC algorithm for converting those semantics into one executable Entry price.

## Synthetic case

Construct a bullish SP2L sequence containing:

1. Spike and source-valid breakout/follow-through;
2. an initial structural low after the Spike;
3. at least two subsequent completed higher-lows before correction;
4. a pending Buy Limit candidate before the final correction;
5. a deliberately separated Leg-2 start price;
6. a deeper structural invalidation/base low below the candidate entry levels.

Create the mirrored bearish research case only if direct source evidence later supports it. Do not assume sign symmetry.

## Competing interpretations

### Candidate A — immutable first/base correction low

Entry remains tied to the first qualifying low created after the Spike.

### Candidate B — latest completed relevant higher-low

Entry follows the most recent completed higher-low that remains structurally relevant immediately before correction.

### Candidate C — generic swing-low algorithm

Entry is the output of an independently defined swing detector, regardless of the source's Spike/correction structure.

This is a negative-control candidate unless the source explicitly defines such a detector.

### Candidate D — Leg-2 start

Entry is placed at the point where Leg 2 begins.

This is a negative-control candidate because source evidence already separates Entry from Leg-2 start.

### Candidate E — market-entry reclaim/close

The pending Limit is replaced by market entry on a candle close or reclaim.

This is a negative-control candidate because the source confirms pending-Limit correction execution.

## Source-discrimination questions

1. Is the first/base low immutable after the order is created?
2. Does the actionable Entry reference move to a newer completed higher-low as structure develops before fill?
3. What makes a low/high "relevant" in the source's own terms?
4. Which candle index is the anchor in every demonstrated variant?
5. Which OHLC field supplies the executable price?
6. Does the source require the same rule for every bullish construction?
7. Does a bearish construction have independently sufficient evidence?
8. Can Entry ever equal the Leg-2 start?
9. Can pending execution be replaced by market entry?

## Current adjudication

The source discriminates against Candidate D at the semantic level: Entry and Leg-2 start must remain separate.

The source discriminates against Candidate E: pending-Limit correction execution is retained as the execution model.

The visual/transcript evidence strongly supports Candidate B for the demonstrated bullish variant: the pending Buy Limit reference becomes associated with the currently relevant higher-low while deeper structural invalidation remains separate. However, the available evidence does not establish a universal candle-level definition of "relevant" or prove that the latest higher-low rule applies across all source variants.

The evidence also does not uniquely determine the executable OHLC field or exact candle index for Entry.

Therefore the deterministic universal entry rule remains:

`SOURCE-DOES-NOT-DISCRIMINATE`

## Negative controls

Do not promote:

- `Entry = latest swing low/high` as a universal algorithm;
- `Entry = first low/high` as a universal immutable rule;
- `Entry = Leg-2 start`;
- `Entry = structural invalidation`;
- market-entry-on-close/reclaim;
- Fibonacci percentage substitution;
- arbitrary wick/body selection;
- arbitrary tick/pip buffer;
- a backtest-selected entry anchor;
- an assumed bearish sign-flip mirror.

## Gate impact

- SOURCE RESOLUTION: **partial pass — Entry semantics materially narrowed**.
- SYNTHETIC FIXTURES: **F8 defined and adjudicated**.
- FROZEN GEOMETRY: **BLOCKED**.
- DEV: **LOCKED for Strategy A geometry**.
- UNTOUCHED VALIDATION: **LOCKED**.
- ROBUSTNESS/STABILITY: **LOCKED**.
- FRESH HOLDOUT: **LOCKED**.
- PRODUCTION: **LOCKED**.

## Reopen condition

F8 can move beyond unresolved status only if a Tier 1/2 source artifact explicitly discriminates the universal relevant-low/high rule and its executable price anchor, including the candle/OHLC semantics required for deterministic implementation.

## Governance

No engine implementation, optimization, historical tie-breaking, validation promotion, or canonicalization is authorized by this fixture. Manual canonical approval by Ali remains mandatory.
