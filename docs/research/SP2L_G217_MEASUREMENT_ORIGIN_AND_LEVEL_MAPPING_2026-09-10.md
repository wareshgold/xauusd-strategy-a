# SP2L G217 — Measurement Origin and Level Mapping

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Objective

This pass follows the previous G216 recommendation: inspect the earliest appearance of the measurement stack around the first order-panel example, and determine whether the source's `0.0 / 2x / E / 1 / 2` levels can be mapped to the terminal's explicit prices without inventing geometry.

Source video convention: 30 fps, frame = `round(total_seconds × 30)`.

## 2. First-appearance finding

A direct frame sequence around 21:37–21:40 was inspected.

- 21:37.5: the chart is still in the prior hand-annotated breakout view (`sell` marking); the later terminal/measurement state is not yet present.
- ~21:37.6: the video cuts/transitions to the terminal/order view. The measurement stack is already instantiated.
- 21:38.0 and later: the stack is clearly visible with labels `0.0`, `2x`, `E`, `1`, `2`.
- 21:39.0 / frame 39,000: the same stack is visible together with the order panel.

Important conclusion: the video does **not** continuously show the actual drawing gesture that creates the measurement object. The first visible state is a post-cut/post-transition state. Therefore the anchor-construction gesture itself cannot be recovered from these frames.

## 3. Strong mapping from visible price alignment

At frame 39,000 / 21:40 the terminal explicitly shows:

- Order Price / Entry: `3229.08`
- S/L: `3237.12`
- T/P: `3213.44`
- current market Price: approximately `3224.67`

The chart measurement stack is vertically aligned with the same price scale.

### 3.1 `E`

The horizontal line labelled `E` is at the same vertical price level as the terminal's `Price = 3229.08` order field, within the resolution/anti-aliasing limits of the source recording.

This is substantially stronger than the earlier inference from the label alone.

**Status:** `E = terminal order Price` is now a **STRONG SOURCE-CORRELATED MAPPING**, but not yet frozen as a universal rule because this is one independently inspected order state and the source text defining `E` has not been recovered.

### 3.2 `0.0`

The `0.0` line is vertically aligned with the terminal S/L level `3237.12`.

The difference between these two terminal prices is:

`3237.12 − 3229.08 = 8.04`

The vertical distance between the chart's `0.0` and `E` levels is consistent with that same price-scale separation.

**Status:** `0.0 = terminal SL` is a **STRONG SOURCE-CORRELATED MAPPING**, not yet a universal frozen rule.

### 3.3 `2x`

The `2x` line lies approximately halfway between `0.0` and `E` on the chart's price axis.

Using the terminal values:

`3229.08 + (3237.12 − 3229.08)/2 = 3233.10`

This agrees with the visual location of `2x`.

**Status:** the combined mapping

`0.0 = SL`, `E = Entry`, `2x = midpoint(Entry, SL)`

is now strongly mutually consistent for this source state.

### 3.4 `1` and `2`

The `1` and `2` levels are below `E` in this bearish example and therefore appear to be continuation/target-side levels.

The visible `2` level is close to, but not exactly coincident with, the terminal TP `3213.44` at the inspected frame. Because source drawing thickness, chart scaling, and the exact line center introduce measurement uncertainty, this does **not** justify declaring `2 = TP`.

Likewise, no exact formula for `1` or `2` is frozen from this single state.

## 4. Important distinction: source measurement vs order field

The evidence supports a useful hierarchy:

1. The source chart contains a measurement object with named levels.
2. The terminal contains explicit executable prices.
3. In the first inspected order state, `E` and `0.0` align with the terminal Entry and SL, respectively.
4. `2x` is consistent with the exact midpoint of those two executable prices.
5. `1` and `2` remain unresolved target/projection levels.

This is stronger than treating the labels as abstract annotations, but it still does not prove that every setup uses the same object construction or that the terminal fields always correspond one-to-one with the labels.

## 5. Why the construction origin remains unresolved

The transition from the hand-annotated chart to the terminal state occurs between approximately 21:37.5 and 21:37.6. The measurement stack is already present after the transition.

Therefore we cannot truthfully claim from this segment:

- which candle was selected as the measurement origin;
- whether the object was created from A→B, spike→correction, or another pair of anchors;
- whether the chart tool itself generated the `0.0 / 2x / E / 1 / 2` labels or the presenter manually annotated them;
- exact A/B/C/D anchors;
- exact target formula behind `1` and `2`.

This is a hard source-evidence boundary, not a missing implementation detail to be guessed.

## 6. New evidence status

| Mapping / rule | Status |
|---|---|
| `E` aligns with terminal Entry/Price | **Strong source-correlated mapping** |
| `0.0` aligns with terminal SL | **Strong source-correlated mapping** |
| `2x` is midpoint of Entry and SL | **Strong multi-example candidate + direct level alignment** |
| `1` = exact formula | **UNRESOLVED** |
| `2` = exact formula | **UNRESOLVED** |
| `2` = TP | **UNRESOLVED** |
| measurement creation anchors | **UNRESOLVED** |
| A/B/C/D anchors | **UNRESOLVED** |

## 7. Non-inference boundary

This pass does not freeze:

- `Entry = C`;
- a P-Gap formula;
- a specific SL wick/body rule;
- `1 = 1R`;
- `2 = 2R`;
- `2 = TP`;
- any AB=CD anchor/tolerance;
- mandatory trigger logic;
- generic Fibonacci semantics;
- generic FVG semantics.

## 8. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

The most useful new result is that the first order example provides a coherent source-side mapping:

`0.0 ↔ SL`  
`E ↔ Entry/Price`  
`2x ↔ midpoint(Entry, SL)`

while the construction origin and the `1/2` target geometry remain unresolved.

The next highest-value source pass is to locate another independent example where the measurement stack is visible together with a different Entry/SL pair and determine whether the same `0.0/E/2x` mapping repeats, then separately solve `1/2` using explicit source examples rather than assuming risk multiples.
