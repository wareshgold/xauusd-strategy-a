# G392 — Hypothesis Metrics

## Status

**RESEARCH METRICS READY; CANONICAL VALIDATION BLOCKED.**

This layer summarizes externally supplied, explicitly noncanonical trade outcomes. It does not discover entries, infer P-Gap geometry, choose A/B/C/D anchors, or optimize thresholds.

## Metrics

For each split it deterministically reports trade count, wins/losses, win rate, average R, median R, expectancy R, profit factor, maximum consecutive losses, and average holding bars.

## Guardrail

These metrics are suitable for hypothesis comparison only. A profitable hypothesis result cannot promote a rule to Strategy A. Canonical DEV remains blocked until authoritative executable geometry is frozen.

## Holdout policy

Fresh Holdout remains a confirmation dataset and must not be used for hypothesis optimization or selection.
