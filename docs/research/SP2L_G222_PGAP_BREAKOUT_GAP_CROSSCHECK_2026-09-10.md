# SP2L G222 — Breakout Gap ↔ P-Gap Cross-Check

Date: 2026-09-10
Status: SOURCE-CORRELATED / EXECUTABLE GEOMETRY STILL UNRESOLVED
Gate: SOURCE RESOLUTION

## Purpose

Targeted comparison of the same-author comprehensive Gap-course video with the raw SP2L source video, specifically to determine whether the course's Breakout Gap definition uniquely resolves the P-Gap geometry used by SP2L.

## Source assets

### Comprehensive Gap course
- File: `gap پورصمدی دوره جامع.mp4`
- Duration: ~1955.7667 s (32:35.77)
- FPS: 30
- Frames: 58,673
- Resolution: 854x480
- SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`
- Relevant frame convention: nominal zero-based frame ~= round(t*30).

### Raw SP2L source
- File: `strtjy_sp2l_strategy_subtitle_7hec5mO3d3U_7899aa08.mp4`
- Duration: ~4155.67 s (69:15.67)
- FPS: 30
- Resolution: 640x360
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Evidence A — comprehensive Gap course

At approximately 20:00 (course frame ~36,000), the source explicitly states:

> زمانیکه یک گپ در ابتدای یک حرکت ایجاد می شود، آن یک بریک اوت گپ است

Meaning: when a gap is created at the beginning of a move, it is a Breakout Gap.

The same slide labels the bullish case as **بریک اوت گپ صعودی** and states that in this case the closing price of the referenced candle is at the previous high. The subsequent chart sequence (approximately 20:20–22:00) visually demonstrates the Breakout Gap around a trendline breakout and a prior reference level.

Important: this is authoritative same-author evidence for the semantics of **Breakout Gap**. It is not, by itself, a unique candle-index/OHLC formula for SP2L P-Gap.

## Evidence B — raw SP2L source

Around 30:00–32:30, the raw SP2L source develops the spike examples and then explicitly labels **P-GAP**. Around 35:45–36:16 the source shows three numbered examples with shaded P-Gap regions and the explicit text:

**Valid BO = P-Gap**

Representative raw-source frames inspected:
- 31:30 (frame 56,700): three-candle example with the source's hand-drawn P-Gap reference.
- 32:00 (frame 57,600): explicit `P-GAP` annotation.
- 35:50 (frame 64,500): `Valid BO = P-Gap` and shaded example.
- 35:55 (frame 64,650): same construction.
- 36:00 (frame 64,800): three numbered examples / shaded regions.
- 36:15 (frame 65,250): numbered examples remain visible.

The raw SP2L visuals strongly support that P-Gap is a first-class breakout-validity condition and that the visual construction is applied to a local candle sequence. However, the source resolution and hand-drawn overlays do not uniquely expose all participating OHLC boundaries.

## Cross-reference result

### What is now stronger

1. **Breakout Gap is a real source-defined category**, not an invented interpretation.
2. The comprehensive course defines it by occurrence at the beginning of a directional move.
3. The raw SP2L source independently states **Valid BO = P-Gap**.
4. Therefore the semantic relationship between **breakout-validity gap** and **P-Gap** is now materially stronger than before.
5. The comprehensive course's bullish example also introduces a prior-high/closing-price relationship that is relevant to the SP2L breakout context.

### What is NOT established

The evidence does **not** uniquely establish that:

- P-Gap = every Breakout Gap;
- P-Gap uses the exact same candle indexing as the generic Breakout Gap examples;
- P-Gap is a generic three-candle imbalance/FVG;
- the gap boundaries are `high(C1)` to `low(C3)` (or the bearish mirror);
- wick or body boundaries are canonical;
- overlap/non-overlap rules are canonical;
- a minimum numeric gap size exists;
- the prior-high closing condition is the complete P-Gap definition;
- the shaded rectangle's visual edges are exact OHLC anchors rather than explanatory annotation.

## Research decision

**Do not freeze B1.**

Current B1 status:

`P-Gap semantic role: SOURCE-CONFIRMED`

`Breakout Gap corroboration: STRONG`

`P-Gap executable OHLC geometry: UNRESOLVED`

`Generic FVG equivalence: NOT ESTABLISHED`

## Next targeted source pass

The highest-value next pass is not another generic Gap example. It is to inspect the exact moment in the raw SP2L source where the P-Gap shaded region is constructed, preferably an example where the drawing action and all three/four participating candles are visible continuously without a cut. The goal is to determine whether the source explicitly identifies the two boundary prices, the candle indices, or the relation to the prior high/low.

If no such continuous construction exists, the correct output remains an unresolved B1 geometry rather than an invented formula.

## Gate impact

- SOURCE RESOLUTION: **BLOCKED at B1 executable geometry**
- FROZEN GEOMETRY: **BLOCKED**
- DEV/VAL/production: **unchanged and prohibited from using an invented P-Gap formula**
