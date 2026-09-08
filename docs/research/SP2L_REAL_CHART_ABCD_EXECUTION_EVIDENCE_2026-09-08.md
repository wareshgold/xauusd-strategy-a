# SP2L Real-Chart A/B/C/D + Execution Evidence

Date: 2026-09-08
Branch: `research/source-resolution-entry-level-v2`

## Purpose

Inspect the later real-chart / execution examples in the uploaded full source video after the teaching sections, with emphasis on whether the source itself exposes A/B/C/D labels, entry levels, structural stop levels, and actual order prices.

This is source-resolution evidence only. It does not freeze geometry and does not authorize production changes.

## Source-video provenance

Source asset:
`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

The uploaded video is the same 69:15 SP2L source referenced by the public Telegram post, which lists:

- four trades performed during the recording before the teaching;
- the difference between four candle Spike types;
- P-Gap;
- order placement;
- the 2X entry;
- ten entry examples on 13 May 2025;
- later detailed teaching of the four initial trades.

The public Telegram post also states that a Persian subtitle was prepared, but the uploaded MP4 itself has no embedded subtitle stream according to local media inspection. The Telegram statement is therefore a provenance lead, not a substitute for the missing subtitle asset.

## Finding 1 — Real chart explicitly exposes A/B/C/D-style labels

Around video time ~62:30, the source switches to a real XAUUSD chart and displays horizontal reference levels with small letter labels. At the inspected raster resolution, the labels visually correspond to an A/B/C/D-style sequence on the chart.

This is materially stronger than the earlier 29:00–41:50 teaching drawings because the labels are overlaid on a real market chart rather than only on a schematic.

However, the available 640x360 source raster and the compressed enlarged frame do not provide enough certainty to map every letter to a unique OHLC anchor without risk of misreading the label or point. Therefore:

- `A/B/C/D labels visibly used on a real chart`: SOURCE-VISUAL CONFIRMED
- exact A anchor: STILL UNRESOLVED
- exact B anchor: STILL UNRESOLVED
- exact C anchor: STILL UNRESOLVED
- exact D anchor: STILL UNRESOLVED
- whether the labels refer to candle extrema, closes, candle bodies, or manually selected price levels: UNRESOLVED

The key advance is that A/B/C/D is no longer supported only by the handwritten `AB=CD` teaching annotation; the later real-chart material appears to use explicit lettered reference levels.

## Finding 2 — Actual XAUUSD execution table is shown

Around video time ~60:30, the source shows the platform's XAUUSD account/order history. Four visible rows include the following prices:

| Entry/Price | S/L | T/P | Closing Price | Observed Profit |
|---:|---:|---:|---:|---:|
| 3229.08 | 3237.73 | 3213.37 | 3223.36 | 118.40 |
| 3223.84 | 3235.50 | 3213.37 | 3223.36 | 10.60 |
| 3228.88 | 3235.50 | 3213.37 | 3223.36 | 112.80 |
| 3232.41 | 3237.80 | 0.00 | 3223.36 | 364.40 |

These values are transcribed from the visible execution table and should be treated as source-video observations, not as a canonical target rule.

The rows demonstrate that the recorded execution contains multiple entries with different entry/SL distances and a shared TP in at least part of the example. Consequently, the observed execution cannot safely be reduced to a universal `TP = entry ± risk` rule from this example alone.

The fourth row has no visible TP (`0.00`) and was closed at 3223.36, further showing that recorded execution includes management behavior that is not equivalent to a single fixed TP formula.

## Finding 3 — Execution examples materially complicate the target rule

Using the visible prices only as arithmetic observations:

- 3229.08 → 3237.73 has risk 8.65 and TP distance 15.71.
- 3223.84 → 3235.50 has risk 11.66 and TP distance 10.47.
- 3228.88 → 3235.50 has risk 6.62 and TP distance 15.51.
- 3232.41 → 3237.80 has risk 5.39, with no displayed TP and a close at 3223.36.

These ratios differ materially. This is consistent with the source presenting additional execution/order-management modules (including 2X) rather than one simplistic universal reward formula.

The authoritative published page separately states a default 1:1 TP and a possible secondary entry at 50% of entry-to-SL distance. That published statement must be reconciled with the full-video examples before a canonical TP/2X rule is frozen.

## Finding 4 — Real-chart evidence supports, but does not yet solve, C

The later chart examples show multiple horizontal reference levels around the impulse/correction area. Combined with the explicit AB=CD teaching earlier in the video, this materially strengthens the hypothesis that the source uses named geometric points rather than an arbitrary close-reclaim trigger.

But the evidence still does not prove:

```text
C == Buy/Sell Limit price
```

nor does it prove that C is the high/low of a particular correction candle.

Therefore the following remain prohibited:

- setting `entry = C` without source confirmation;
- defining C as a candle low/high merely because it visually aligns with an entry level;
- deriving AB/CD tolerance from these examples;
- using the observed execution ratios to select a target rule.

## Finding 5 — Public source metadata gives a high-value transcript lead

The public Telegram source explicitly lists both the initial four trades and a later detailed explanation of those same four trades. It also states that a Persian subtitle was prepared. This identifies a high-value missing artifact: the actual Persian subtitle/transcript for the source video.

If recovered, the highest-value timestamp ranges are approximately:

1. 38:40–41:50 — Limit / Buy Limit / SL / 2X mechanics;
2. 56:00–60:30 — real chart and execution examples;
3. 62:00–65:00 — real chart A/B/C/D-style labeling and later execution review;
4. any spoken explanation immediately around the first four trades.

## Gate impact

### Newly strengthened

- Real-chart A/B/C/D-style labeling: **SOURCE-VISUAL CONFIRMED**
- Real execution prices and SL/TP examples: **SOURCE-VISUAL CONFIRMED**
- Multiple-entry/order-management behavior: **SOURCE-VISUAL CONFIRMED**

### Still unresolved

- exact A/B/C/D OHLC anchors;
- exact P-Gap executable geometry;
- exact C/Entry equivalence;
- AB=CD tolerance;
- canonical relationship between default 1:1 TP and the recorded multi-entry/2X examples.

### Gate state

Canonical geometry remains **BLOCKED**.

DEV, VAL, robustness, Fresh Holdout, and Production remain unchanged.

## Guardrail

No heuristic from the real-chart execution examples is promoted to production merely because it can be measured or appears profitable. These examples are being used to resolve source meaning, not to optimize a strategy.
