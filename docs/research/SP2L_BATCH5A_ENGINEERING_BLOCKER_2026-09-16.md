# SP2L Batch 5A — Engineering Blocker Record — 2026-09-16

## Purpose

Separate repository/build failures from SP2L source-geometry resolution. This record does not alter canonical geometry, source interpretation, risk semantics, or the 125R forensic case.

## Evidence

### Isolated deterministic test path

Run `35063295675` completed successfully on commit `382e7d822aa7ecf3537d50223ca24cec71ed4802`.

- source-boundary assertions: 3/3 passed
- synthetic source fixtures: 3/3 passed
- workflow job: success

This validates the isolated boundary/fixture harness only. It does not freeze geometry.

### Full regression path

Run `35063295658` completed with failure during `npm run build`.

Build errors include TypeScript import-extension errors, optional-volume typing, missing execution-module imports, and stale test fixture type mismatches. Because the build step failed, the deterministic regression/source-boundary/fixture steps in that workflow were skipped.

## Interpretation

The build failure is an engineering/repository-integrity blocker, not evidence for choosing any unresolved SP2L geometry interpretation.

No changes are authorized here to:

- P-Gap formula
- relevant swing selection
- structural invalidation anchor
- wick/body semantics
- pending-order replacement threshold
- trigger taxonomy
- AB=CD anchors/tolerance
- 2X formula
- TP1/TP2 formula
- session semantics
- 125R treatment

## Gate State

- Source Resolution: PARTIAL PASS
- Source-boundary assertions: PASS
- Synthetic fixture infrastructure: PASS
- Full deterministic regression: BLOCKED by build
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

## Next Engineering Step

Repair only repository/build integrity, then rerun build and the full deterministic suite. Do not use profitability or backtest performance to resolve source-equivalent geometry.
