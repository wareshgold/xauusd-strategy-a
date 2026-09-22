# SP2L Strategy A — Source Geometry Resolution Checkpoint — 2026-09-22

## Purpose

Consolidate the currently source-supported geometry boundaries after the engineering signal-reconciliation gate closed at commit `a6823a8`.

This document is research evidence only. It does not freeze or redefine Strategy A geometry.

## Evidence hierarchy

`source meaning > source-discriminated semantics > synthetic fixtures > implementation > performance`

Historical performance, parameter stability, or MT5 forward observations cannot resolve an ambiguity that the source does not uniquely define.

## Current source-supported state

| Area | Current status | Safe conclusion |
|---|---|---|
| SP2L meaning | SOURCE-CONFIRMED | Spike → 2 Leg |
| Valid breakout | SOURCE-CONFIRMED | Valid BO is associated with P-Gap |
| P-Gap vs common gap | SOURCE-CONFIRMED | P-Gap is distinguished from common/E-Gap |
| P-Gap executable OHLC formula | UNRESOLVED | No canonical formula |
| P-Gap candle indexing | UNRESOLVED | No canonical indices |
| P-Gap equality/boundary semantics | UNRESOLVED | No invented > / >= rule |
| Bullish dynamic entry concept | STRONGLY SOURCE-SUPPORTED | Relevant/current higher-low can be the pending Buy Limit level in the demonstrated construction |
| Universal entry anchor | UNRESOLVED | Do not hard-code latest swing low for every setup |
| Pending-order refresh | SOURCE-SUPPORTED CONCEPT / RULE UNRESOLVED | Order may be deleted/replaced as structure develops; exact deterministic replacement threshold is not established |
| Entry vs SL | SOURCE-SUPPORTED | Entry and structural invalidation are distinct levels |
| Structural SL exact OHLC anchor | UNRESOLVED | No wick/body/base-low formula frozen |
| AB=CD magnitude relationship | SOURCE-CONFIRMED | Leg 2 expected approximately equal to Leg 1 |
| A/B/C/D anchors | UNRESOLVED | Entry=C and arbitrary swing mappings prohibited |
| AB=CD tolerance | UNRESOLVED | No numerical tolerance inferred |
| 2X concept | SOURCE-CONFIRMED | Second-position/reward-management concept exists |
| 2X exact numeric formula | UNRESOLVED | No universal half-target or R-multiple formula frozen |
| Bearish universal geometry | UNRESOLVED | Synthetic mirror is deterministic but is not source confirmation |
| Production execution semantics | LOCKED | Research-only until geometry is frozen and validated |

## What the current evidence does NOT authorize

- Selecting a P-Gap formula because it gives the best backtest.
- Treating a generic three-candle imbalance as canonical P-Gap.
- Assuming C equals the pending-order fill price.
- Assuming Entry = C.
- Choosing arbitrary A/B/C/D swing points.
- Substituting Fibonacci for AB=CD.
- Inventing an AB=CD tolerance.
- Treating the synthetic bearish mirror as proof of the teacher's bearish rule.
- Converting the current research runner into canonical production logic.

## Next source-resolution work

1. Resolve P-Gap boundary and candle-reference semantics from the archived visual evidence.
2. Resolve whether the demonstrated dynamic/relevant-low entry generalizes across the source examples.
3. Resolve the exact structural SL anchor.
4. Resolve deterministic pending-order replacement semantics.
5. Resolve A/B/C/D anchors for AB=CD.
6. Resolve the relationship between AB=CD and TP1/TP2/2X.
7. Obtain source-level bearish confirmation before promoting a universal mirrored rule.

## Gate status

- Source Resolution: **PARTIAL — active**
- Synthetic Fixtures: **PASS**
- Engineering signal reconciliation: **PASS**
- Frozen Geometry: **BLOCKED**
- DEV: **LOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**

## Important observation

The recent MT5 stability results and clean multi-symbol predicate reconciliation demonstrate engineering consistency and research behavior. They do not resolve the remaining source-geometry ambiguities. The next work therefore stays on source resolution rather than parameter optimization.
