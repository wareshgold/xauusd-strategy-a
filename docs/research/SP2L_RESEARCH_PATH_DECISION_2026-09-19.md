# SP2L Research Path Decision — Provisional Implementation vs Canonical Strategy — 2026-09-19

## Purpose
Record the distinction between the currently tested research implementation and the source-frozen canonical Strategy A.

## Observed research performance
The bounded parameter study produced positive historical results, including a baseline decisive win rate of 66.883% (103 wins / 51 losses, 4 ambiguous) and +52R. Across 81 bounded combinations, 81/81 had positive Total R and 80/81 exceeded 60% decisive win rate.

These results are evidence that the tested research path is worth investigating further. They do **not** establish that the unresolved source interpretations are correct.

## Decision
The current research implementation may remain available as a **non-canonical research harness** for reproducibility and diagnostics.

It must not be relabeled as the source-frozen Strategy A and must not be used to:
- choose among competing P-Gap/AB=CD/swing/SL/trigger interpretations;
- promote a parameter;
- authorize live BUY/SELL generation;
- unlock Frozen Geometry.

## Research questions for the next phase
Instead of another generic win-rate optimization, the next useful step is to measure whether the observed edge is structurally dependent on the unresolved assumptions.

Required analysis:
1. Map each tested rule/assumption to its source status.
2. Identify which unresolved assumptions materially affect signal count and outcome.
3. Run sensitivity diagnostics only where the implementation already defines a bounded research variant; do not present variants as canonical.
4. Separate source evidence, engineering assumptions, and empirical observations in the report.
5. Preserve the existing frozen configuration and holdout boundary.

## Gate impact
- Frozen Geometry: **BLOCKED**
- Research harness: **ALLOWED**
- Canonical promotion: **BLOCKED**
- Fresh Holdout: **WAITING FOR ELIGIBLE DATA**
- Production: **OFF**

## Principle
A >60% historical win rate is useful evidence of a potentially promising research path, but it cannot resolve source ambiguity. The project therefore continues forward without discarding the empirical result and without converting it into canonical trading rules.
