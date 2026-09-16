# SP2L Metrics Fail-Closed Provenance Checkpoint — 2026-09-16

## Purpose

Record the next engineering hardening step after the Frozen Geometry Gate audit.

## Change

The research-only canonical metrics aggregator now requires all of the following before an observation can contribute to performance metrics:

1. `status === EXECUTED`;
2. `excludedFromMetrics === false`;
3. every geometry provenance field is `SOURCE_CONFIRMED`.

An observation marked `EXECUTED` cannot bypass the provenance boundary merely by mutating status or metric fields.

## Safety property

Candidate or unresolved provenance is fail-closed at the metrics boundary. Such observations remain visible to research but contribute zero to trade count, win rate, expectancy, drawdown, and R-value distributions.

## Test coverage

The validation-report suite now explicitly covers:

- blocked geometry excluded from metrics;
- ready-but-unexecuted reports excluded from metrics;
- canonical executed observations aggregated;
- executed-but-non-canonical provenance excluded from metrics.

## 125R

The new regression fixture uses a synthetic `125R` value only to prove that non-canonical provenance cannot enter the denominator. It does not alter, clip, reclassify, or validate the historical 125R observation.

## Gate status

Frozen Geometry remains `BLOCKED`. This change does not promote any source field and does not unlock historical validation, robustness, holdout, or production.

## Next action

Run the SP2L harness typecheck and focused validation-report / frozen-gate / geometry-contract tests locally after pulling the new commits. If green, continue with fixture-led accounting and provenance coverage without changing unresolved geometry.
