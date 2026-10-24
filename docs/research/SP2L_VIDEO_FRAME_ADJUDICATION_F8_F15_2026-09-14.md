# SP2L Video Frame Adjudication — F8–F15 — 2026-09-14

## Scope

This research artifact records a second-pass, frame-by-frame inspection of the user-supplied source video `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4` at the previously identified evidence windows.

It is evidence/provenance only. It does not define canonical Strategy A geometry.

## Source integrity

- Duration: `01:09:15.721723`
- Video: `640x360`, `30 fps`, H.264
- Source SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Window 1 — 36:58–37:22

### Observations

The teaching slide visibly contains the candle construction together with the explicit labels `Valid BO = P-Gap` and `AB=CD`. Additional handwritten annotations reference 1M/5M context/timeframes.

### Adjudication

- F14 semantic AB=CD relationship: `SOURCE-DISCRIMINATED`.
- P-Gap as valid-breakout association: `SOURCE-DISCRIMINATED`.
- Exact P-Gap candle indices: `SOURCE-DOES-NOT-DISCRIMINATE`.
- Exact P-Gap OHLC boundaries: `SOURCE-DOES-NOT-DISCRIMINATE`.
- Exact A/B/C/D anchors: `SOURCE-DOES-NOT-DISCRIMINATE`.
- Equality tolerance: `SOURCE-DOES-NOT-DISCRIMINATE`.

Reason: the visual is a schematic teaching diagram, not a coordinate-labelled OHLC chart.

## Window 2 — 38:35–39:55

### Observations

The bullish teaching sequence shows several successive low references under the rising candle construction. The teacher draws/updates horizontal reference levels and explicitly labels the order `Buy Limit` / `BuyLimit`. A separate lower horizontal reference is labelled `SL`. The final simplified diagram retains the Buy Limit level above the lower SL level.

### Adjudication

- F8: relevant correction-level concept strengthened; universal exact anchor remains `SOURCE-DOES-NOT-DISCRIMINATE`.
- F9: Entry is visually separate from the lower SL/invalidation representation; exact Leg-2-start relationship remains governed by the existing ledger.
- F10: separate Entry and SL/invalidation levels are directly visible; exact wick/body/OHLC boundary remains unresolved.
- F11: the sequence supports order management evolving with structure, but no deterministic retain/replace threshold can be extracted.
- Market-close-reclaim replacement is not supported by this teaching sequence.

Reason for unresolved exact anchor: the drawing does not expose price-scale or unambiguous OHLC endpoint semantics.

## Window 3 — 1:02:40–1:03:32

### Observations

The chart shows a bearish directional sequence with lower-high/lower-low structure and a correction/range region. No unambiguous candle-level A/B endpoint labels are visible in the sampled frames.

### Adjudication

- F15 bearish directional structure: `SOURCE-DISCRIMINATED`.
- F15 complete deterministic mirror: `BLOCKED`.
- Exact bearish A/B endpoint geometry: `BLOCKED`.

Reason: directional symmetry is visible, but the frames do not expose every executable endpoint needed for a deterministic mirrored algorithm.

## Window 4 — 1:04:00–1:04:40

### Observations

A bearish chart sequence continues lower after a correction. A red horizontal order/reference marker is visible around a corrective lower-high region before subsequent continuation.

### Adjudication

- Bearish order-before-continuation concept: `SOURCE-DISCRIMINATED`.
- Exact bearish entry price: `BLOCKED`.
- Exact bearish invalidation/SL OHLC boundary: `BLOCKED`.
- Exact bearish P-Gap geometry: `BLOCKED`.
- Exact bearish AB=CD anchors/tolerance: `BLOCKED`.

## F8–F15 final disposition after direct-video second pass

| Fixture | Result | Canonical geometry unlocked? |
|---|---|---|
| F8 Entry correction level | `SOURCE-DOES-NOT-DISCRIMINATE` | No |
| F9 Entry vs Leg-2 start | Existing separation retained; exact anchor unresolved | No |
| F10 Invalidation vs risk stop | Structural separation confirmed; OHLC unresolved | No |
| F11 Pending refresh | Structure-dependent update supported; threshold unresolved | No |
| F12 Trigger family | 1/2/3-candle family remains confirmed; classifier unresolved | No |
| F13 2X / TP1 / TP2 | Unresolved | No |
| F14 AB=CD anchors/tolerance | Magnitude relationship supported; exact anchors/tolerance unresolved | No |
| F15 Bearish mirror | Bearish order/continuation observed; deterministic mirror blocked | No |

## Research gate impact

The direct video artifact materially strengthens the evidence base for:

- P-Gap being associated with valid breakout.
- Pending Limit execution.
- Separate Entry and SL/invalidation levels.
- Bullish correction-order structure.
- Bearish order-before-continuation structure.
- AB=CD as a source relationship.

It does **not** uniquely resolve the executable geometry blockers.

Therefore:

- SOURCE RESOLUTION: evidence strengthened; blockers remain.
- SYNTHETIC FIXTURES: F8–F15 adjudication evidence strengthened.
- FROZEN GEOMETRY: `BLOCKED`.
- DEV: locked.
- UNTOUCHED VALIDATION: locked.
- ROBUSTNESS/STABILITY: locked.
- FRESH HOLDOUT: locked.
- PRODUCTION: locked.

## Non-negotiable boundary

No formula, tolerance, anchor, buffer, fill semantic, or execution rule is inferred from visual appearance alone. No profitability or historical backtest result is used to select among unresolved interpretations. Canonical promotion remains subject to explicit manual approval by Ali.