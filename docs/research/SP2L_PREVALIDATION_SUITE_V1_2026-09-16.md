# SP2L Pre-Validation Suite v1 — 2026-09-16

## Purpose

Prepare a deterministic pre-validation layer for F09–F14 and P-Gap without freezing unresolved source geometry and without generating production BUY/SELL decisions.

## Current contract

The suite distinguishes:

- `SOURCE_CONFIRMED`: source uniquely determines the field.
- `CANDIDATE`: a plausible interpretation exists but is not canonical.
- `UNRESOLVED`: source does not uniquely determine the executable meaning.

Canonical historical validation is blocked while any required geometry field is not `SOURCE_CONFIRMED`.

## Frozen Geometry Gate integration

Canonical validation is downstream of the deterministic Frozen Geometry Readiness Gate:

`SOURCE RESOLUTION → FROZEN GEOMETRY GATE → CANONICAL VALIDATION`

The gate is fail-closed. Any `CANDIDATE` or `UNRESOLVED` required field blocks canonical validation. Candidate fixtures remain allowed for source-discrimination and engineering work, but their outcomes must not enter canonical performance metrics.

## Fixture inventory

| Fixture | Source state | Required discipline |
|---|---|---|
| F09 Entry vs Leg-2 start | PARTIAL | Do not equate entry with Leg-2 origin by assumption. |
| F10 Stop anchor | PARTIAL | Keep structural invalidation separate from risk-stop implementation. |
| F11 Limit refresh | PARTIAL | Preserve delete/re-place behavior; do not invent a numeric threshold. |
| F12 Trigger family | PARTIAL | Preserve 1/2/3-candle and bar/key-bar variants; classifier/precedence unresolved. |
| F13 2X | PARTIAL | Preserve optional second-position concept; do not invent a universal equation. |
| F14 AB=CD | PARTIAL | Preserve Leg2≈Leg1 magnitude semantics; do not invent A/B/C/D or tolerance. |
| P-Gap | UNRESOLVED | Do not substitute a generic three-candle imbalance formula. |

## Allowed execution modes

1. **Source-discrimination mode:** compare explicit candidate interpretations against fixtures.
2. **Contract mode:** verify unresolved fields fail closed.
3. **Historical validation mode:** LOCKED until the Frozen Geometry Gate is READY.

## Explicit non-goals

This suite does not define entry price, stop price, P-Gap formula, AB=CD anchors/tolerance, 2X sizing, fill semantics, refresh threshold, trigger precedence, or production signal rules.

## 125R preservation

The 125R observation remains untouched. This integration does not clip, exclude, reclassify, or optimize it.

## Next gate

Only after primary evidence uniquely determines the executable fields may provenance be promoted to `SOURCE_CONFIRMED`, the Frozen Geometry Gate become READY, and untouched validation activate. No historical performance result from a candidate interpretation may be used to promote that interpretation to canonical status.
