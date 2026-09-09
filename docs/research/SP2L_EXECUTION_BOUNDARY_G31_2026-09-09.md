# SP2L Execution Boundary — G31 — 2026-09-09

## Purpose

Define exactly what research/implementation work is allowed while source geometry remains unresolved. This prevents accidental promotion of heuristics into Strategy A production logic.

## Allowed now

1. Source evidence indexing and provenance mapping.
2. Synthetic fixtures that compare competing geometry hypotheses.
3. Rejection tests for interpretations explicitly contradicted by the source.
4. Data-pipeline engineering independent of strategy decisions: timestamp normalization, OHLC integrity checks, duplicate detection, gap detection, feed provenance and reproducible dataset versioning.
5. Generic order/risk infrastructure tests using injected, already-resolved prices.
6. Backtest-engine mechanics tests using synthetic events, without claiming Strategy A performance.
7. Reporting infrastructure for trade statistics, MAE/MFE, drawdown, clustering and regime slices.
8. Live-delivery plumbing tests using mocked deterministic signals only.
9. Source documentation and review artifacts.

## Not allowed now

1. A production BUY/SELL detector for Strategy A.
2. Choosing wick versus body versus structural pivot because it performs better.
3. Choosing an AB=CD tolerance from historical optimization.
4. Defining P-Gap as a generic FVG/three-candle imbalance.
5. Inventing an Entry buffer, SL buffer or pending-order replacement threshold.
6. Assuming fill price equals geometric C or Leg-2 start.
7. Replacing the pending Limit mechanism with market-close reclaim.
8. Using session filters as canonical Strategy A rules unless separately source-confirmed.
9. Optimizing thresholds before source geometry is frozen.
10. Running DEV/VAL/holdout performance claims as Strategy A validation.

## Safe software boundary

The implementation may expose unresolved types/states explicitly, for example:

- `PGapGeometry.UNRESOLVED`
- `EntryAnchor.UNRESOLVED`
- `StopAnchor.UNRESOLVED`
- `TriggerAcceptance.UNRESOLVED`
- `ABCDAnchorModel.UNRESOLVED`
- `Leg2Projection.UNRESOLVED`
- `PendingUpdateThreshold.UNRESOLVED`
- `BearishOHLCGeometry.UNRESOLVED`

A detector receiving any critical unresolved state must return `UNRESOLVED`, not BUY or SELL.

## Promotion rule

A production signal may be emitted only after every critical geometry dependency is resolved with source provenance and the resulting deterministic specification passes:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

## Important distinction

A source-limited freeze is not permission to backtest the missing geometry and pick the most profitable candidate. It is the opposite: it freezes the uncertainty so that later empirical work cannot rewrite the source meaning.

## Gate

**Current implementation state: RESEARCH-SAFE SCAFFOLD ONLY.**

**Production Strategy A signal generation: BLOCKED.**