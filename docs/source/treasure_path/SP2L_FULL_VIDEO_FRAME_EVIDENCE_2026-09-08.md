# SP2L Full Video — Frame-by-Frame Evidence Register

Date: 2026-09-08
Source asset: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
Duration: 01:09:15.667
FPS: 30.0
Frames: 124,670

## Purpose

This register records source visual evidence from the complete uploaded SP2L video. It is an evidence ledger, not a canonical rule specification. No geometry is promoted to production solely from visual resemblance or backtest performance.

## Treasure Path

This file belongs under `docs/source/treasure_path/` and must be treated as the persistent source-evidence index for future research sessions.

The full video has been uploaded in the current research workspace. The repository stores provenance and evidence findings; the binary media is intentionally not committed to Git.

## High-value source windows identified in the full video

| Time | Evidence | Status |
|---|---|---|
| 25:00–27:30 | SP2L Strategy title/intro and candle examples | source evidence |
| 27:30–32:00 | illustrated candle/spike examples and annotations | source evidence; geometry requires interpretation |
| 32:00–35:30 | further candle examples, annotated spike/candle structures | source evidence |
| **36:00–37:20** | **explicit `Valid BO = P-Gap`; examples numbered 1/2/3; `AB=CD`; `1M / 5M`** | **high priority** |
| **37:20–38:40** | **hand-drawn wave sequence showing continuation after correction** | **high priority** |
| **38:40–40:20** | **BUY LIMIT annotation and horizontal pending-entry level; SL shown below structure** | **high priority** |
| 40:20–44:30 | order/SL/TP mechanics, deletion/order-management annotations, TP1/TP2 examples | source evidence |
| 44:30 onward | additional target/round-number and trade-management material | source evidence |

## Key frame observations

### 36:00–36:20 — P-Gap examples

The slide explicitly displays `SP2L Strategy / Spike - 2Leg`. Multiple bullish candle constructions are shown. A shaded rectangular region is drawn around a candle-area structure and the printed text reads `Valid BO = P-Gap`.

At approximately 36:10 the examples are explicitly numbered `1`, `2`, and `3`. This is stronger evidence that the teacher distinguishes specific breakout/candle constructions rather than treating every directional move as valid.

**Important limitation:** the raster image does not yet expose enough exact OHLC coordinate detail to derive a unique P-Gap formula. The shaded region must not be translated into a generic three-candle imbalance without further source confirmation.

### 36:30–37:10 — AB=CD

The source explicitly writes `AB=CD` above the SP2L example. Around 37:00 the source additionally writes `1M / 5M`.

This confirms the equality relationship and the relevant timeframes shown in this teaching section. It does **not** by itself identify the exact A, B, C and D OHLC anchors or a numeric tolerance.

### 37:20–38:40 — two-leg wave grammar

The teacher draws a multi-wave sequence containing an initial directional movement, correction/pullback, and continuation. The drawing reinforces the Spike → correction → second-leg construction.

The available frame does not unambiguously label A/B/C/D, so candidate anchors remain unresolved.

### 38:40–40:20 — pending-limit entry

The source shows a bullish candle sequence with a horizontal reference level. Around 39:40 the handwritten annotation explicitly reads `Buy Limit`, with an arrow to the horizontal level. A lower horizontal line is annotated `SL`.

This is direct visual evidence for a pending-limit entry placed at a defined price level during/around the correction structure. It is incompatible with silently replacing the canonical entry with a later market-close reclaim.

**Still unresolved:** the exact rule mapping the horizontal pending-limit price to geometric C and the precise structural stop anchor.

### 40:00–44:30 — order/target mechanics

The source demonstrates order-line manipulation and later marks TP1/TP2 and SL. These frames are useful for execution semantics and target research, but they should not be used to infer unresolved A/B/C/D geometry without explicit source explanation.

## Current source-resolution conclusions

1. `SP2L = Spike - 2Leg` is directly visible.
2. `Valid BO = P-Gap` is directly visible.
3. `AB = CD` is directly visible.
4. `1M / 5M` is directly visible in the same teaching sequence.
5. Pending-limit entry is directly demonstrated (`Buy Limit`).
6. Structural SL is visually demonstrated below the relevant bullish structure in the example.
7. G4 (exact Leg-1 A/B OHLC anchors) remains unresolved.
8. G5 (exact Leg-2 origin/C anchor) remains unresolved.
9. P-Gap executable formula remains unresolved.
10. No AB=CD tolerance is sourced by these frames.
11. Entry/fill price must not be automatically equated with C.

## Required next extraction

The next frame-by-frame pass should focus on:

- 25:00–35:30 for the teacher's candle/spike taxonomy;
- 36:00–38:40 for P-Gap, AB=CD and wave geometry;
- 38:40–44:30 for pending-limit, SL, TP1/TP2 and order semantics;
- later trade examples only after the educational definitions above are mapped.

For each candidate geometry, record:

`timestamp → frame number → visible marking → semantic role → candidate OHLC anchor → confidence → unresolved questions`

No candidate becomes canonical until the visual evidence uniquely supports it.

## Gate status

**SOURCE RESOLUTION: IN PROGRESS**

**SYNTHETIC FIXTURES: available and research-only**

**FROZEN GEOMETRY: blocked on G4/G5/P-Gap**

**DEV / VAL / Fresh Holdout / Production: unchanged and gated**
