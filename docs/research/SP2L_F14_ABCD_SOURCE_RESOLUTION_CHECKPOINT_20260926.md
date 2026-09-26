# SP2L F14 AB=CD Source Resolution Checkpoint — 2026-09-26

## Scope

This checkpoint isolates what the primary SP2L material actually establishes about AB=CD / the two-leg relationship. It does not define executable A/B/C/D anchors from convention, visual estimation, or backtest performance.

## Primary transcript evidence

The primary SP2L transcript states:

- 36:15: SPIKE-2LEG and the concept of 2Leg / AB=CD are explicitly linked.
- 36:31–36:46: the instructor contrasts the classical A/B/C/Fibonacci treatment with the SP2L approach, saying the strategy works at candle-level detail.
- 36:59–37:08: after a Spike and correction, the expectation is that Leg 2 completes and Leg 1 and Leg 2 are equal.
- 37:57: the instructor repeats that after the directional move and correction, the next leg is expected to be the same size.

The primary source therefore confirms the magnitude relationship, not a machine-readable candle-index formula.

## Visual evidence ledger

The preserved visual evidence for 36:30–37:26 records:

1. first directional leg from a lower structural point to an upper structural point;
2. correction toward a lower structural point;
3. second directional leg continuing from that correction;
4. second leg approximately equal in magnitude to the first.

The same visual evidence contains 1M/5M annotations.

A later bearish example at approximately 1:02:41–1:04:32 is structurally consistent with the mirrored Leg 1 -> Correction -> Leg 2 construction.

## What is source-confirmed

- SP2L has a two-leg structure.
- The second leg is expected to match the first leg in magnitude.
- AB=CD is the source's named conceptual analogy for this relationship.
- The construction is expressed at candle/structural level rather than requiring a classical Fibonacci-only representation.
- Bullish and bearish examples support the existence of a directional mirror.

## What remains unresolved

The source does not yet establish:

- exact A anchor;
- exact B anchor;
- exact C anchor;
- exact D anchor;
- whether anchors are wick extremes, candle bodies, opens, closes, or structural swing points represented by another field;
- whether A/B/C/D refer to individual candles or structural turning points that may span multiple candles;
- exact equality semantics;
- numerical tolerance;
- whether D is the TP1 point, a projected point, or merely the completion of the second leg;
- interaction between AB=CD and the separate entry/SL/P-Gap rules.

## Candidate interpretations — research labels only

The following are explicitly hypotheses, not canonical rules:

- H1: structural swing-point extremes;
- H2: candle wick extremes at selected structural candles;
- H3: candle body endpoints;
- H4: open/close-derived leg endpoints;
- H5: mixed structural anchors.

No hypothesis is promoted by performance.

## Synthetic discrimination fixtures

The next fixture layer should test only source discrimination:

- F14-001: exact equal structural legs;
- F14-002: unequal structural legs;
- F14-003: equal wick distance but unequal body distance;
- F14-004: equal body distance but unequal wick distance;
- F14-005: equal leg distance under one anchor convention but not another;
- F14-006: same geometry with multi-candle swing formation;
- F14-007: bearish mirror;
- F14-008: equality boundary / tolerance perturbation.

Expected use: expose which source evidence would be required to distinguish the hypotheses. Fixture outcomes must not choose the canonical anchor.

## Gate

F14 concept: SOURCE-CONFIRMED

F14 magnitude relationship: SOURCE-CONFIRMED

F14 A/B/C/D anchors: UNRESOLVED

F14 equality tolerance: UNRESOLVED

F14 executable TP projection: UNRESOLVED

Frozen Geometry: BLOCKED

Untouched Validation: LOCKED

Fresh Holdout: LOCKED

Production: DISABLED

## Source escalation path

A further video pass is justified only if the original video frames can be inspected at the relevant timestamps with enough resolution to identify explicit A/B/C/D labels or unambiguous structural endpoints. A transcript alone cannot settle wick/body/index semantics.

If high-resolution source frames still contain no explicit anchor definition, F14 should be recorded as a source ceiling rather than resolved by inference.

## Non-negotiable boundary

Do not use a conventional AB=CD definition, Fibonacci convention, current code, or backtest performance to select A/B/C/D anchors or tolerance.
