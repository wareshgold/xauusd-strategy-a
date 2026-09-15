# SP2L Strategy A — Current Project State Snapshot

**Date:** 2026-09-15  
**Purpose:** Freeze a human-readable project-state checkpoint before the next research/engineering gate.

## Executive status

`SOURCE_RESOLUTION_STOPPED_PENDING_NEW_TIER1_TIER2_DISCRIMINATOR`

Strategy A geometry is **not frozen** and execution is **disabled**.

No statistically valid Strategy A Win Rate has been established yet. Any previously observed backtest/replay performance must not be treated as evidence of canonical Strategy A edge while source geometry remains unresolved.

## Governance invariants

1. Source meaning outranks implementation convenience.
2. Only source-confirmed rules may become canonical.
3. Unresolved geometry remains explicitly unresolved.
4. Backtest performance cannot resolve source ambiguity.
5. Generic technical-analysis conventions cannot fill source gaps.
6. Inferred symmetry cannot fill the bearish mirror gap.
7. No undocumented buffer, threshold, formula, candle indexing, fill rule, or execution rule may be introduced.
8. AI may assist research, engineering, validation, documentation, and analytics, but cannot autonomously define canonical Strategy A geometry or generate production BUY/SELL decisions.
9. Production authorization requires frozen geometry plus statistical validation, robustness/stability, and fresh holdout evidence.

## Source-resolution state

The authoritative source remains the SP2L source video and its Tier-1 transcript/frame evidence. Multiple bounded source-review passes have already been completed. The existing evidence package and adjudication worksheet narrow semantic hypotheses but do not uniquely and reproducibly determine all executable OHLC geometry.

### C01–C08 conservative adjudication state

| Candidate | Dimension(s) | State | What is source-supported | What remains unresolved |
|---|---|---|---|---|
| C01 P-Gap | `p_gap` | `REMAINS_BLOCKED` | P-Gap is explicitly associated with valid breakout; distinct from E-GAP | Exact executable candle/price boundary |
| C02 Entry / SL | `entry_anchor`, `structural_invalidation` | `REMAINS_BLOCKED` | Corrective Buy Limit and lower SL/invalidation role are distinct | Exact candle/price anchors and fill semantics |
| C03 AB=CD / Leg-2 | `abcd_anchors`, `abcd_tolerance`, `leg2_start` | `REMAINS_BLOCKED` | AB=CD and Leg-2≈Leg-1 magnitude semantics at candle level | A/B/C/D anchors, tolerance, exact Leg-2 start |
| C04 Targets / 2X | `targets_2x` | `REMAINS_BLOCKED` | TP1, TP2 and 2X are named source concepts | Exact formulas, anchors and execution semantics |
| C05 Bearish | `bearish_mirror` | `REMAINS_BLOCKED` | Bearish examples/continuation exist | Explicit deterministic bullish↔bearish mapping |
| C06 Pending lifecycle | `pending_refresh` | `REMAINS_BLOCKED` | Pending order can be deleted/changed in source examples | Exact delete/replace/retain condition |
| C07 Trigger family | `trigger_classifier` | `REMAINS_BLOCKED` | 1/2/3-candle family and breakout/follow-through concepts | Exact OHLC classifier and exhaustiveness |
| C08 Correction / invalidation | `structural_invalidation`, `entry_anchor` | `REMAINS_BLOCKED` | Correction and return-to-level invalidation relationship | Exact OHLC boundary and anchor identity |

## Ten geometry dimensions

All ten remain blocked pending source-discriminating evidence plus human adjudication:

1. `p_gap`
2. `entry_anchor`
3. `leg2_start`
4. `structural_invalidation`
5. `pending_refresh`
6. `trigger_classifier`
7. `abcd_anchors`
8. `abcd_tolerance`
9. `targets_2x`
10. `bearish_mirror`

## Engineering state

The project now has source-safe engineering infrastructure for continued work without promoting unresolved geometry:

- deterministic replay plumbing with provenance preservation;
- source-safe synthetic fixture contract;
- evidence candidate intake contract;
- manual adjudication contract and reusable worksheet;
- frozen-geometry readiness gate;
- CI checks and governance scans;
- engineering-only Spec Kit pilot/adoption boundary.

These components are infrastructure, not authorization to execute Strategy A.

## Spec Kit state

Decision remains:

`ADOPT_SELECTIVELY`

Spec Kit is treated as an engineering SDD layer only. It is not a source authority and cannot decide P-Gap, entry, Leg-2, AB=CD, targets, refresh, bearish mirror, fill, or execution semantics.

## Statistical state

### Current claim

`WIN_RATE = NOT_ESTABLISHED`

There is intentionally no canonical Strategy A Win Rate to report at this stage.

A high observed percentage would not be considered evidence of a reproducible edge unless the same frozen, source-aligned rules survive:

`Development → Untouched Validation → Robustness/Stability → Fresh Holdout`

The project therefore explicitly rejects performance-chasing, parameter selection by best Win Rate, and using backtest results to resolve source ambiguity.

## Current gate position

```text
SOURCE RESOLUTION
        ↓
C01–C08 evidence package
        ↓
Manual adjudication
        ↓
Frozen Geometry Readiness
        ↓
NOT READY — unresolved source geometry
```

Engineering work may continue only where it remains strategy-neutral and execution-disabled.

## Next authorized step

1. Treat the repeated source-review hunt as stopped unless genuinely new Tier-1/Tier-2 evidence appears.
2. Complete/record human manual adjudication outcomes for C01–C08.
3. Run the Frozen Geometry Readiness Review.
4. Keep every unresolved dimension blocked.
5. If/when all required geometry is genuinely source-discriminated and manually adjudicated, prepare a reviewable frozen-geometry candidate package.
6. Only after a legitimate freeze proceed to deterministic Strategy A development and later untouched statistical validation.

## Explicit non-claims

This snapshot does **not** claim:

- Strategy A is profitable;
- Strategy A has an 80%+ Win Rate;
- any observed performance is statistically validated;
- any unresolved geometry has been inferred safely enough for production;
- BUY/SELL generation is authorized.

## Bottom line

The project is currently stronger in **research governance, provenance, reproducibility, and execution safety** than it was before the evidence-gating work. The remaining bottleneck is not lack of engineering infrastructure; it is the absence of source-discriminating evidence for the unresolved executable geometry.

The correct response to that bottleneck is to preserve the ambiguity, not optimize around it.
