# G393 — Hypothesis Batch Runner

## Status

**READY FOR EXPLICIT HYPOTHESIS INPUT; CANONICAL VALIDATION BLOCKED.**

G393 executes an explicitly supplied research adapter over selected chronological splits and feeds externally resolved outcomes into G392 metrics. It does not infer trading geometry and does not select a winning hypothesis.

## Selection policy

The runner defaults to DEV and VAL only. Fresh Holdout is excluded by default and is not an optimization surface.

## Current result

With `SP2L-UNRESOLVED-GEOMETRY`, candidate count remains zero and all metrics are empty/zero. This is intentional.

## Next substantive action

Populate the runner only from the existing noncanonical hypothesis registry/formulas already documented in the repository, then compare them on DEV without touching Holdout. Any implementation remains `canonical=false` and cannot promote itself based on performance.
