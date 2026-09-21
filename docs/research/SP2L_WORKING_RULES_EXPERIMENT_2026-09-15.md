# SP2L Working-Rules Experiment — 2026-09-15

## Purpose

Define a bounded, non-canonical research experiment using the project owner's current Working Rules. This document does **not** freeze Strategy A geometry, does not resolve source ambiguity, and does not authorize production BUY/SELL decisions.

## Governance status

- Mode: research / observation-only
- Canonical Strategy A geometry: **NOT FROZEN**
- Production signal generation: **LOCKED**
- Backtest performance must not be used to decide source meaning.
- C03, C07, and C08 remain unresolved unless the project owner explicitly adjudicates them.

## Current human/source adjudication baseline

| Candidate | Status | Current interpretation |
|---|---|---|
| C01 P-Gap | SOURCE_DISCRIMINATED | Source explicitly distinguishes P-GAP from common GAP and labels Valid BO = P-Gap. Exact OHLC boundary/candle indexing remains outside this experiment. |
| C02 SL / RR | WORKING_FIXED_TEST_RULE | Initial SL hypothesis: 50–80 pips; test RR 1:2. This is a project-owner working hypothesis, not source-canonical geometry. |
| C03 Leg equality | REMAINS_BLOCKED | Do not require Leg2 magnitude to equal Leg1 as a canonical rule. |
| C04 Targets / 2X | SOURCE_DISCRIMINATED | Source visually establishes Entry/SL/TP1/TP2 and a 2X concept; exact executable formulas remain unresolved. |
| C05 Market direction | WORKING_FIXED_TEST_RULE | M15 price relative to MA50 is the current working market-direction filter. It is a test hypothesis, not source-canonical meaning. |
| C06 Pending behavior | SOURCE_DISCRIMINATED | Source shows deletion behavior for a pending order; exact deterministic timing/condition remains unresolved. |
| C07 Trigger family | REMAINS_BLOCKED | No canonical trigger classifier. |
| C08 Correction/invalidation | REMAINS_BLOCKED | No canonical correction/invalidation boundary. |

## Experiment boundary

The experiment may measure how the two Working Rules (C02 and C05) affect outcomes **only after a candidate setup has been independently identified by source-safe, explicitly available evidence**.

It must not invent missing P-Gap geometry, entry anchors, invalidation boundaries, trigger conditions, fill semantics, buffers, thresholds, candle indexing, or bearish mirror rules.

Where an unresolved field is required to produce an executable trade, the candidate must be marked `UNRESOLVED / NO TRADE` rather than guessed.

## Risk hypothesis

C02 test matrix:

- Stop-loss working range: 50–80 pips.
- Primary target assumption for this experiment: RR = 1:2.
- Evaluate each stop value/range separately; do not silently select the best value and call it canonical.
- Report sensitivity across the range rather than optimizing for the highest result.

This is exploratory risk research only. It does not replace the source-described structure-based SL requirement.

## Context hypothesis

C05 test matrix:

- Timeframe: M15.
- Direction filter: price relative to MA50.
- Bullish candidate context: price above M15 MA50.
- Bearish candidate context: price below M15 MA50.

The exact MA50 calculation convention must be recorded by the data/engineering layer before any numerical experiment. If convention is not frozen, results must be labeled implementation-sensitive.

## Required data contract

Before statistical measurement:

1. Raw XAU/USD M1 data must be immutable and provenance-tracked.
2. M5/M15 candles must be deterministically derived from the raw series where applicable.
3. Timezone/session convention must be explicit.
4. Missing/duplicate/out-of-order candles must be audited.
5. No future candles may influence a candidate at its decision timestamp.
6. The dataset split must be defined before results are inspected.

The repository's current data principle identifies Twelve Data XAU/USD as the initial research candidate, with M1 as raw source of truth and higher bars derived locally where practical.

## Measurement plan

For every source-safe candidate that reaches the experiment boundary, record at minimum:

- timestamp
- timeframe
- direction
- entry representation, only if source-safe and explicitly available
- SL representation and whether it is working-rule-derived
- TP1 / RR representation
- M15 MA50 value and side
- outcome in R
- reason for exclusion, if excluded
- unresolved fields
- provenance/version identifier

Primary descriptive metrics:

- number of candidates
- win rate
- average R
- expectancy
- profit factor
- maximum drawdown
- average winner / loser
- consecutive losses
- outcome distribution by 50–80 pip setting
- outcome distribution by M15 MA50 context

No parameter optimization is permitted in this phase.

## Acceptance discipline

A positive result does **not** promote C02 or C05 to source-canonical status.
A weak result does **not** disprove the source concept.
A result can only inform whether the Working Rule should remain a useful research hypothesis.

Canonical promotion still requires source resolution and the separate frozen-geometry decision gate.

## Next gate

1. Verify/ingest research data under the data contract.
2. Verify that an independently source-safe candidate set exists.
3. Run the experiment without lookahead or parameter optimization.
4. Produce descriptive statistics and failure analysis.
5. Keep C03/C07/C08 blocked.
6. Do not enter canonical freeze or production development from this experiment alone.
