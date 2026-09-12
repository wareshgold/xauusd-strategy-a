# SP2L G296 — Phase 41 65.91R Counterfactual Outlier Audit

**Date:** 2026-09-12  
**Scope:** Phase 41 A/New York chronological audit  
**Status:** `COUNTERFACTUAL_ONLY__OUTLIER_TRACE_COMPLETE__CANONICAL_GEOMETRY_UNRESOLVED`

## Objective

Audit the single `R=65.913577` observation that dominates the Phase 41 A/New York counterfactual result. Determine whether the value is an arithmetic/data artifact or a deterministic consequence of the currently implemented research hypothesis.

## Exact observation

Phase 24 identifies the observation as:

- entry time: `2026-08-26 00:15:00`
- baseline entry index: `9574`
- direction: `BUY`
- session: `NEW_YORK`
- split/window: `VAL / VAL_2`
- baseline result: `SL`

The baseline order values are:

- Entry: `4654.61451`
- Stop: `4654.41005`
- TP1: `4668.091200000001`
- baseline risk distance: `0.20446`

These values are directly present in the frozen baseline report/data. The baseline trade itself is a loss (`SL`).

## Arithmetic reconstruction

Phase 40 flips the baseline BUY into a counterfactual SELL using the same entry-to-stop risk and the same entry-to-TP reward distance:

- counterfactual SELL entry = `4654.61451`
- counterfactual SELL stop = `4654.81897`
- counterfactual SELL TP = `4641.13782`

Reward distance:

`4654.61451 - 4641.13782 = 13.47669`

Risk distance:

`4654.81897 - 4654.61451 = 0.20446`

Therefore:

`13.47669 / 0.20446 = 65.913577... R`

The 65.91R value is therefore **arithmetically reproducible** from the stored Entry/SL/TP values. It is not a floating-point anomaly or an LOO reconstruction error.

## Forward-candle execution check

The source 5-minute dataset contains:

### Entry candle — 00:15

- Open `4653.44984`
- High `4654.84336`
- Low `4651.75573`
- Close `4654.61451`

Phase 40 intentionally begins forward evaluation at the candle after the entry candle, so the entry candle's high is not used to invalidate the counterfactual order.

### 00:20

- High `4654.14034`
- Low `4645.32912`

This does not hit the counterfactual SELL stop `4654.81897`, and it does not yet hit TP `4641.13782`.

### 00:25

- High `4647.70403`
- Low `4643.54231`

Still no stop or TP.

### 00:30

- High `4653.10628`
- Low `4644.41054`

Still no stop or TP.

### 00:35

- High `4648.00436`
- Low `4639.43820`

The counterfactual SELL TP `4641.13782` is crossed. Therefore the 65.913577R result is also reproducible under the Phase 40 forward-candle execution semantics.

## Root cause classification

### Arithmetic/data artifact

**Rejected.** The number is exactly explained by the stored distances and forward candles.

### Execution-timing artifact

**Not demonstrated.** The counterfactual TP is reached after entry and before a later counterfactual stop under the implemented first-hit semantics.

### Canonical Strategy A evidence

**Rejected.** Phase 40 is explicitly a research-only counterfactual hypothesis. It does not establish a source-confirmed Strategy A target or stop geometry.

## Critical geometry finding

The outlier exposes why this hypothesis cannot be promoted:

1. The research `LegProjection` implementation defines Leg 1 as the absolute difference between the spike-end close and spike-start open, then projects it from the correction extreme.
2. The research `Invalidation` implementation uses the correction extreme as the stop/invalidation level.
3. The resulting reward/risk ratio can become extremely large when the correction extreme is very close to the entry while the projected Leg 1 is large.
4. The source-aligned project record does **not** currently authorize either executable geometry as canonical.
5. In particular, source evidence says the structural stop is behind the candle from which the Spike originated; the current research implementation's `CORRECTION_EXTREME_BREACH` is therefore not sufficient to establish canonical Strategy A stop geometry.
6. The source target construction is also unresolved; `TP1=1R`, `TP2=2R`, `TP=AB=CD`, `250/500`, and Round Level selection remain unconfirmed.

## Decision

The 65.913577R observation is **real within the counterfactual implementation**, but it is **not evidence of a Strategy A edge**.

It must not be removed merely because it is large, and it must not be accepted merely because it improves the result. It should remain in the counterfactual audit while canonical geometry remains unresolved.

### Phase 41 interpretation after G296

`A_NY N=15` remains a descriptive/counterfactual result only.

The `LAST_20` and `LAST_40` headline statistics are strongly influenced by this observation and therefore should not be presented as evidence of a validated edge.

The correct next research step is not outlier trimming. It is to resolve the **source-confirmed stop and target geometry**, then rerun the same observation under the frozen deterministic specification. Any change must be justified by source evidence, not by performance.

## Provenance

- Phase 24 loss-archetype report: observation `2026-08-26 00:15:00`, baseline index `9574`, `LOSS_A_NO_PRE_FAVORABLE`.
- Baseline 5-minute dataset: TwelveData XAU/USD, UTC.
- Phase 40 implementation: counterfactual BUY→SELL transformation and forward first-hit evaluation.
- Phase 41 implementation: chronological slicing of the 15 Phase 40 counterfactual observations.
- Source-resolution gate remains blocked for executable target geometry.
