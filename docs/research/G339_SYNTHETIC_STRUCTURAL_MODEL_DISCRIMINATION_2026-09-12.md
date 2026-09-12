# G339 — Synthetic Structural-Model Discrimination

Date: 2026-09-12  
Parent gate: G338  
Scope: synthetic fixtures only; no historical market data

## Objective

Discriminate among source-compatible structural interpretations without allowing backtest performance to select a geometry. G338 established that the source semantically distinguishes a deep-leg origin, a later parent Leg-1 endpoint, correction, pending-limit execution, and a larger/nested leg hierarchy, while leaving exact candle/OHLC mapping unresolved.

## Fixture design

`G339_SOURCE_COMPATIBLE_FIXTURE` encodes the semantic sequence:

`context range → deep-leg origin → spike → parent Leg-1 endpoint → lower-high correction structure → correction reference → pending-limit → fill → Leg-2 endpoint`

The fixture deliberately gives pending-limit and fill their own events. It therefore cannot silently collapse execution into the geometric correction anchor.

`G339_NESTED_FIXTURE` contains two distinguishable structural scales. The parent measurement and nested measurement intentionally produce different magnitudes, demonstrating why an implementation must not select the first visually obvious swing as the parent leg.

## Candidate interpretations tested

| Candidate | Fixture treatment | Canonical status |
|---|---|---|
| `SOURCE_DEEP_ORIGIN` | explicit semantic event | NOT SELECTED |
| `FIRST_BREAKOUT_CANDLE` | competing interpretation | NOT SELECTED |
| `NEAREST_SWING` | competing interpretation | NOT SELECTED |
| `FILL_AS_C` | competing interpretation | REJECTED BY SOURCE BRIDGE |
| `SOURCE_CORRECTION_REFERENCE` | explicit semantic event | NOT SELECTED |

The test suite asserts that every candidate remains non-canonical. G339 is a discrimination gate, not a geometry-freezing gate.

## Source-aligned invariants demonstrated

1. Deep-leg origin precedes correction and execution.
2. Correction is distinct from pending-limit placement.
3. Pending-limit placement is distinct from actual fill.
4. Parent and nested leg scales can coexist in the same price series.
5. No wick/body selection is encoded.
6. No AB=CD tolerance is encoded.
7. No historical performance is used to choose among candidates.

## Deliberate non-goals

This gate does **not** define:

- A/B as specific candle fields;
- C as a specific OHLC field;
- wick versus body semantics;
- a universal swing/fractal algorithm;
- a seven-lower-high count rule;
- executable D arithmetic;
- AB=CD tolerance;
- TP1/TP2 mapping;
- P-Gap geometry.

## Validation

The suite is under the research namespace and is registered as `test:sp2l-g339`. It is intended to run alongside the existing repository test suite. Production strategy logic is unchanged.

## Gate decision

**G339 = PASS WITH GEOMETRY UNRESOLVED**

The fixtures successfully preserve and discriminate the source's semantic distinctions, but they do not create new source evidence capable of freezing A/B/C/D OHLC semantics. Therefore:

`FROZEN_GEOMETRY = BLOCKED`  
`DEV = BLOCKED`  
`VAL = PROTECTED`  
`FRESH_HOLDOUT = LOCKED`  
`PRODUCTION = BLOCKED`

## Next source-first direction

The next useful gate should target the remaining executable anchor ambiguity using additional source evidence or explicitly labelled source frames. If no source evidence resolves wick/body or A/B/C mapping, the ambiguity must remain represented as competing models rather than being optimized away.
