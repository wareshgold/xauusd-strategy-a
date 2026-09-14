# SP2L F14 — AB=CD Anchor Source-Discrimination Fixture

Date: 2026-09-14  
Status: SOURCE-DOES-NOT-DISCRIMINATE  
Canonical status: NOT CANONICAL

## Purpose

F14 isolates the unresolved A/B/C/D anchor selection and equality tolerance behind the source-confirmed AB=CD relationship.

This is a synthetic source-discrimination fixture, not historical evidence, optimization data, or a production rule. Source meaning outranks backtest performance.

## Source-aligned invariant

The source confirms the conceptual relationship that the second leg is approximately equal in magnitude to the first leg: `Leg2Magnitude ≈ Leg1Magnitude`.

The source does not currently provide enough explicit evidence to freeze a universal four-point A/B/C/D candle-index algorithm or a numerical equality tolerance.

## Synthetic cases

Construct a bullish SP2L sequence containing:

1. context/range;
2. directional Spike and breakout/follow-through;
3. correction and pending-Limit entry;
4. a measurable first leg;
5. a second-leg continuation with a visually plausible completion.

Hold the market sequence constant while testing competing anchor interpretations.

### Candidate A — structural swing anchors

Select A/B/C/D from source-relevant structural swing points surrounding the Spike, correction, and second leg.

### Candidate B — Spike-origin / Spike-extreme anchors

Use the Spike-origin and Spike-extreme as one or more AB anchors, with the correction point supplying C and the projected continuation supplying D.

### Candidate C — Entry-as-C anchor

Treat the executable Entry as C.

This is a candidate only; the source has not established that Entry universally equals C.

### Candidate D — candle-index / close-based anchors

Select A/B/C/D from fixed candle indices or close prices rather than structural extrema.

No such fixed indexing or close-only rule may be assumed without direct evidence.

### Candidate E — arbitrary Fibonacci/ratio substitution

Replace AB=CD with a Fibonacci percentage or another ratio.

This is a negative control and is not source-authorized.

## Source-discrimination questions

1. Which exact source points are A and B?
2. Which exact source point is C?
3. Is C always Entry, the correction low/high, or another structural point?
4. Which exact point defines D?
5. Are anchors candle extrema, body values, closes, or another source-defined field?
6. Is AB=CD exact, approximate, or visually qualitative?
7. If approximate, does the source define a numerical tolerance?
8. Does the same anchor taxonomy apply bullish and bearish?

## Adjudication

Current source evidence discriminates the **magnitude relationship** but not the executable anchor algorithm.

Safe conclusion:

- `Leg2Magnitude ≈ Leg1Magnitude` = source-confirmed semantic relationship.
- A/B/C/D exact anchors = unresolved.
- Candle-index / OHLC-field semantics = unresolved.
- Equality tolerance = unresolved.

Therefore F14 remains:

`SOURCE-DOES-NOT-DISCRIMINATE`

No candidate may be selected because it produces better historical performance.

## Negative controls

Do not invent or promote:

- `C = Entry` as a universal rule;
- arbitrary Spike-origin/extreme anchors;
- fixed candle-index anchors;
- close-only or body-only anchors without source evidence;
- Fibonacci substitutions;
- a numeric AB=CD tolerance;
- pip/tick/percentage tolerances;
- backtest-selected anchors or tolerances.

## Gate impact

- SOURCE RESOLUTION: partial pass; AB=CD magnitude relationship established, executable anchor geometry unresolved.
- SYNTHETIC FIXTURES: F14 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for Strategy A AB=CD geometry.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

Documentation only. No engine, simulator, replay, or production changes. No backtest/optimization selection. Manual approval by Ali remains required for any future CANONICAL promotion.
