# SP2L Direct Video Frame Extraction — 2026-09-14

## Purpose

Record direct visual inspection of the user-supplied source video corresponding to the authoritative SP2L video `7HEC5mO3d3U`.

This is a research evidence artifact only. It does not canonicalize executable Strategy A geometry.

## Source artifact

- Local source file: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: `01:09:15.721723`
- Video: H.264, 640x360, 30 fps
- Audio: AAC, 44.1 kHz
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Direct frame observations

### 1. 36:59–37:22 — P-Gap / AB=CD teaching diagram

Direct inspection shows a whiteboard teaching diagram with a directional candle sequence and the explicit labels `Valid BO = P-Gap` and `AB=CD`. The same segment also contains handwritten timeframe/context annotations.

Source-safe conclusion:

- P-Gap is explicitly associated with a valid breakout in this visual teaching segment.
- AB=CD is explicitly presented as a relationship in the segment.
- The frame does **not** provide machine-readable OHLC coordinates or a unique candle-index formula for P-Gap.
- The frame does **not** uniquely define A/B/C/D anchors or an equality tolerance.

Disposition: `SOURCE-DISCRIMINATED` for the semantic associations; `SOURCE-DOES-NOT-DISCRIMINATE` for executable P-Gap geometry and exact AB=CD anchors/tolerance.

### 2. 38:40–39:50 — bullish order-placement teaching sequence

Direct frame extraction shows a bullish candle construction with several higher lows. The teacher draws multiple candidate horizontal levels, labels the execution as a Buy Limit, marks a separate lower SL reference, and later simplifies the diagram to a Buy Limit line above a lower structural level marked as SL.

Source-safe conclusion:

- Pending-limit execution is visually confirmed.
- Entry and SL are visibly represented as separate levels.
- The demonstrated construction is consistent with a structurally relevant correction level rather than a market-close-reclaim model.
- The frames alone do **not** uniquely establish a universal `Entry = latest HL` rule, an exact OHLC anchor, wick/body semantics, or a deterministic order-refresh threshold.

Disposition: `SOURCE-DISCRIMINATED` for Pending Limit and Entry/SL separation; `SOURCE-DOES-NOT-DISCRIMINATE` for universal entry anchor and refresh rule.

### 3. 1:02:41–1:03:32 — bearish structural example

Direct inspection shows a bearish chart sequence with lower-high/lower-low structure and a separate correction/range region. The available frames do not expose a unique candle-level A/B endpoint annotation sufficient to freeze Leg-1 geometry.

Source-safe conclusion:

- Bearish directional structure is visually present.
- The visual evidence does not uniquely define a deterministic mirrored executable geometry for all Strategy A dimensions.
- No bearish mirror rule is promoted from this segment alone.

Disposition: `BLOCKED` for deterministic bearish mirror and exact A/B endpoint extraction.

### 4. 1:04:00–1:04:32 — bearish order/leg sequence

Direct inspection shows a bearish chart sequence with a red order marker/level appearing around a corrective structural area, followed by continuation lower. The chart demonstrates a placed order and subsequent directional movement, but the frame set does not uniquely identify every OHLC anchor needed for deterministic execution.

Source-safe conclusion:

- The segment provides additional direct visual evidence that bearish examples use an order placed before subsequent continuation.
- It does not uniquely determine exact entry price, structural invalidation OHLC boundary, fill semantics, or AB=CD endpoints.

Disposition: `SOURCE-DISCRIMINATED` for the existence of the demonstrated bearish pending-order sequence; `BLOCKED` for full deterministic bearish geometry.

## Cross-check against existing geometry ledger

This direct inspection strengthens, but does not overturn, the existing evidence boundary:

- Pending Limit: confirmed.
- Entry distinct from Leg-2 start: retained.
- Entry distinct from structural invalidation: confirmed.
- Structural invalidation distinct from risk-budget sizing: retained.
- `Leg2Magnitude ≈ Leg1Magnitude`: retained.
- P-Gap semantic association with valid breakout: confirmed.
- Exact P-Gap OHLC/candle-index formula: unresolved.
- Exact Entry anchor: unresolved.
- Exact SL/invalidation OHLC boundary: unresolved.
- Pending-order refresh threshold: unresolved.
- Exact 1/2/3-candle trigger classifier: unresolved.
- Exact 2X/TP1/TP2 formulas: unresolved.
- Exact A/B/C/D anchors and AB=CD tolerance: unresolved.
- Deterministic bearish mirror: unresolved.

## Governance result

This artifact is **new direct visual evidence**, but it does not uniquely resolve any previously blocked executable geometry dimension.

Therefore:

- no canonical geometry is added;
- no production code changes are authorized;
- no historical optimization is performed;
- Frozen Geometry remains `BLOCKED`;
- DEV / Untouched Validation / Robustness / Fresh Holdout / Production remain locked.

## Reopening rule

A later source-resolution pass may use this artifact as provenance, but a blocker should only move toward canonical review when direct source evidence uniquely discriminates the executable rule and Ali explicitly approves the canonical transition.
