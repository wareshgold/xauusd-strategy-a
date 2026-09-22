# SP2L Strategy A — Research Candidate V0.1 — P-Gap + SL Test Boundary — 2026-09-22

## Purpose

This branch is a **research candidate only**. It exists to test the two remembered source-aligned areas (P-Gap and Spike-origin SL) without changing canonical Strategy A geometry.

It does **not** unlock Frozen Geometry, Untouched Validation, Fresh Holdout, or Production.

## Candidate under test

### P-Gap candidate

The current author-replica research implementation uses:

- BUY: `correction.low > A.high + 1.0`
- SELL: `correction.high < A.low - 1.0`

The `1.0` value is retained only as a **candidate parameter**. It is not declared source-confirmed.

### SL candidate

The current author-replica research implementation uses the Spike candle directional extreme:

- BUY: `SL = spike.low`
- SELL: `SL = spike.high`

This is supported by the source concept that the stop/invalidation reference is associated with the candle from which the Spike originated, and by author-implementation cross-confirmation. Exact wick/body/buffer and invalidation-event semantics remain unresolved.

## Intentionally unchanged

- No canonical P-Gap formula, fixed indexing, equality rule, or boundary rule.
- No canonical Entry/Fill rule.
- No canonical pending-order refresh rule.
- No canonical F14 A/B/C/D or tolerance rule.
- No production BUY/SELL logic.
- No source meaning selected from historical performance.

## Test status

The existing research runner already exposes the candidate parameters through `SP2L_P_GAP_PRICE`, `SP2L_SPIKE_MULTIPLIER`, `SP2L_MAX_SL_DISTANCE`, and `SP2L_TP_R`. Therefore no canonical implementation change is required merely to test this candidate.

## Required experiment

Record signal count, decisive win/loss/ambiguous counts, win rate, total R, profit factor, weekly breakdown, parameter perturbation, and exact signal-set delta versus the existing research baseline.

Treat all results as **descriptive research evidence**, not source resolution.

## Promotion rule

A candidate becomes canonical only after a new auditable primary-source artifact uniquely specifies the disputed geometry. Performance cannot promote it.

## Current gate

- Source Resolution: PARTIAL
- Synthetic Fixtures: PASS
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF
