# SP2L G225 — P-Gap vs Generic Gap Geometry Cross-Check

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `P-GAP_GEOMETRY_STILL_UNRESOLVED`

## Objective

Cross-check the P-Gap examples in the raw SP2L video against the same-author comprehensive Gap-course definition, without promoting a generic Gap definition to canonical P-Gap geometry.

## Source assets

### Raw SP2L video

- File: `strtjy_sp2l_strategy_subtitle_7hec5mO3d3U_7899aa08.mp4`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- Duration: ~4155.67 s
- FPS: 30
- Resolution: 640x360
- Primary P-Gap teaching window: ~30:00–36:16

### Comprehensive Gap course

- File: `gap پورصمدی دوره جامع.mp4`
- SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`
- Duration: ~1955.77 s
- FPS: 30
- Resolution: 854x480

## Direct source observations

### 1. Generic Gap geometry is explicitly described in the Gap course

Around 17:00–18:00 in the Gap course, the slide states in Persian that attention should be paid to the distance between the **high of the candle two bars before** and the **low of the current candle**; if there is a distance, a Gap has formed.

This is direct same-author source evidence for a generic bullish three-candle gap relation of the form:

`High[t-2] < Low[t]`

for the bullish case. The bearish mirror is semantically expected from the chart examples, but its exact textual OHLC formulation was not frozen here.

**Important:** this establishes a generic `Gap` definition only. It does **not** by itself establish that `P-Gap` in SP2L is exactly this relation.

### 2. Breakout Gap is a separate named Gap category

Around 20:00 in the Gap course, the source explicitly states:

- when a Gap occurs at the beginning of a move, it is a **Breakout Gap**;
- the displayed example is labelled as a bullish Breakout Gap;
- the source text additionally states that, in this case, the close of the relevant candle is at the previous high.

The accompanying chart marks the Gap area and the breakout context.

This supports a taxonomy in which `Breakout Gap` is a contextual subtype/concept, not simply an arbitrary synonym for every Gap.

### 3. SP2L explicitly labels P-Gap as a valid-breakout condition

Around 35:55–36:16 in the raw SP2L video, the source displays multiple examples with shaded Gap regions and the explicit text:

`Valid BO = P-Gap`

The examples are numbered and include both valid-looking P-Gap constructions and an invalid example marked with a red X.

Around 32:00–32:10 the source also visibly writes `P-GAP` separately from `GAP / Common`, which is strong evidence that the SP2L term is not intended to be treated as an unqualified synonym for generic/common Gap.

## Cross-check result

The evidence now supports the following hierarchy:

`Generic Gap` — source-defined OHLC relation  
`Breakout Gap` — source-defined contextual Gap category  
`P-Gap` — SP2L-specific term explicitly tied to valid breakout

The exact equivalence among these three remains unresolved.

In particular, the following are **not frozen**:

- `P-Gap = Generic Gap`
- `P-Gap = Breakout Gap`
- `P-Gap = Pressure Gap`
- `P-Gap = FVG`
- exact P-Gap candle indexing
- exact P-Gap OHLC boundaries
- wick vs body treatment
- overlap/non-overlap rule
- whether the SP2L P-Gap requires the additional Breakout-Gap condition concerning close/location

## Visual comparison

The SP2L P-Gap examples use shaded zones spanning a local candle structure around the directional move. At source resolution, the drawings are sufficient to establish that the author is identifying a discrete Gap region, but they are not sufficient to uniquely recover all OHLC boundaries from pixels alone.

The Gap-course examples independently show shaded Gap regions consistent with the generic `t-2 high` versus `t low` construction. This is useful corroboration but is not enough to prove identity with SP2L P-Gap.

## Decision

**B1 remains unresolved at executable geometry.**

The new source evidence materially narrows the hypothesis space but does not justify implementing a canonical P-Gap formula.

### Permitted research candidate

The following may be used only in explicitly labelled research/fixture modules:

- generic Gap candidate: bullish `High[t-2] < Low[t]`, mirrored for bearish;
- contextual Breakout-Gap candidate: Gap at beginning of directional move plus the source-described breakout/close context.

### Production prohibition

Do not implement either candidate as canonical SP2L P-Gap logic until the raw SP2L source uniquely resolves the mapping.

## Next source-resolution target

Return to the SP2L P-Gap teaching sequence (~35:45–36:16) and inspect the three numbered examples frame-by-frame, identifying for each shaded P-Gap zone the exact participating candles and whether the zone boundaries coincide with the generic Gap-course relation. If the source does not uniquely reveal the boundaries, preserve `UNRESOLVED`.

## Gate impact

- Source Resolution: **BLOCKED at P-Gap executable geometry**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**
- No trading rule, threshold, or production code changed by this research pass.
