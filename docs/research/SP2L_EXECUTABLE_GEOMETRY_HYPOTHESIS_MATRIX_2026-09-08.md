# SP2L Executable Geometry Hypothesis Matrix — 2026-09-08

## Status

**RESEARCH ONLY — NON-CANONICAL**

This matrix exists to structure the next synthetic-discrimination phase. It does not select any executable Strategy A geometry and must never be imported into production merely because one hypothesis performs better historically.

## Why this exists

The semantic contract is now frozen, but several executable questions remain unresolved. The source does not provide enough machine-readable geometry to select one formula without risk of invention.

The purpose of this matrix is therefore to compare hypotheses using synthetic fixtures **before** historical performance testing.

## H1 — P-Gap geometry

Candidate interpretations to discriminate:

| ID | Candidate | Status |
|---|---|---|
| PG-01 | Previous candle High/Low to subsequent candle Low/High non-overlap | RESEARCH HYPOTHESIS |
| PG-02 | Candle-body boundary non-overlap | RESEARCH HYPOTHESIS |
| PG-03 | Wick-to-wick highlighted gap zone | RESEARCH HYPOTHESIS |
| PG-04 | Other source-specific manually defined gap zone | RESEARCH HYPOTHESIS |

No candidate is canonical.

## H2 — P-Gap timing

Candidate timing relationships:

| ID | Candidate | Status |
|---|---|---|
| PT-01 | Gap on breakout candle | RESEARCH HYPOTHESIS |
| PT-02 | Gap on follow-through candle | RESEARCH HYPOTHESIS |
| PT-03 | Gap spanning the breakout/follow-through construction | RESEARCH HYPOTHESIS |
| PT-04 | Variant-dependent timing | RESEARCH HYPOTHESIS |

The source explicitly discusses multiple Spike constructions, so a single fixed candle index must not be assumed.

## H3 — Entry geometry

Source semantic contract:

`directional Spike → correction toward previous/relevant Low/High → pending limit`

Competing executable hypotheses:

| ID | Candidate | Status |
|---|---|---|
| EN-01 | Previous/relevant candle Low/High itself | RESEARCH HYPOTHESIS |
| EN-02 | Correction structural boundary identified by source sequence | RESEARCH HYPOTHESIS |
| EN-03 | A source-specific level inside the correction | RESEARCH HYPOTHESIS |
| EN-04 | P-Gap boundary | REJECTED AS CANONICAL; retain only as falsification control |
| EN-05 | Classical harmonic C | REJECTED AS CANONICAL; retain only as falsification control |
| EN-06 | 50% retracement | REJECTED AS CANONICAL BASE ENTRY; retain only as falsification control |

A market close-reclaim is not an equivalent implementation of the pending-limit semantic and must not be used as the canonical entry substitute.

## H4 — Spike-origin / SL geometry

Competing origin candidates:

| ID | Candidate | Status |
|---|---|---|
| OR-01 | First/earliest candle of source-defined Spike movement | STRONGEST SEMANTIC CANDIDATE; NOT FROZEN |
| OR-02 | Breakout candle/level | UNRESOLVED |
| OR-03 | First structural High/Low of the Spike sequence | UNRESOLVED |

Price convention remains unresolved:
- wick extreme;
- body edge;
- source-specific structural boundary;
- buffer/offset.

## H5 — Leg 1 geometry

Competing candidates:

| ID | Candidate | Status |
|---|---|---|
| L1-01 | Spike-origin → Spike-extreme | STRONGEST CURRENT RESEARCH CANDIDATE; NOT FROZEN |
| L1-02 | Breakout level → Spike-extreme | UNRESOLVED |
| L1-03 | First structural High/Low → Spike-extreme | UNRESOLVED |

The source-confirmed invariant is only:

`Leg 2 magnitude ≈ Leg 1 magnitude` and explicitly `AB = CD`.

The exact equality tolerance is unresolved.

## H6 — Leg 2 projection anchor

Competing candidates:

| ID | Candidate | Status |
|---|---|---|
| L2-01 | Correction entry/fill price ± Leg 1 magnitude | RESEARCH HYPOTHESIS |
| L2-02 | Source-defined correction structural point ± Leg 1 magnitude | RESEARCH HYPOTHESIS |
| L2-03 | Classical C ± AB | REJECTED AS CANONICAL IMPORT |

No projection formula is canonical until the source anchor is resolved.

## Synthetic discrimination protocol

For each unresolved question:

1. Construct the smallest OHLC fixture that makes two candidates produce different outputs.
2. Hold all unrelated properties constant.
3. Record each candidate's output without judging profitability.
4. Compare against source visual/textual evidence.
5. If source evidence still cannot discriminate, retain both as unresolved.
6. Never choose the candidate because it backtests better.

Required outputs for each fixture:

- fixture ID;
- OHLC sequence;
- candidate interpretations tested;
- predicted P-Gap;
- predicted Entry;
- predicted SL/origin;
- predicted Leg 1;
- predicted Leg 2 target;
- source evidence that could discriminate;
- result: ACCEPT / REJECT / UNRESOLVED.

## Explicit prohibition

This matrix must not be converted into a single Strategy A implementation by parameter optimization. A geometry hypothesis remains a hypothesis until source evidence resolves it.

## Gate

`SYNTHETIC FIXTURES = OPEN`

`FROZEN GEOMETRY = BLOCKED`

`DEV / VAL / ROBUSTNESS / HOLDOUT / PRODUCTION = LOCKED`
