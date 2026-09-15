# SP2L Strategy A — Readiness Dashboard

**Date:** 2026-09-15  
**Status:** `SOURCE_RESOLUTION_STOPPED / FREEZE_NOT_READY / EXECUTION_DISABLED`

## 1. Current gate position

The repeated source-resolution passes have not produced a genuinely new Tier-1/Tier-2 discriminator. The source hunt is therefore stopped rather than extended by inference.

The active research packet is the C01–C08 evidence candidate package. Each candidate remains subject to human manual adjudication. No candidate is canonical merely because it is source-grounded.

## 2. Geometry readiness matrix

| Dimension | Candidate | Current status | Canonical? |
|---|---|---|---|
| `p_gap` | C01 | `REMAINS_BLOCKED` | No |
| `entry_anchor` | C02 | `REMAINS_BLOCKED` | No |
| `leg2_start` | C03 | `REMAINS_BLOCKED` | No |
| `structural_invalidation` | C08 | `REMAINS_BLOCKED` | No |
| `pending_refresh` | C06 | `REMAINS_BLOCKED` | No |
| `trigger_classifier` | C07 | `REMAINS_BLOCKED` | No |
| `abcd_anchors` | C03 | `REMAINS_BLOCKED` | No |
| `abcd_tolerance` | C03 | `REMAINS_BLOCKED` | No |
| `targets_2x` | C04 | `REMAINS_BLOCKED` | No |
| `bearish_mirror` | C05 | `REMAINS_BLOCKED` | No |

## 3. Source-confirmed semantic layer

The current evidence supports semantic statements such as breakout/follow-through, P-Gap as a source term, Spike → correction → Second Leg, corrective entry, structural invalidation concept, Leg-2/Leg-1 magnitude relationship, target/2X concepts, and bearish examples.

These semantics do **not** by themselves supply a reproducible executable OHLC specification. Exact boundaries, anchors, tolerances, thresholds, indexing, fill semantics, and execution rules remain unresolved where the source does not discriminate them.

## 4. Engineering readiness

Available source-safe infrastructure includes:

- synthetic fixture contract;
- source-safe replay harness;
- evidence candidate intake;
- human manual-adjudication contract and worksheet;
- frozen-geometry readiness gate;
- CI/provenance checks;
- strategy-neutral Spec Kit engineering pilot.

The infrastructure is not an authorization to execute Strategy A.

## 5. Statistical-validation readiness

Statistical validation is downstream of a legitimate geometry freeze.

Required sequence:

`FROZEN GEOMETRY → DEVELOPMENT → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION REVIEW`

Required future reporting includes event/sample counts, uncertainty around performance statistics, expectancy, drawdown/risk, predefined temporal stability, defensible regime stability, sensitivity/stability diagnostics, and independent untouched/fresh-holdout results.

**Win Rate status:** `NOT_ESTABLISHED`

A development-period Win Rate, even if high, cannot resolve source ambiguity and cannot authorize production.

## 6. Explicit prohibitions

- No invented P-Gap formula.
- No invented AB=CD anchors or tolerance.
- No invented entry/fill semantics.
- No implementation-selected buffer or threshold.
- No inferred bearish symmetry.
- No optimization to manufacture a desired Win Rate.
- No pooling of incompatible pattern/action families.
- No production BUY/SELL generation.

## 7. Next actions

1. Human adjudication of C01–C08.
2. Record `SOURCE_DISCRIMINATED` only where the source itself uniquely and reproducibly determines the rule; otherwise retain `REMAINS_BLOCKED`.
3. Run Frozen Geometry Readiness Review.
4. If and only if all required dimensions are legitimately frozen, begin deterministic development and downstream statistical gates.

This dashboard is a governance/readiness artifact. It does not freeze Strategy A geometry and does not authorize execution.
