# SP2L Synthetic Discrimination Gate — 2026-09-08

## Purpose

Create deterministic synthetic fixtures that distinguish competing interpretations of unresolved Strategy A / SP2L geometry before any historical optimization or production implementation.

Synthetic fixtures are evidence-control infrastructure. They do not decide what the source means.

## Rule

A hypothesis may become canonical only after a primary-source observation discriminates it. A synthetic fixture can prove that two interpretations are mechanically different; it cannot prove which interpretation is source-correct.

## Covered unresolved fields

| Field | Candidate interpretations | What a discriminating source observation must show |
|---|---|---|
| P-Gap boundary | prior extremes / body edges / wick-to-wick | Explicitly identify the two price boundaries used by the source gap |
| P-Gap candle identity | fixed 3-candle / breakout-follow-through relational / multi-candle relational | Repeated source examples with identifiable candle roles |
| P-Gap touch rule | strict non-overlap / touch allowed / equality allowed | A source example at the boundary case |
| Entry candle identity | previous/relevant / first correction / origin | Source chart where the reference candle is unambiguous |
| Entry price convention | wick / body | Source price visibly aligned to one boundary |
| Entry revision | fixed at qualification / revised during correction | Source order-management example showing whether level changes |
| Fill semantics | intrabar touch / cross / close confirmation | Source execution example that distinguishes intrabar from close behavior |
| SL boundary | origin wick / origin body / buffered extreme | Source order and candle geometry with unambiguous alignment |
| Spike origin identity | first directional candle / structural origin / variant-specific | Source example mapping the origin annotation to a specific candle |
| Leg-1 anchors | origin→extreme / correction-extreme→extreme / breakout-level→extreme | Source AB=CD diagram with explicit anchor identity |
| AB=CD tolerance | exact / fixed tolerance / contextual tolerance | Multiple source examples or explicit textual tolerance rule |

## Fixture design principles

1. Every fixture is mirrored where direction matters.
2. Candidate anchors are deliberately separated so a future source observation can select exactly one interpretation.
3. Boundary cases are included for equality/touch semantics.
4. No fixture contains a selected production value.
5. No fixture contains profitability metrics.
6. No fixture imports generic FVG, BOS/MSS, liquidity sweep, displacement, Fibonacci AB/CD, or fixed thresholds as canonical rules.
7. Synthetic data must never be optimized to make one interpretation profitable.

## Current decision

The gate is **READY / NO HYPOTHESIS SELECTED**.

This is the correct state while executable geometry remains unresolved. The semantic contract remains frozen separately; DEV, untouched validation, robustness, fresh holdout, and production remain locked.

## Promotion protocol

For each unresolved field:

1. Identify a primary-source observation.
2. Map the observation to the fixture's candidate interpretations.
3. Require the observation to discriminate at least two candidates.
4. Record the source timestamp/frame and reasoning.
5. Update the relevant research fixture.
6. Add/adjust a unit test proving the selected interpretation is now represented.
7. Update the source-resolution matrix.
8. Only when all required executable fields are resolved may Frozen Geometry be considered for approval.

## Prohibited shortcut

A backtest may compare already-source-confirmed alternatives, but it may not select the meaning of an unresolved source concept. Profitability is not source evidence.

## Gate status

SOURCE RESOLUTION: semantic contract complete.
SYNTHETIC FIXTURES: ready.
FROZEN GEOMETRY: blocked.
DEV: locked.
UNTOUCHED VALIDATION: locked.
ROBUSTNESS / STABILITY: locked.
FRESH HOLDOUT: locked.
PRODUCTION: unchanged.
