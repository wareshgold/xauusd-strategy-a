# SP2L Source Resolution — Next Gate Plan — 2026-09-14

## Objective

Run only finite, source-first research against the remaining blockers identified by the F8–F15 consolidation. No historical optimization is permitted to choose among source interpretations.

## Priority order

### P0 — executable geometry that gates the core setup

1. **P-Gap**
   - Question: can authoritative source evidence uniquely determine candle index, OHLC boundaries, and equality/overlap semantics?
   - Existing state: semantic identity resolved; executable geometry blocked.
   - Stop condition: if authoritative evidence does not discriminate, record `UNRESOLVED` and do not substitute generic gap arithmetic.

2. **Entry anchor**
   - Question: can the demonstrated relevant/dynamic Low/High semantics be generalized across source variants without invention?
   - Existing state: demonstrated bullish variant strongly favors relevant/dynamic structural level; universal algorithm unresolved.
   - Stop condition: no universal rule unless source evidence explicitly supports it.

3. **Structural invalidation / SL boundary**
   - Question: can Spike-origin/base structural semantics be mapped to a unique candle/OHLC boundary?
   - Existing state: semantic separation resolved; executable OHLC level blocked.
   - Stop condition: no wick/body/buffer choice without direct evidence.

### P1 — deterministic state transitions

4. **Pending-order refresh**
   - Question: can the source define a deterministic retain/replace condition?
   - Existing state: refresh is permitted; threshold remains qualitative.
   - Stop condition: if the source remains qualitative, retain `UNRESOLVED` rather than inventing a distance threshold.

5. **Trigger classifier**
   - Question: can the one-/two-/three-candle family be classified deterministically?
   - Existing state: family existence source-discriminated; classifier blocked.
   - Stop condition: no arbitrary priority or candle-count rule.

### P2 — reward/measurement geometry

6. **AB=CD**
   - Question: can A/B/C/D be identified at candle/OHLC level and can equality tolerance be source-derived?
   - Existing state: magnitude relationship confirmed; anchors/tolerance blocked.
   - Stop condition: no Fibonacci or numeric tolerance substitution.

7. **2X / TP1 / TP2**
   - Question: can the source define the exact operational meaning and formulas?
   - Existing state: concept and TP1 preference present; implementation unresolved.
   - Stop condition: no `2R`, `1:1`, `50%`, Fibonacci, or other formula unless directly sourced.

### P3 — directional completeness

8. **Bearish mirror**
   - Question: is there sufficient independent bearish evidence for deterministic execution?
   - Existing state: blocked.
   - Stop condition: no sign-flip or geometric-mirror assumption.

9. **Session/time constraints**
   - Question: does authoritative source material establish a canonical session/time filter?
   - Existing state: no inferred filter is canonical.
   - Stop condition: absence of direct evidence means no session filter.

10. **Strategy-side fill/exit semantics**
    - Question: after infrastructure semantics are fixed, does source material uniquely determine strategy-specific fill/stop/target interpretation?
    - Existing state: infrastructure is audited; strategy geometry remains source-blocked where applicable.
    - Stop condition: unresolved source semantics remain explicitly unresolved.

## Evidence rule

For each blocker, the research record must contain:

1. Tiered evidence source(s).
2. Exact source meaning supported by those sources.
3. Competing executable interpretations.
4. Which interpretations the source explicitly eliminates.
5. Which interpretations remain indistinguishable.
6. Final status: `SOURCE-DISCRIMINATED`, `SOURCE-DOES-NOT-DISCRIMINATE`, `BLOCKED`, or `REJECTED` with reason.
7. No backtest result used as evidence of source meaning.

## Freeze criterion

Frozen Geometry may begin only when every required executable dimension needed by the deterministic Strategy A specification is either:

- source-discriminated to a unique executable rule, with explicit manual approval by Ali; or
- explicitly marked unresolved and the strategy specification formally records that the unresolved dimension prevents deterministic execution.

A profitable backtest is never a substitute for source resolution.

## Current gate

- SOURCE RESOLUTION: **IN PROGRESS**
- SYNTHETIC FIXTURES F8–F15: **ADJUDICATION COMPLETE**
- FROZEN GEOMETRY: **BLOCKED**
- DEV / UNTOUCHED VALIDATION / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: **LOCKED**

## Immediate next action

Perform a source-evidence pass on the highest-impact unresolved P0 dimensions, starting with P-Gap executable geometry, then Entry anchor and structural invalidation boundary. If the authoritative evidence cannot discriminate them, close those dimensions as `UNRESOLVED` rather than extending the research indefinitely or optimizing around ambiguity.