# SP2L Spike Source Resolution — 2026-09-08

## Purpose

Register the detailed inspection of the full source video around the Spike teaching section and reconcile it with the authoritative SP2L page. This is evidence only. It does not freeze unresolved geometry or authorize production changes.

## Source asset

- Video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: 01:09:15.667
- FPS: 30
- Resolution: 640x360
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Detailed visual inspection: 29:00–35:30

### 29:00–30:00 — four illustrated spike examples

The source displays four separate bullish candle constructions side-by-side. They are circled/isolated as distinct examples and then progressively annotated. The examples differ in candle sequencing and relative candle size, but the available raster evidence does not expose authoritative names for the four variants.

**Decision:** record as `SPIKE_VARIANT_1..4` visual examples only. Do not invent variant names or numerical candle rules.

### 30:00–32:00 — progressive annotation

The teacher adds arrows and handwritten marks to the first examples. The drawings emphasize the directional movement and the candle-level structure. The annotation is educational and schematic; it does not provide a machine-readable P-Gap formula.

**Decision:** supports spike as a directional candle sequence and source-specific visual classification; does not freeze executable spike thresholds.

### 32:00–33:30 — P-Gap / level teaching

A prominent handwritten `P-GAP` / `GAP` annotation appears with a continuation note. Horizontal levels are progressively added to candle examples. The visual grammar clearly connects the valid spike construction to a price gap and subsequent continuation/level behavior.

A later frame around 33:10 shows multiple horizontal marks on the first candle sequence and a separate `Buy` annotation on another sequence. These marks are visually important, but the letter-like annotations cannot safely be mapped to AB=CD A/B/C/D labels from the raster evidence alone.

**Decision:** P-Gap semantic relationship is strengthened; executable P-Gap geometry remains unresolved.

### 33:30–35:30 — valid/invalid examples and entry direction

The source places a large red X over one example while the other examples receive directional annotations. `Buy` and `Sell` are explicitly shown in the teaching diagram. The visual sequence reinforces that the setup is directional and that not every sharp-looking candle construction is accepted.

**Decision:** source supports directional validity filtering, but no exact rejection predicate is promoted to canonical without explicit source wording.

## Authoritative website corroboration

The official SP2L page states that a Spike is a strong sudden movement, usually consisting of several large consecutive candles in one direction, and that a valid Spike has a price gap (P-Gap) between candles. It explicitly states that a sharp movement without a gap is not considered valid in the strategy.

The same official page states the second-leg trigger more concretely:

- bullish case: wait for the corrective candle to reach the low of the previous candle;
- bearish case: wait for the corrective candle to reach the high of the previous candle.

It then states that the trade is entered in the Spike direction, with SL behind the candle from which the Spike originated, and default TP at 1:1 risk/reward.

This is authoritative corroboration for the **entry trigger and structural SL semantics**. It is not used to invent P-Gap candle boundaries or AB=CD anchors.

## What can now be promoted to source-confirmed semantics

1. Spike is a strong directional movement composed of multiple candles in the source's teaching examples.
2. A valid Spike requires a P-Gap; sharp movement without the required gap is invalid.
3. After the Spike, the corrective candle reaching the prior candle's low (bullish) / high (bearish) is the source-described second-leg trigger.
4. Entry direction follows the Spike.
5. SL is placed behind the candle from which the Spike originated.
6. Default TP is 1:1 on the official page.

## What remains unresolved

- Exact P-Gap formula / candle indices / price boundaries.
- Exact A/B coordinates for the `AB=CD` construction.
- Exact C coordinate and whether it is identical to the pending-limit level.
- Any numerical tolerance for AB=CD.
- Exact deterministic rejection predicate represented by the red-X examples.
- Names and executable definitions of the four visually illustrated Spike variants.

## Research guardrails

- Do not replace source P-Gap with a generic three-candle imbalance.
- Do not infer A/B/C/D from the letter-like annotations in low-resolution frames.
- Do not infer numerical spike thresholds from third-party indicators.
- Do not use historical profitability to choose among source-geometry candidates.
- Keep production unchanged until geometry is frozen and all validation gates pass.

## Gate impact

| Gate | State |
|---|---|
| Source semantic resolution | materially advanced |
| Spike semantics | strengthened / partially source-confirmed |
| Entry trigger semantics | source-confirmed |
| Structural SL semantics | source-confirmed |
| Default TP semantics | source-confirmed on official page |
| P-Gap executable geometry | unresolved |
| G4 A/B | unresolved |
| G5 C | unresolved |
| AB=CD relationship | source-confirmed |
| Canonical geometry freeze | blocked |
| DEV | blocked for canonical SP2L |
| VAL | untouched |
| Fresh Holdout | locked |
| Production | unchanged |
