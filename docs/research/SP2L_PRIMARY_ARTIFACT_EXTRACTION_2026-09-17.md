# SP2L Primary Artifact Extraction — 2026-09-17

## Status

`RESEARCH_ONLY / SOURCE EVIDENCE / NON-CANONICAL`

This record is based on direct inspection of the user-supplied MP4 artifact corresponding to the author-associated SP2L training video (`7HEC5mO3d3U`). The artifact duration is approximately 69m16s and contains video plus audio. This pass uses direct visual frames from the supplied artifact; it does not infer missing geometry from implementation behavior or backtest results.

## Primary-artifact evidence inspected

### E01 — AB=CD visual teaching segment

**Observed interval:** approximately `00:36:45–00:37:20`.

Direct visual observations:

- The slide identifies the method as `SP2L Strategy — Spike - 2Leg`.
- `AB=CD` is explicitly handwritten and boxed at the top of the slide.
- An arrow connects the AB=CD annotation to the teaching diagram.
- `1M` and `5M` are handwritten beside the diagram, indicating that multiple chart/timeframe contexts are being discussed in this segment.
- The candlestick teaching diagram is explicitly labeled `Valid BO = P-Gap`.
- The visible diagram contains a directional candle sequence, but no explicit A/B/C/D point labels are drawn on the visible frame.

**Resolution:**

`AB=CD CONCEPT = DIRECTLY CONFIRMED`

`LEG-MAGNITUDE RELATION = DIRECTLY SUPPORTED`

`A/B/C/D EXECUTABLE ANCHORS = NOT DISCRIMINATED`

The direct artifact therefore strengthens the source evidence for AB=CD, but it does not by itself establish which candle OHLC values or structural pivots are A, B, C, and D.

### E02 — P-Gap / 2X / order-placement transition

**Observed interval:** approximately `00:38:10–00:39:40`.

Direct visual observations:

- The same teaching diagram is marked with the P-Gap/breakout sequence.
- A handwritten `2X` appears during the continuation of the example.
- The later frame explicitly labels `Buy Limit` and shows a horizontal order level.
- A lower horizontal level is marked as `SL` in the subsequent frame.

**Resolution:**

`P-GAP ROLE = DIRECTLY VISUALIZED`

`2X CONCEPT = DIRECTLY VISUALIZED`

`BUY-LIMIT CONCEPT = DIRECTLY VISUALIZED`

`SL CONCEPT = DIRECTLY VISUALIZED`

Exact price anchors, fill semantics, and deterministic update/replacement behavior remain unresolved.

### E03 — TP1 / TP2 / Entry / SL teaching diagram

**Observed interval:** approximately `00:42:30`.

The frame visibly labels four horizontal/structural levels as `TP2`, `TP1`, `Entry`, and `SL` around the example structure.

This confirms the existence and ordering of these named trade-management concepts in the primary artifact. It does not expose a deterministic formula for their exact price construction.

## What the primary artifact does NOT establish in this pass

The inspected visual evidence does **not** uniquely determine:

- A anchor definition;
- B anchor definition;
- C anchor definition;
- D anchor definition;
- wick vs body vs open vs close semantics;
- exact candle indexing;
- numeric AB=CD tolerance;
- exact P-Gap boundary formula;
- exact Buy Limit price formula;
- exact SL price formula;
- fill semantics;
- pending-order replacement/deletion rules;
- exact 2X formula.

No such rule is promoted merely because the diagram can be visually approximated.

## Source-resolution consequence

This primary-artifact pass changes the evidence quality, but **does not close the Frozen Geometry gate**.

### Updated gate

- Primary artifact accessible: `PASS`
- AB=CD concept: `SOURCE-CONFIRMED`
- Leg-2 approximately equals Leg-1: `SOURCE-SUPPORTED`
- A/B/C/D anchors: `BLOCKED`
- AB=CD tolerance: `BLOCKED`
- P-Gap executable formula: `BLOCKED`
- Entry/SL executable formulas: `BLOCKED`
- Fill semantics: `BLOCKED`
- Frozen Geometry: `BLOCKED`
- DEV: `LOCKED`
- Untouched Validation: `LOCKED`
- Robustness/Stability: `LOCKED`
- Fresh Holdout: `LOCKED`
- Production: `OFF`

## Next discriminator

The highest-value next action is **frame-by-frame extraction around the actual drawing/annotation transitions**, especially:

1. `00:36:45–00:37:30` for any transient A/B/C/D or measurement marks that are not visible in sparse snapshots;
2. `00:38:10–00:40:20` for exact Buy Limit / SL visual placement;
3. `00:42:20–00:42:50` for TP1/TP2/Entry/SL construction;
4. `00:58:00–00:59:15` for the 2X example;
5. `01:02:41–01:04:32` for the bearish counterpart.

Any frame-level discriminator will be promoted only if the artifact itself uniquely specifies the executable dimension. Otherwise the dimension remains `BLOCKED`.

## Non-negotiables

- No invented geometry.
- No inferred symmetry beyond what the artifact explicitly teaches.
- No generic technical-analysis convention.
- No backtest-based geometry selection.
- No tolerance mining.
- No production BUY/SELL generation.
- Historical validation remains locked until Frozen Geometry is source-resolved and frozen.
