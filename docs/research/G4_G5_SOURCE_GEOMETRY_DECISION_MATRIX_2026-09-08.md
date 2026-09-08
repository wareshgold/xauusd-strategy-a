# SP2L G4/G5 Source Geometry Decision Matrix

Date: 2026-09-08
Branch: `research/source-aligned-sp2l-semantics-v1`

## Purpose

Freeze the current visual evidence state without converting ambiguous drawings into executable geometry.

This document is a research record. It is not a canonical rule specification and does not authorize production changes.

## Evidence reviewed

The supplied SP2L video excerpt and extracted visual frames around the initial teaching sequence were inspected. The visible material contains:

- `SP2L Strategy / Spike - 2Leg`;
- handwritten `AB = CD`;
- handwritten `1M / 5M` notation;
- printed `Valid BO = P-Gap`;
- a hand-drawn multi-wave sequence showing an impulse/spike, pullback/correction, and continuation;
- a marked horizontal structural/reference line in the drawing;
- a circled visual point near the upper portion of the illustrated move.

## G4 — Leg 1 A/B geometry

### Source-confirmed

The source confirms that the first leg used in the AB=CD construction has identifiable visual endpoints. The exact OHLC coordinate identity of those endpoints is not yet explicit enough in the available raster evidence to freeze.

### Candidate interpretations retained

1. Structural swing low/high -> spike extreme.
2. Breakout/reference level -> spike extreme.
3. Spike start -> spike end.
4. Relevant candle open -> spike extreme.
5. Other explicitly marked visual anchor in the teacher's drawing.

### Decision

**NOT FROZEN.**

No candidate may be selected because it gives better historical performance.

## G5 — Leg 2 C geometry

### Source-confirmed

The second leg follows a correction before continuation. The source also demonstrates pending-limit entry during the correction.

### Candidate interpretations retained

1. Correction extreme.
2. Structural higher-low / lower-high.
3. Explicitly marked visual correction anchor.
4. Other source-defined point that can be identified from a higher-resolution frame.

### Explicit exclusions

- Pending-limit fill price is not automatically C.
- Entry price is not automatically C.
- A generic retracement percentage is not C unless source-confirmed.

### Decision

**NOT FROZEN.**

## P-Gap

The excerpt confirms the semantic relationship `Valid BO = P-Gap`, but does not provide sufficient coordinate/OHLC detail to derive a unique executable formula.

Therefore:

- generic three-candle imbalance remains research-only;
- no gap-size threshold is authorized;
- no candle-index formula is authorized;
- no ATR/tick/percentage condition is authorized;
- P-Gap remains a source-resolution blocker for canonical implementation.

## AB = CD

Status: **SOURCE-CONFIRMED**.

The source explicitly displays `AB = CD`. The implementation may use the equality relationship only after A/B/C are source-confirmed. No tolerance is inferred from the visual material.

## Current gate state

| Gate | State |
|---|---|
| Source semantics | materially resolved |
| P-Gap semantic relationship | resolved |
| P-Gap executable geometry | unresolved |
| G4 A/B | unresolved |
| G5 C | unresolved |
| G6 AB=CD relationship | resolved |
| Synthetic discrimination fixtures | complete |
| Canonical geometry freeze | blocked |
| DEV | blocked for canonical SP2L |
| VAL | locked / untouched |
| Fresh Holdout | locked |
| Production | unchanged |

## Required next evidence

The next useful source evidence is not another generic backtest. It is higher-resolution chart material in which the teacher's marked A/B/C/D points and P-Gap boundaries are visible at candle/price-coordinate level.

Until that evidence exists, the correct deterministic state is **UNRESOLVED**, not a guessed formula.
