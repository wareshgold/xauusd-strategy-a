# G356 — Pressure Gap Geometry Source Audit

**Date:** 2026-09-12  
**Gate:** SOURCE RESOLUTION → SOURCE VISUAL DISCRIMINATION  
**Status:** PASS for discrimination; executable P-GAP geometry remains unresolved  
**Issue:** #87  
**Source video:** `gap پورصمدی دوره جامع.mp4`  
**Source SHA-256:** `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`

## 1. Scope

This audit isolates the Pressure Gap material from the newly supplied Poursamadi `PriceAction (Gaps)` lesson and tests whether the source visuals resolve the machine-executable geometry of the SP2L `P-GAP` concept.

The audit is deliberately narrower than a generic gap audit. It does not assume that a visually marked blue gap region is itself a formula, and it does not convert source drawings into OHLC rules unless the source labels those fields or otherwise makes the relationship explicit.

## 2. Source-confirmed findings

### 2.1 P-GAP semantic identity

The SP2L lesson explicitly uses `P-GAP` for `گپ فشار` (Pressure Gap). The gap lesson independently presents `گپ فشار` as a named gap category. Therefore:

`P-GAP ↔ Pressure Gap`

is source-confirmed at the semantic level.

### 2.2 Gap taxonomy remains separate

The gap lesson distinguishes at least:

- Breakout Gap
- Pressure Gap
- Exhaustion Gap
- Common Gap

The source therefore does **not** support collapsing every visually separated candle region into one generic `P-GAP` detector.

### 2.3 Generic bullish gap geometry is source-confirmed, but only for generic gap teaching

The generic gap section explicitly describes the displayed bullish example using the distance between the high of the candle two bars earlier and the low of the current candle. A positive separation is described as a gap.

This is evidence for a **generic bullish gap construction** in that lesson example.

It is **not** sufficient evidence that the same endpoint rule is the canonical executable formula for Pressure Gap / P-GAP.

## 3. Pressure Gap visual discrimination

### Frame around 22:30 / 1350s

The Pressure Gap definition slide describes a sustained directional-pressure context, a temporary stop/pause in that pressure, followed by a trend bar, with increased probability of trend start/continuation.

The slide is contextual/semantic. It does not label a specific gap rectangle with OHLC field names.

### Frames around 1400–1440s

The chart example contains a blue highlighted region associated with the Pressure Gap context. Red annotations describe the surrounding price-action sequence. The highlighted region is visually identifiable, but its upper/lower endpoints are not source-labeled as:

- wick high/low;
- candle body high/low;
- open/close;
- a particular candle index such as `i-2` and `i`;
- or an explicit arithmetic difference.

The same chart contains another highlighted region later in the move, reinforcing that the visual marking is contextual rather than a self-documenting formula.

### Consequence

The Pressure Gap visuals establish **where the presenter considers a Pressure Gap to exist in the example**, but they do not establish a deterministic OHLC endpoint convention.

## 4. Discrimination matrix

| Dimension | Source evidence | G356 result |
|---|---|---|
| P-GAP means Pressure Gap | SP2L transcript + gap taxonomy | **RESOLVED** |
| Generic bullish gap example | High of candle two bars earlier vs current Low | **RESOLVED for generic gap example only** |
| P-GAP = generic gap formula | No explicit source statement | **UNRESOLVED** |
| Pressure Gap endpoint candle indices | Not labeled | **UNRESOLVED** |
| Wick vs body | Not labeled | **UNRESOLVED** |
| Open vs close | Not labeled | **UNRESOLVED** |
| Minimum gap size | Not specified | **UNRESOLVED** |
| Overlap/tolerance | Not specified | **UNRESOLVED** |
| Universal candle-count threshold | Context gives 10–30 candles, not a detector threshold | **UNRESOLVED / CONTEXT ONLY** |
| Pressure Gap → SP2L breakout/FT exact machine relation | Semantic examples exist, exact executable relation absent | **UNRESOLVED** |
| Breakout Gap = P-GAP | Taxonomy contradicts this collapse | **REJECTED** |

## 5. Negative controls

The following promotions remain forbidden:

1. `High[i-2] < Low[i]` → canonical P-GAP without additional source evidence.
2. Any fixed minimum gap size inferred from the chart pixels.
3. Any wick/body rule inferred from the blue rectangle boundary.
4. Any overlap or tolerance inferred from visual approximation.
5. Any universal `10–30 candle` threshold for Pressure Gap detection.
6. Breakout Gap substituted for Pressure Gap merely because both may occur near the beginning of a move.
7. A/B/C/D or fill-price semantics inferred from the gap rectangle.

## 6. Gate decision

**G356 = PASS — SOURCE VISUAL DISCRIMINATION COMPLETE.**

The new visual material strengthens the semantic identity and contextual meaning of Pressure Gap, and confirms that the source uses a highlighted gap/zone in the example. It does **not** resolve the executable P-GAP geometry.

Therefore:

- `P-GAP = Pressure Gap` remains source-confirmed.
- Generic gap geometry remains source-confirmed only at the generic-gap example level.
- Canonical P-GAP endpoint geometry remains blocked.
- FROZEN_GEOMETRY remains blocked.
- DEV/backtest/optimization remains blocked for the canonical strategy.
- No production/live rule changes are justified.

## 7. Next research requirement

A future source-resolution step should search only for genuinely new authoritative material that explicitly ties Pressure Gap to candle-index/OHLC endpoint semantics or an executable charting rule. Repeated measurement of the same blue highlighted rectangles must not be used to manufacture a formula.
