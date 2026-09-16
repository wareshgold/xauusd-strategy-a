# SP2L Batch 5A — Engineering Blocker Record — 2026-09-16

## Purpose

Separate repository/build failures from SP2L source-geometry resolution. This record does not alter canonical geometry, source interpretation, risk semantics, or the 125R forensic case.

## Previous evidence

### Isolated deterministic test path

Run `35063295675` completed successfully on commit `382e7d822aa7ecf3537d50223ca24cec71ed4802`.

- source-boundary assertions: 3/3 passed
- synthetic source fixtures: 3/3 passed
- workflow job: success

This validates the isolated boundary/fixture harness only. It does not freeze geometry.

### Full regression path

Run `35063295658` completed with failure during `npm run build`.

Build errors included NodeNext import-extension errors, exact-optional-property typing, missing execution-module imports, and stale test fixture type mismatches. Because the build step failed, the deterministic regression/source-boundary/fixture steps in that workflow were skipped.

## Engineering repair pass

The following changes were applied on the Batch 5A branch strictly to restore repository/build integrity:

- restored NodeNext `.js` import specifiers in `StrategyAAdapter.ts`;
- preserved `Candle.volume` exact-optional semantics in `TwelveDataDataset.ts` by omitting `volume` when unavailable;
- restored the execution-layer boundary modules that the current execution skeleton imports: `PositionManager.ts`, `TrailingStopSafety.ts`, `mt5/BrokerConstraintGate.ts`, and `mt5/PositionModificationAdapter.ts`;
- aligned legacy test fixtures with the existing `Candle` and `Correction` interfaces without changing assertions or Strategy A geometry;
- changed the Batch 5A regression workflow so build diagnostics do not suppress later test diagnostics; the final gate still fails unless build, full regression, source-boundary assertions, and synthetic fixtures all succeed.

These are type/import/test-harness repairs only. No source-geometry rule, threshold, target, invalidation semantics, or 125R treatment was changed.

## Verification status

The repair commits have been pushed to the Batch 5A branch and the regression workflow has been configured to execute the complete sequence. A new workflow run must be inspected before any PASS claim is made.

**Important:** until that real Actions run is fetched and its job steps/logs confirm success, Full deterministic regression remains **BLOCKED / UNVERIFIED**.

## Gate State

- Source Resolution: PARTIAL PASS
- Source-boundary assertions: PASS (isolated run `35063295675`)
- Synthetic fixture infrastructure: PASS (isolated run `35063295675`)
- Full deterministic regression: BLOCKED / UNVERIFIED pending post-repair Actions evidence
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

## Non-negotiable source boundary

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

## Next Step

Inspect the real post-repair GitHub Actions run. If build and all required suites pass, record the exact run/job evidence and reassess Batch 5A. If any failure remains, repair only that engineering blocker. Geometry freeze remains conditional on source discrimination, never on profitability.
