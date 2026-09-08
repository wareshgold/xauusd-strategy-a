# SP2L G4/G5 Source Geometry Decision Matrix

Date: 2026-09-08
Branch: `research/source-aligned-sp2l-semantics-v1`

## Purpose

Freeze the current visual evidence state without converting ambiguous drawings into executable geometry.

This document is a research record. It is not a canonical rule specification and does not authorize production changes.

## Full-source evidence — 36:00–41:50

The full 01:09:15.667 source video has now been inspected frame-by-frame around the highest-value teaching sequence. Exact frame-addressed observations are registered in `docs/research/SP2L_FULL_VIDEO_FRAME_EVIDENCE_2026-09-08.md`.

Directly visible source elements include:

- `SP2L Strategy / Spike - 2Leg`;
- `Valid BO = P-Gap`;
- repeated handwritten `AB=CD`;
- `1M / 5M` notation;
- a multi-wave / impulse-correction-continuation drawing;
- a horizontal reference level;
- explicit `BO` and `Limit` annotations;
- explicit `Buy Limit` annotation;
- explicit `SL` annotation below the lower structural area;
- a separate `2X` module/level.

### Important new execution evidence

Around 38:40–39:50 the teacher resets to a simplified bullish candle example, marks a horizontal reference level, writes `Limit`, then `BO`, and subsequently writes `Buy Limit` and `SL`. This is direct evidence that the demonstrated entry mechanism is a pending limit order associated with the illustrated reference/breakout structure.

However, the visual material still does not explicitly label the horizontal order level as geometric `C`, nor does it expose enough OHLC detail to prove that the order price, C, breakout level, or another source-defined anchor are identical. Therefore this evidence strengthens the pending-limit rule but does not freeze G5.

### Important new target/risk evidence

The same sequence shows `PT` and later a separate `2X` annotation with vertical distance measurements. The 2X material is explicitly treated as a separate module and is not silently promoted to the core SP2L target rule.

## Earlier supplied video segment — 2026-09-08

A second uploaded video was inspected. Its duration is approximately **14:52**, so it does not contain the previously requested 01:02:00–01:07:00 source-video timestamps. The useful educational material in that file is approximately **02:20–08:45**, followed by MetaTrader/chart examples from approximately **08:50 onward**.

The additional segment provides stronger visual evidence for the source's teaching grammar:

- approximately 02:40–03:40: a hand-drawn sequence of successive directional waves;
- approximately 04:20–05:40: a more developed two-move illustration with circled regions and directional annotations;
- approximately 07:40–08:45: an explicit worked drawing with numbered points/steps (`1`, `2`, `3`), two large circled move regions, a horizontal reference line, a correction/return path, and a continuation toward a later marked point.

The numbered marks in the available raster frames appear to identify teaching steps/points, but they do **not** unambiguously establish source labels `A/B/C/D` or exact OHLC candle coordinates. The frame also does not expose a unique executable P-Gap boundary.

The chart/order-history material after approximately 08:50 is treated as execution/example evidence only. It is not used to infer geometric anchors without an explicit source statement connecting the order price or chart point to A/B/C/D.

**Decision impact:** the second segment materially strengthens the existence of a repeatable spike → correction → continuation / two-leg teaching structure, but it does **not** freeze G4, G5, or the executable P-Gap formula.

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

The second leg follows a correction before continuation. The source also demonstrates pending-limit entry during the correction. The full-source execution sequence strengthens this entry fact: `Limit` and `Buy Limit` are explicitly written next to the illustrated horizontal level.

### Candidate interpretations retained

1. Correction extreme.
2. Structural higher-low / lower-high.
3. Explicitly marked visual correction anchor.
4. Breakout/reference level if and only if a future source statement explicitly identifies it as the AB=CD C point.
5. Other source-defined point that can be identified from a higher-resolution frame or transcript.

### Explicit exclusions

- Pending-limit fill price is not automatically C.
- Entry price is not automatically C.
- A generic retracement percentage is not C unless source-confirmed.
- The illustrated horizontal Buy Limit level is not automatically C merely because it is visually prominent.

### Decision

**NOT FROZEN.**

## P-Gap

The full-source teaching slide directly displays `Valid BO = P-Gap`. This resolves the semantic relationship more strongly than the earlier excerpt alone.

The executable P-Gap geometry remains unresolved. The source material inspected so far does not expose enough candle-coordinate detail to derive a unique formula without interpretation.

Therefore:

- generic three-candle imbalance remains research-only;
- no gap-size threshold is authorized;
- no candle-index formula is authorized;
- no ATR/tick/percentage condition is authorized;
- P-Gap remains a source-resolution blocker for canonical implementation.

## AB = CD

Status: **SOURCE-CONFIRMED**.

The source explicitly displays `AB = CD` and repeatedly reinforces it during the teaching sequence. The implementation may use the equality relationship only after A/B/C are source-confirmed. No tolerance is inferred from the visual material.

## 2X

Status: **SOURCE-CONFIRMED AS A DISTINCT MODULE**.

The full-source sequence explicitly marks `2X` separately from the basic Buy Limit / SL construction. It must remain a separate source module until the relationship between 2X and the canonical SP2L TP rule is explicitly resolved.

## Current gate state

| Gate | State |
|---|---|
| Source semantics | materially resolved |
| SP2L = Spike → 2Leg | resolved |
| AB=CD semantic relationship | resolved |
| Pending-limit entry semantics | strongly resolved |
| Structural SL placement | strongly resolved |
| 2X as distinct module | resolved |
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

The next useful source evidence is now narrower than before:

1. spoken/subtitle text during **36:00–39:50**;
2. sub-second inspection at the exact moments the teacher draws the AB/CD arrows and horizontal reference level;
3. the four-spike-type teaching section, to map the numbered examples to the actual spike taxonomy;
4. the source's explicit verbal definition of where the Buy Limit is placed relative to the P-Gap, breakout, correction, and AB=CD construction.

Until those relationships are source-confirmed, the correct deterministic state is **UNRESOLVED**, not a guessed formula.
