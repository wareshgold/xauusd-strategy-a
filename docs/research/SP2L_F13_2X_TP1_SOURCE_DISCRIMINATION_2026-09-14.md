# SP2L F13 — 2X / TP1 Source-Discrimination Fixture

Date: 2026-09-14  
Status: SOURCE-DOES-NOT-DISCRIMINATE  
Canonical status: NOT CANONICAL

## Purpose

F13 isolates the unresolved operational meaning of the source's 2X / TP1 concepts without inventing a numerical target formula.

This is a synthetic source-discrimination fixture, not historical evidence, optimization data, or a production rule. Source meaning outranks backtest performance.

## Source-aligned invariants

The source supports a second-position / reward-management concept and expresses TP1 preference in the source material. Related evidence also supports a Leg-2 objective and an approximate Leg-2-to-Leg-1 magnitude relationship. However, the exact executable 2X and TP1 formulas remain unresolved.

## Synthetic cases

Construct a bullish SP2L-like setup with fixed Entry, structural invalidation, Leg 1 magnitude, and a source-consistent pending-Limit correction. Vary only the interpretation of 2X / TP1.

### Case A — half-target interpretation

Interpret 2X as a target/reward-management level corresponding to a defined fraction of the Leg-2 objective, such as a half-target.

No fraction is canonicalized by this fixture; the case exists only to discriminate the semantic possibility.

### Case B — second-position reward-profile interpretation

Interpret 2X as an instruction about the reward profile or management of a second position rather than a direct price-distance multiplier.

### Case C — direct price-multiple interpretation

Interpret 2X as a literal two-times price-distance formula from Entry or another anchor.

This is not accepted merely because the notation contains “2X”. The anchor and exact arithmetic require direct source evidence.

### Case D — AB=CD-derived target

Interpret the operational target through the source-confirmed relationship `Leg2Magnitude ≈ Leg1Magnitude`.

The exact A/B/C/D anchors and tolerance remain unresolved, so this case cannot be converted into a deterministic formula here.

## Source-discrimination questions

1. Does the source explicitly define what “2X” measures?
2. Is 2X a price-distance multiple, a position/reward-management concept, or another source-defined construct?
3. Does the source define the anchor from which 2X is measured?
4. Does it define whether TP1 is at a fixed ratio, a Leg-2/AB=CD objective, or another level?
5. Does it define partial-position sizing or sequencing associated with 2X?
6. Does it define an exact TP1/TP2 numerical formula?

## Adjudication

Current source evidence does not uniquely discriminate the operational interpretation of 2X or the exact TP1/TP2 executable geometry. The safe source-aligned state is therefore:

`SOURCE-DOES-NOT-DISCRIMINATE`

The confirmed semantic concepts may remain documented, but no numeric target formula, anchor, fraction, position-sizing sequence, or tolerance may be promoted to CANONICAL from this fixture.

## Negative controls

Do not invent or promote:

- `TP = Entry + 2R` or `Entry - 2R`;
- a fixed 50% target without direct source confirmation of its operational role;
- a fixed 1:1 or 2:1 target as a universal Strategy A rule;
- arbitrary partial-position percentages;
- an assumed AB=CD A/B/C/D mapping;
- a numerical AB=CD tolerance;
- Fibonacci target substitutions;
- ATR or pip-distance substitutes;
- backtest-selected target formulas.

## Gate impact

- SOURCE RESOLUTION: partial pass; 2X/TP1 operational geometry remains unresolved.
- SYNTHETIC FIXTURES: F13 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for Strategy A target geometry.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

Documentation only. No engine, simulator, replay, or production changes. No backtest/optimization selection. Manual approval by Ali remains required for any future CANONICAL promotion.
