# SP2L G297 — Phase 41 Outlier Influence Decision

**Date:** 2026-09-12  
**Status:** `COUNTERFACTUAL_ONLY__OUTLIER_INFLUENCE_QUANTIFIED`

## Observed Phase 41 result

The 15-observation A/New York counterfactual sample reports:

- N = 15
- win rate = 53.33%
- average R = 5.615185
- PF = 13.032539
- total R = 84.227775

The largest observation is:

- `2026-08-26 00:15:00`
- `R = 65.913577`

## Single-observation influence

Removing only the 65.913577R observation produces:

- N = 14
- average R = `1.308157`
- PF = `3.616314`
- total R = `18.314198`

Thus the headline Phase 41 result is **highly magnitude-sensitive** to one observation, even though the remaining 14 observations remain positive in this particular counterfactual sample.

This is an influence diagnostic, not a justification for deleting the observation.

## Why no trimming rule is introduced

The 65.913577R observation is arithmetically and execution-wise reproducible under the current Phase 40 counterfactual implementation (see G296). Removing it because it is inconvenient would constitute outcome-driven parameter/data selection.

Conversely, retaining it does not establish a canonical Strategy A edge because the underlying target and stop geometry are not source-frozen.

## Decision

1. Keep the observation in the raw counterfactual audit.
2. Report both full-sample and leave-one-out influence statistics when discussing Phase 41.
3. Do not winsorize, cap, delete, or otherwise transform R values.
4. Do not optimize around this observation.
5. Resolve source-confirmed Entry/SL/Leg/Target geometry before interpreting any counterfactual profitability.
6. Treat Phase 41 as a diagnostic of a hypothesis, not as validation of Strategy A.

## Gate impact

`SOURCE_RESOLUTION`: still incomplete for executable target/stop geometry.

`FROZEN_GEOMETRY`: blocked.

`DEV / VALIDATION / FRESH HOLDOUT`: no promotion from this audit.

`PRODUCTION`: blocked.

## Numerical integrity note

The large value originates from a very small risk distance (`0.20446`) combined with a large projected reward distance (`13.47669`). The ratio is exactly the reported 65.913577R. The issue is therefore the **economic/geometry meaning of the counterfactual order**, not arithmetic precision.
