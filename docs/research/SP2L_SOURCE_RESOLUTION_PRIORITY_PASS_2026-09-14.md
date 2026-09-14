# SP2L Source Resolution Priority Pass — 2026-09-14

## Purpose

This document converts the F8–F15 consolidation into a finite next-pass research order. It does not define executable Strategy A geometry and does not authorize engine implementation.

## Governing rule

Source meaning outranks backtest performance. If authoritative evidence cannot discriminate competing executable interpretations, the result remains `UNRESOLVED` / `BLOCKED`. No numerical formula, tolerance, candle index, OHLC anchor, buffer, fill rule, or mirrored rule may be invented to force closure.

## Current source-resolved semantics

1. SP2L is Spike → 2 Leg.
2. Valid breakout is associated with source-defined P-Gap / Pressure Gap semantics.
3. Correction entry uses a pending Limit model.
4. Entry is distinct from the start of Leg 2.
5. Entry is distinct from structural invalidation.
6. Structural invalidation is distinct from risk-budget position sizing.
7. Source demonstrates one-, two-, and three-candle trigger constructions.
8. AB=CD establishes a Leg-2 magnitude relationship approximately matching Leg 1.
9. None of the above freezes a complete executable candle/OHLC algorithm.

## Priority A — P-Gap executable geometry

**Status:** BLOCKED at executable level.

Resolve only from source evidence:
- exact candle/index relationship, if explicitly demonstrated;
- executable boundaries, if source identifies them;
- wick/body treatment;
- equality/overlap semantics;
- whether the demonstrated variants share one invariant.

Explicitly prohibited:
- substituting a generic three-candle imbalance formula;
- inventing minimum gap size;
- selecting the formula because it improves historical results.

**Closure:** `SOURCE-DISCRIMINATED` only if the evidence supports a deterministic source-consistent geometry. Otherwise `SOURCE-DOES-NOT-DISCRIMINATE`.

## Priority B — Entry anchor

**Status:** BLOCKED at universal executable level.

Resolve:
- whether the demonstrated relevant/current HL/LH semantic generalizes across source variants;
- exact price field/anchor when source evidence is explicit;
- interaction with evolving structure before fill.

Do not freeze `Entry = latest swing low/high` universally without evidence.

## Priority C — Structural invalidation / SL boundary

**Status:** Semantic separation resolved; executable OHLC boundary blocked.

Resolve only if source evidence permits:
- Spike-origin/base candle index;
- wick versus body;
- exact stop boundary or source-defined buffer;
- bullish/bearish symmetry.

Do not replace structural invalidation with ATR, fixed distance, or risk-budget arithmetic.

## Priority D — Pending-order refresh

**Status:** Refresh is source-supported; deterministic retain/replace threshold unresolved.

Resolve:
- exact source condition for deleting/replacing a pending order;
- whether the condition is structural, distance-based, or qualitative;
- whether a deterministic invariant exists across examples.

Market-entry-on-reclaim is not an acceptable substitute for the pending-Limit model.

## Priority E — Trigger classifier

**Status:** 1/2/3-candle family confirmed; final classifier blocked.

Resolve only source-demonstrated acceptance/rejection and overlap priority. No arbitrary candle-count priority or threshold.

## Priority F — AB=CD / 2X / TP

**AB=CD:** magnitude relationship resolved; A/B/C/D anchors and tolerance blocked.

**2X / TP1 / TP2:** concepts supported, executable meaning/formula blocked.

Resolve from source only. Do not substitute Fibonacci percentages, fixed R multiples, or backtest-selected targets.

## Priority G — Bearish mirror

**Status:** BLOCKED.

A mirrored implementation is a hypothesis until sufficient bearish source evidence confirms the required symmetry. Do not assume sign-flip, wick/body, P-Gap, refresh, AB=CD, or target symmetry.

## Finite next-pass rule

The next research pass should inspect the highest-priority unresolved dimension in order: **P-Gap → Entry → SL → Refresh → Trigger → AB=CD/Targets → Bearish mirror**.

For each dimension, record exactly one outcome:
- `SOURCE-DISCRIMINATED`
- `SOURCE-DOES-NOT-DISCRIMINATE`
- `BLOCKED` (when evidence collection itself is incomplete)
- `REJECTED` with an explicit source-based reason.

Once a dimension is source-nondiscriminating, stop optimization of that dimension and move to the next one. Do not reopen it through backtest performance.

## Gate state

| Gate | State |
|---|---|
| SOURCE RESOLUTION | IN PROGRESS |
| SYNTHETIC FIXTURES F8–F15 | COMPLETE |
| FROZEN GEOMETRY | BLOCKED |
| DEV | LOCKED |
| UNTOUCHED VALIDATION | LOCKED |
| ROBUSTNESS / STABILITY | LOCKED |
| FRESH HOLDOUT | LOCKED |
| PRODUCTION | LOCKED |

## Decision

No executable Strategy A geometry is promoted by this pass. Engine implementation remains frozen until source resolution produces an explicitly approved canonical geometry. Manual approval by Ali is required for any transition to `CANONICAL`.
