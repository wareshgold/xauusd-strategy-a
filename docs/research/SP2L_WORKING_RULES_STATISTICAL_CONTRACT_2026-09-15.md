# SP2L Working-Rules Statistical Contract — 2026-09-15

## Status

**PRE-REGISTRATION / NON-CANONICAL**

This document defines how exploratory results must be reported. It does not define Strategy A geometry or execution semantics.

## Frozen analysis principles

1. The audited dataset fingerprint is immutable for a given run.
2. Candidate detection parameters are frozen before outcome inspection.
3. C02 SL values are reported independently at 50/60/70/80 pips.
4. RR is fixed at 2.0R.
5. C05 is fixed at M15/MA50.
6. No parameter search, ranking, or selection by realized performance is permitted.
7. Unresolved geometry produces `UNRESOLVED`, never an inferred label.
8. No production signal is emitted.

## Required metrics

For each pre-declared SL point, report:

- N candidate observations
- N resolved outcomes
- N unresolved/excluded outcomes by reason
- wins
- losses
- timeouts/other resolved outcomes if the frozen outcome protocol permits them
- win rate
- mean R
- expectancy in R
- profit factor when both gross profit and gross loss are defined
- maximum drawdown in R when a deterministic chronological equity series exists

## Statistical uncertainty

The first exploratory run must report point estimates together with an explicitly chosen uncertainty method. The method must be declared before viewing results and must not be selected after observing which method looks favorable.

No claim of statistical significance or proven edge is permitted merely from a positive point estimate.

## Multiple-parameter discipline

The four SL values form a sensitivity grid. They are not four independent chances to select a winning configuration. The report must show all four values side by side and preserve the fact that the grid was pre-declared.

## Holdout boundary

The current audited week is exploratory data only. It must not be presented as an untouched validation or fresh holdout. Any later holdout must be designated before it is inspected for performance.

## Required conclusion vocabulary

Allowed:

- `DATA_AUDITED`
- `EXPLORATORY_RESULT_AVAILABLE`
- `EXPLORATORY_RESULT_INCONCLUSIVE`
- `UNRESOLVED_LABELS_PRESENT`
- `NO_EDGE_CLAIM`
- `REQUIRES_LARGER_DATA`

Disallowed:

- `PROVEN_EDGE`
- `PRODUCTION_READY`
- `BUY`
- `SELL`
- `CANONICAL_GEOMETRY_FROZEN`

unless separately authorized by the project's later validation gates.
