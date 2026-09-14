# SP2L Source-Resolution Checkpoint — F8–F15 — 2026-09-14

## Purpose

Clean source-resolution checkpoint created directly from the main research baseline. This artifact consolidates only source-confirmed semantics and unresolved geometry for synthetic fixtures F8–F15.

## Evidence rule

Source meaning outranks backtest performance. No historical profitability, parameter optimization, or implementation convenience is used to select an interpretation. Lower-tier evidence may generate hypotheses but cannot canonicalize Strategy A geometry.

## Adjudication summary

| Fixture | Source result | Frozen consequence |
|---|---|---|
| F8 | `SOURCE-DOES-NOT-DISCRIMINATE` at universal algorithm level | Demonstrated bullish variant favors dynamic/relevant HL; universal entry-anchor algorithm unresolved |
| F9 | `SOURCE-DISCRIMINATED` at semantic level | Entry and Leg-2 start remain separate; exact anchors unresolved |
| F10 | `SOURCE-DISCRIMINATED` at semantic level | Structural invalidation and risk-budget stop remain separate; exact OHLC/wick/body semantics unresolved |
| F11 | `SOURCE-DOES-NOT-DISCRIMINATE` | Refresh is permitted, but deterministic retain/replace threshold unresolved |
| F12 | `SOURCE-DISCRIMINATED` for family; `BLOCKED` for classifier | 1/2/3-candle family confirmed; exact acceptance taxonomy unresolved |
| F13 | `SOURCE-DOES-NOT-DISCRIMINATE` | 2X concept confirmed; universal executable formula unresolved |
| F14 | `SOURCE-DOES-NOT-DISCRIMINATE` | `Leg2 ≈ Leg1` confirmed; A/B/C/D anchors and tolerance unresolved |
| F15 | `BLOCKED` | Bearish mirror not canonicalized without direct source evidence |

## Source-confirmed semantic floor

The current evidence supports the following semantic floor without freezing executable geometry:

1. Pending-limit correction entry is part of the source model.
2. Entry is distinct from the start of Leg 2.
3. Structural invalidation is distinct from risk-budget sizing.
4. A one/two/three-candle trigger family exists in the source material.
5. 2X exists as a source concept, but its universal operational formula is unresolved.
6. AB=CD establishes an approximate Leg-2-to-Leg-1 magnitude relationship.
7. The demonstrated bullish higher-low example supports a dynamic/relevant correction low, but does not establish a universal entry-anchor algorithm.
8. Pending-order refresh can occur, but the deterministic replacement condition is unresolved.

## Remaining blockers to Geometry Freeze

- exact P-Gap executable geometry
- universal relevant Low/High selection algorithm
- exact Entry price/candle anchor
- exact structural invalidation OHLC/wick/body anchor
- exact pending-order retain/replace condition
- deterministic trigger acceptance classifier
- universal 2X operational formula
- exact AB=CD A/B/C/D anchors
- AB=CD equality tolerance
- sufficiently direct bearish evidence for F15
- any unresolved canonical session/time constraint

## Gate decision

**SOURCE RESOLUTION: PARTIAL / IN PROGRESS**

**SYNTHETIC FIXTURES: ADJUDICATED PARTIALLY**

**FROZEN GEOMETRY: BLOCKED**

**DEV / UNTOUCHED VALIDATION / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: LOCKED for Strategy A geometry**

## Non-negotiable boundary

This checkpoint is documentation only. It does not authorize Strategy A engine geometry, canonicalization, validation, Fresh Holdout, or production signals. Canonical promotion still requires explicit manual approval by Ali.
