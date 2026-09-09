# SP2L Visual Geometry Triangulation V3 — 2026-09-09

## Scope

Direct frame inspection of the uploaded authoritative source video was combined with the timestamped source transcript. This record is intentionally conservative: visual geometry can narrow a rule without inventing unstated tolerances.

## Finding 1 — Entry line is not the original Spike low in the demonstrated sequence

Frames around 38:40–39:50 show a bullish higher-low sequence. At approximately 38:40 the chart contains multiple marked lows and a horizontal reference line at the earliest low. As the sequence is extended, the horizontal Buy Limit reference is visibly moved upward to the **most recent completed higher-low immediately before the correction**. By approximately 39:30–39:50 the Buy Limit line aligns with the low of the latest bullish candle, while the SL annotation remains below near the original structural low.

This matters because the transcript at 38:38 says correction begins when price comes below the "first low" and that an order can be placed there, while the later visual sequence shows the pending Buy Limit at the currently relevant higher-low. The most coherent source-aligned interpretation is therefore:

`Spike creates a chain of higher lows -> the currently protected/relevant low becomes the pending Buy Limit level -> correction retraces to that level -> structural invalidation is lower at the original/base low.`

The word "first" in the transcript remains semantically ambiguous without an explicit label, so this is classified as **strong visual evidence + strong transcript evidence for a dynamic/relevant-low entry, but not yet universal geometry for every Spike variant**.

## Finding 2 — Entry and SL are distinct structural levels

The same frames show:
- Buy Limit at the latest/relevant higher-low;
- SL below, near the original/base structural low.

Therefore the system must not define SL as a fixed multiple of entry distance and must not collapse Entry and invalidation into one anchor.

## Finding 3 — Pending order can be refreshed as the structure develops

The transcript at 39:48 explicitly permits deleting the prior order and placing a new order based on the updated distance to SL when another candle forms. This matches the visual movement of the reference level upward as the higher-low sequence extends.

The exact rule for when the old order is retained versus replaced is still not deterministic in source language because the teacher uses a qualitative/material-distance judgment.

## Finding 4 — AB=CD is a magnitude relationship, not yet a fully specified four-point algorithm

The source explicitly names AB=CD and later says the next leg is expected to be the same size as the first. However, the direct teaching frames do not label unique A/B/C/D points with unambiguous OHLC semantics.

Current safe representation:

`Leg2Magnitude ≈ Leg1Magnitude`

Current unsafe representations:
- A = arbitrary swing low;
- B = arbitrary spike high;
- C = entry price by assumption;
- D = fixed Fibonacci extension;
- any invented numerical tolerance.

## Finding 5 — P-Gap remains semantically resolved but geometrically blocked

The direct frame around 36:45 visibly contains `AB=CD` and `Valid BO = P-Gap`. The source transcript also distinguishes P-Gap from E-Gap/Common-Gap and ties P-Gap to the breakout construction. The source variants around the Spike teaching section do not justify a single generic three-candle imbalance formula.

## Source-aligned candidate state machine

For the demonstrated bullish variant only:

1. Context/range exists.
2. Directional Spike develops with higher lows.
3. Breakout includes source-recognized P-Gap and follow-through.
4. The latest completed structural higher-low is the relevant pending Buy Limit level.
5. A correction retraces toward/below that level.
6. Structural invalidation remains below the original/base low.
7. If the structure extends before fill, the pending order may be refreshed to the new relevant low, subject to the source's still-qualitative replacement rule.
8. After fill, the second leg is expected to be approximately equal to Leg 1.

This is a **research semantic state machine**, not yet the frozen production algorithm.

## Remaining blockers

1. Exact P-Gap boundary/index/equality rule.
2. Exact definition of "relevant/current higher-low" across all source Spike variants.
3. Exact structural SL OHLC anchor and any spread/buffer treatment.
4. Exact A/B/C/D candle-level anchors.
5. Exact AB=CD tolerance.
6. Exact TP1 formula and relationship to AB=CD.
7. Exact deterministic pending-order replacement condition.
8. Full mirrored bearish confirmation from source visuals.

## Fixture updates

The synthetic suite must now include a dynamic-entry fixture:

### F8 — Moving higher-low / pending-limit refresh

Construct a bullish Spike with three or more successively higher lows. Place a pending Buy Limit at the current relevant higher-low. Add another higher-low before price retraces.

Candidate behaviors:
- retain original order;
- move order to newest higher-low;
- place at original/base low;
- market-entry on close reclaim.

Source evidence currently rejects market-close-reclaim as a replacement for the pending-limit model and visually favors the relevant/current higher-low level, but the universal refresh rule remains unresolved.

## Gate impact

- Source resolution: **advanced**
- Entry geometry: **strongly narrowed; dynamic relevant-low candidate**
- SL geometry: **narrowed to separate base structural low; exact OHLC still unresolved**
- P-Gap geometry: **still blocked**
- AB=CD geometry: **still blocked at anchor/tolerance level**
- Synthetic fixtures: **expanded with F8**
- Frozen geometry: **blocked**
- Historical DEV/VAL/holdout: **locked**
- Production: **unchanged**

## Rule against overreach

The visual discovery in this document is not permission to hard-code `Entry = latest swing low` for every possible SP2L setup. It is a source-supported candidate for the demonstrated higher-low construction that must next be discriminated against the other source examples.
