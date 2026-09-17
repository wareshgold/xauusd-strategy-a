# SP2L Source Visual Resolution — 2026-09-17

## Source artifact inspected

- Uploaded source video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: `4155.666667s`
- Video: `640x360`, `30 fps`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Purpose

Resolve the previously blocked SP2L geometry questions from the original source visual material, without promoting implementation behavior into canonical rules.

## Source windows inspected

### 36:30–37:26 (approx. source timeline)

The source explicitly presents `AB=CD` and draws the pattern as:

1. an initial directional leg from a lower structural point to an upper structural point,
2. a correction back toward a lower structural point,
3. a second directional leg continuing from that correction,
4. with the second leg represented as approximately equal in magnitude to the first.

The same visual segment also contains handwritten `1M` / `5M` annotations.

### 1:02:41–1:03:32

The source shows a concrete bearish chart example with a marked range/position overlay following the preceding directional move and subsequent correction. The visual sequence is consistent with the source's Leg 1 → Correction → Leg 2 construction, but the overlay itself does not uniquely define the exact OHLC field used for entry, stop, or anchor selection.

### 1:04:00–1:04:32

The source continues the bearish example and visually points to structural turning areas during the decline. This provides additional evidence that the construction is discussed in terms of visible structural swings, but it still does not uniquely specify wick-vs-body or another exact OHLC anchor.

## Resolution status

### G4 / Leg 1 endpoints

**PARTIAL SOURCE RESOLUTION — narrowed, not frozen.**

The original source visual material supports treating Leg 1 as a **structural swing-to-swing movement** for conceptual geometry: lower structural point → upper structural point (bullish case), mirrored for bearish construction.

However, the source material inspected does **not** uniquely establish which exact candle field represents each structural point for deterministic implementation. In particular, it does not prove a wick extreme, body extreme, open, close, or another exact OHLC anchor.

Therefore:

- `structural swing endpoints` = **source-supported conceptual geometry**
- exact OHLC mapping = **UNRESOLVED**
- tolerance for `AB=CD` = **UNRESOLVED**
- implementation-level A/B/C/D anchor formula = **UNRESOLVED**

### F10 / stop geometry

**UNRESOLVED.**

The concrete chart overlays inspected do not uniquely establish the canonical stop anchor or its fill semantics. No wick/body rule, buffer, minimum-risk threshold, or replacement rule is inferred from these visuals.

### F14 / AB=CD

**PARTIAL SOURCE RESOLUTION.**

`AB=CD` is directly visible in the source material and the pattern is represented as two approximately equal directional legs separated by a correction. Exact A/B/C/D candle anchors and tolerance remain unresolved.

### F15 / bearish mirror

The inspected bearish example is consistent with a directional mirror of the same structural construction, but no additional mirror-specific implementation rule is promoted to canonical status from the visual evidence alone.

## Gate consequence

This evidence narrows G4 and strengthens the source basis for structural swing geometry, but it does **not** satisfy the Frozen Geometry gate.

The following remain prohibited from being invented to improve statistics:

- exact wick/body anchor selection,
- minimum-risk threshold,
- stop buffer,
- alternate entry formula,
- AB=CD numerical tolerance,
- execution/fill semantics.

The next deterministic research step is to encode the source-supported structural geometry as competing synthetic fixtures whose only differences are the unresolved OHLC anchor semantics, then use source evidence to select the canonical interpretation before validation.
