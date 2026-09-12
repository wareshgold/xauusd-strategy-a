# SP2L G298 — Phase 41 Counterfactual Concentration & Execution Semantics Audit

**Date:** 2026-09-12  
**Status:** `COUNTERFACTUAL_ONLY__HIGH_CONCENTRATION__EXECUTION_SEMANTICS_MISMATCH_CONFIRMED`

## Scope

Audit the 15 observations printed by Phase 40/41 A/New York counterfactual robustness and check whether the headline result is concentrated in a small number of observations. Also compare the counterfactual exit semantics with the repository's current invalidation semantics.

## Concentration

The 15 R observations are:

`0.397728, 0.748876, -1, 1.130113, 5.203051, -1, -1, -1, 2.378574, -1, -1, 12.880169, 65.913577, 2.575687, -1`

Total = `84.227775R`.

Gross positive R = `91.227775R`.

Gross negative R = `-7R`.

The largest observation contributes:

`65.913577 / 84.227775 = 77.78%` of total R.

The two largest observations (`65.913577 + 12.880169`) contribute approximately `93.55%` of total R.

The three largest observations (`65.913577 + 12.880169 + 5.203051`) contribute approximately `99.73%` of total R.

Removing the largest observation leaves `18.314198R` over 14 observations (`avgR=1.308157`, `PF=3.616314`).

## Interpretation

This is a severe concentration diagnostic. It does not justify deleting or clipping observations. The correct conclusion is that the counterfactual result is economically dominated by a few large-R outcomes and therefore cannot be treated as stable evidence of a canonical Strategy A edge.

## Execution-semantics mismatch

Phase 40's `flipR()` evaluates the counterfactual SELL using the next candles' **high/low first-hit semantics**:

- stop if `high >= stop`
- target if `low <= target`
- if both occur in the same candle, return null

The repository's current `Invalidation.ts` exposes `isInvalidated()` using **close-based semantics**:

- BUY invalidation when `close < invalidationLevel`
- SELL invalidation when `close > invalidationLevel`

Therefore the Phase 40 counterfactual is not an execution-equivalent replay of the current invalidation component. This is another reason the R outcomes must remain research-only.

## Stop-geometry mismatch

The current research invalidation rule returns `correction.extremePrice` with reason `CORRECTION_EXTREME_BREACH`. This is not the source-frozen structural stop. Source evidence currently says the stop is behind the candle from which the Spike originated, while exact OHLC boundary remains unresolved.

## Target-geometry mismatch

The current research projection uses:

`leg1Size = abs(spikeEnd.close - spikeStart.open)`

and projects from `correction.extremePrice` to produce `tp1`.

This is an implementation hypothesis, not source-frozen Strategy A geometry. The source audit has not established that these anchors define Leg 1 or TP1.

## Decision

- Keep all 15 observations unchanged in raw research output.
- Do not trim/cap the 65.913577R value.
- Do not call the 14-observation result validated.
- Do not promote Phase 40/41 to production or validation evidence.
- Before any further performance interpretation, freeze source-confirmed Entry, structural Stop, Leg 1/AB=CD, Target and execution semantics.
- When geometry is frozen, rerun the complete sample under one deterministic execution convention and compare to this counterfactual only as an audit baseline.

## Provenance

- Phase 40 source: `scripts/research-phase40-a-ny-leave-one-out-robustness.mjs`.
- Phase 41 source: `scripts/research-phase41-a-ny-chronological-holdout-audit.mjs`.
- Current invalidation source: `src/domain/strategy-a/Invalidation.ts`.
- Current projection source: `src/domain/strategy-a/LegProjection.ts`.
