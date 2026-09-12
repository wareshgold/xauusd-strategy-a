# SP2L G209 — Source Evidence Matrix (B1-B6)

Date: 2026-09-10  
Scope: research/source-resolution only. This document does **not** freeze executable geometry and does not authorize DEV, validation, or production.

## Evidence provenance

Primary source identity is registered in the persistent Treasure Path as `SP2L_FULL_2026-09-08`. The source registry records the supplied MP4 fingerprint, 30 fps frame convention, and the indexed high-value windows. The registry explicitly separates raw video, extracted frames, transcript/subtitles, frozen specification, implementation, and historical research.

High-value direct observations recorded by the source registry include:

- 36:00 / frame 64,800 — `SP2L Strategy / Spike-2Leg`, shaded P-Gap region, and `Valid BO = P-Gap`.
- 36:10 / frame 65,100 — three numbered constructions with P-Gap shown.
- 36:30 / frame 65,700 — explicit `AB=CD` and `Valid BO = P-Gap`.
- 37:00 / frame 66,600 — `AB=CD` with `1M / 5M`.
- 37:20 / frame 67,200 — multi-wave sequence.
- 38:40 / frame 69,600 — bullish sequence with horizontal reference and correction/continuation.
- 39:40 / frame 71,400 — explicit `Buy Limit` at a horizontal entry level and lower `SL`.
- 40:20 / frame 72,600 — order-line `Delete` handling.
- 42:30 / frame 76,500 — TP1 / TP2 / Entry / SL shown together.

## B1-B6 resolution matrix

| Blocker | Source evidence currently available | What is source-confirmed | What remains unresolved | Gate status |
|---|---|---|---|---|
| B1 — P-Gap / valid breakout | 36:00–36:10; `Valid BO = P-Gap`; shaded P-Gap region | P-Gap is a first-class source-defined breakout condition | Exact participating candles, exact OHLC/range boundaries, overlap/non-overlap rule, executable formula | **SOURCE-UNRESOLVED** |
| B2 — Entry | 38:40–40:00; explicit horizontal level and `Buy Limit` | Entry is pending-limit during the correction structure | Exact anchor/price mapping; whether entry equals C or another source-defined level | **SOURCE-UNRESOLVED** |
| B3 — Structural SL | 39:40 and 42:30; lower `SL` shown | Structural invalidation/SL is distinct from entry and is explicitly demonstrated | Exact invalidation boundary; wick/body treatment; deterministic placement formula | **SOURCE-UNRESOLVED** |
| B4 — Trigger | Source priority region includes trigger discussion; examples around spike/candle taxonomy | Trigger is a source topic requiring source interpretation | Accepted 1/2/3-candle/key-bar trigger, timing, precedence, and exact executable condition | **SOURCE-UNRESOLVED** |
| B5 — AB=CD | 36:30–37:00; `AB=CD` explicitly shown | AB=CD magnitude relationship is directly source-confirmed | Exact A/B/C/D anchors and any equality tolerance | **SOURCE-UNRESOLVED** |
| B6 — Leg 2 / TP | 37:20–38:40 continuation; 42:30 TP1/TP2; 44:30 target-distance discussion | Second-leg continuation and TP1/TP2 concepts are source-supported | Exact Leg-2 projection formula from Leg 1; exact TP anchor(s), precedence and execution semantics | **SOURCE-UNRESOLVED** |

## Spike geometry sub-blocker

The 25:00–35:30 source region contains multiple candle/spike constructions and P-GAP annotations. This is useful for resolving spike grammar, but the current registry does not establish a unique deterministic threshold or OHLC formula. Therefore no numeric spike threshold is promoted here.

## Explicit non-inferences

The following are deliberately **not** promoted to canonical rules:

1. P-Gap is not equated with a generic three-candle imbalance/FVG.
2. A/B/C/D anchors are not selected by backtest performance.
3. Fill price is not assumed to equal geometric C.
4. No AB=CD tolerance is invented.
5. Pending-limit is not replaced by a market close-reclaim trigger.
6. Visually similar candles are not converted into numeric thresholds without source evidence.
7. Liquidity sweep, BOS/MSS, displacement, FVG, retest, session filters, or other external terminology are not treated as canonical without source evidence.

## Transcript provenance boundary

The registered MP4 is documented as video + audio without an embedded subtitle stream. Consequently this matrix does not claim that a complete transcript artifact is registered. If a separately provenance-identified transcript is recovered, it must be linked as a separate source artifact and cannot silently override raw visual evidence.

## Gate decision

**Result: SOURCE RESOLUTION remains BLOCKED at executable geometry.**

The evidence is sufficient to preserve several semantic meanings as source-confirmed, but insufficient to derive production-safe deterministic OHLC rules for B1-B6. The correct action is to continue frame-level source inspection and synthetic discrimination, not to optimize or implement candidate geometry.

## Required next evidence pass

Priority order:

1. Fine-grained frame extraction around 30:00–34:30 for P-Gap/spike construction.
2. Fine-grained frame extraction around 36:00–37:10 for P-Gap and AB=CD drawings.
3. Fine-grained frame extraction around 38:30–40:10 for entry/C/SL mapping.
4. Fine-grained frame extraction around 42:00–44:40 for TP/target semantics.
5. Locate and provenance-check any previously reconstructed transcript artifact before using textual claims as source evidence.

No implementation or production rule should be changed solely from this matrix.
