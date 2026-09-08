# SP2L Source Resolution Checkpoint — Real Chart Follow-up — 2026-09-08

## Scope

Follow-up inspection of the real XAUUSD examples around **50:00–52:00** plus the earlier **61:50–64:30** execution/history segment.

## Findings

### Real chart around 50:00–52:00

The instructor marks several real-chart bullish examples with green rectangles, horizontal levels, circles/arrows, and handwritten annotations. These markings clearly identify areas of interest and trade/management structure, but they do not expose a sufficiently precise numerical OHLC mapping for the P-Gap boundary.

The visible `0.0`, `1`, `2X`, `E`-style labels are management/annotation labels and must not be reinterpreted as harmonic A/B/C/D points.

### Cross-check against execution history

The later order-history table supplies exact entry and SL numbers for several trades, but the chart view does not provide a sufficiently trustworthy price-axis/candle mapping to prove which exact candle OHLC endpoint generated each number.

Therefore the combination of:

`real chart annotation + order-history price`

still does not uniquely resolve the P-Gap formula or exact SL anchor.

## Resolution update

The source-resolution hierarchy now has a clear boundary:

**Resolved strongly:**
- SP2L = Spike → 2 Leg concept.
- Spike is a strong directional movement following range/breakout context.
- Valid breakout is associated with P-Gap.
- P-Gap is not equivalent to every visible gap.
- P-Gap is strongly associated with a non-overlap/gap at breakout/early trend context.
- Correction is part of the setup.
- Pending-limit entry is canonical execution semantics.
- Entry is strongly associated with the correction returning to the relevant prior candle extreme (Low bullish / High bearish).
- SL is structural invalidation rather than a universal fixed-distance stop.
- Leg 2 follows correction and is tied to Leg 1 magnitude.
- AB=CD is a source concept, but classical harmonic/Fibonacci anchor import is not justified.

**Still unresolved:**
- exact P-Gap candle pair and boundaries;
- wick vs body semantics;
- equality/touch rule;
- minimum P-Gap size/tolerance;
- exact prior/relevant candle definition across Spike variants;
- exact SL candle/price anchor;
- exact Leg-1 origin;
- exact AB=CD measurement anchors and tolerance;
- intrabar fill/invalidation ordering;
- universal TP executable formula and relation of TP1/TP2 to the displayed real trades.

## Gate decision

**SOURCE RESOLUTION:** substantially narrowed, but **not complete**.  
**FROZEN GEOMETRY:** remains blocked.  
**SYNTHETIC FIXTURES:** ready for competing hypotheses, but no unresolved hypothesis may be labeled canonical merely because it performs better.  
**DEV / VAL / HOLDOUT:** remain locked for canonical Strategy A.

## Important project decision

Do not spend additional research effort reverse-fitting the few real trades. Their correct role is constraint evidence, not parameter-fitting data.

The next valid gate transition requires either:

1. new authoritative source evidence that explicitly resolves the remaining geometry; or
2. an explicit documented `UNRESOLVED` state for the remaining components, followed by a decision that the project cannot truthfully freeze Strategy A without them.

**Production change: none.**
