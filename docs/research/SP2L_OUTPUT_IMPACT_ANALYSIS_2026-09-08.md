# SP2L Output Impact Analysis

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION → shadow-impact analysis  
**Production:** unchanged

## 1. Objective

Measure how much of the existing Strategy A output is attributable to assumptions that are not source-confirmed, without using profitability to resolve source meaning.

This is an impact analysis, not a canonical backtest and not a validation result.

## 2. Baseline actually present in repository

The baseline runner uses breakout/follow-through heuristics, a spike heuristic, generic context filters, a correction-extreme close-reclaim entry, and a candidate Leg2 projection. These are legacy implementation choices, not a frozen Strategy A specification.

## 3. Existing baseline output

### 1-minute

- candles: 10,000
- source: TwelveData
- period: 2026-08-20 13:05 through 2026-08-27 11:44
- trades: 338
- wins: 96
- losses: 242
- win rate: 28.40%
- average/expectancy: +0.1208R
- profit factor: 1.1687
- max drawdown: 101.4471R
- max consecutive losses: 15

### 5-minute

- candles: 10,000
- source: TwelveData
- period: 2026-07-23 18:25 through 2026-08-27 11:40
- trades: 241
- wins: 78
- losses: 163
- win rate: 32.37%
- average/expectancy: -0.1055R
- profit factor: 0.8440
- max drawdown: 36.6972R
- max consecutive losses: 11

These numbers are baseline observations only. They must not be interpreted as performance of canonical SP2L.

## 4. Source-confirmed changes that can already be assessed

### 4.1 Entry semantics: material change

The baseline entry is a later candle close reclaim of the correction extreme. The source transcript explicitly describes placing a Buy Limit during correction, including before waiting for another candle, and says the order may already be placed within the first three candles.

Therefore the baseline entry event is **source-contradicted**, not merely an alternative implementation.

The source says the bullish correction moves below the first low and that the order can be placed “there”; the teaching diagram shows a horizontal Buy Limit level during the correction. This narrows the candidate entry anchor toward a structural candle level, but it still does not provide a sufficiently explicit OHLC mapping to freeze an exact formula.

### 4.2 P-Gap: hard gate, geometry unresolved

The source slide explicitly states `Valid BO = P-Gap`. The transcript links P-Gap to breakout location and describes a non-overlap/gap relationship in multiple candle constructions.

The source does not yet provide a sufficiently unambiguous formula for candle boundaries, indices, wick/body treatment, or tolerance. The existing generic P-Gap detector therefore cannot be promoted to canonical.

### 4.3 Spike: semantic alignment is stronger, executable taxonomy remains open

The transcript explicitly says three states are considered and treated as Spike: breakout followed by continuation/higher lows; higher lows followed by the gap; and a third three-candle construction. The first two are stated to have the same nature and are intentionally grouped in this strategy.

This now supports a deterministic **three-variant taxonomy candidate** for synthetic fixture work, but exact candle predicates remain to be frozen from the visual examples.

### 4.4 Leg2 / AB=CD: concept confirmed, anchors unresolved

The source explicitly writes `AB=CD` and connects it to the 2Leg concept. The executable A/B/C/D OHLC mapping is still unresolved.

Therefore equality is canonical as a concept, but no anchor mapping or AB=CD tolerance is invented, and `entry = C` is not assumed.

### 4.5 Stop/invalidation: semantic alignment

The source demonstrates structural SL placement and says the scenario is invalid if price returns to the invalidation area. Exact structural anchor mapping still needs final geometry confirmation.

### 4.6 Target / 2X: substantially narrowed, still separate

The transcript explicitly says TP1 or TP2 may be used, that the instructor generally uses TP1, and that TP2 is relatively large for this strategy; it then states that the TP “should be 1” in that context. This strongly supports a **base 1:1 risk/reward target** as the default execution module.

However, the source also describes the second-leg target geometrically and separately describes 2X/second-position management. We must still resolve whether the geometric AB=CD endpoint, TP1=1R, and the optional 2X position are separate levels/modules or how they map to each other.

### 4.7 Round levels: source-supported context, exact filter use still open

The transcript explicitly rejects taking the setup at arbitrary market locations and then points to different levels, including round levels, as useful locations. It gives gold examples such as 3200, 3250, and 3255 and discusses point-based spacing for scalping/swinging.

This corrects the prior classification: **round-level context is source-supported.** What remains unresolved is the exact deterministic mapping from broker/feed precision to point spacing and whether the baseline `roundStep=50` / `roundDistance=5` implementation matches the source's intended use.

### 4.8 Session / volume: do not freeze as filters yet

The source discusses high-volume locations as useful, but the inspected material does not establish a deterministic session-time filter for the core strategy. Keep session as descriptive/research metadata until a canonical rule is explicitly resolved.

## 5. Shadow classification of current baseline

| Baseline component | Source status | Impact classification |
|---|---|---|
| Breakout + follow-through | confirmed semantically | potentially retained |
| Generic Spike heuristic | not frozen | unresolved / research-only |
| Generic P-Gap formula | not source-confirmed | blocked |
| Close-reclaim entry | contradicted by pending-limit evidence | must be replaced |
| Pending-limit representation | source-confirmed | required |
| Structural invalidation | source-confirmed semantically | retain concept; freeze anchor |
| Leg1 geometry | not fully anchored | blocked |
| Leg2 = Leg1 / AB=CD | confirmed conceptually | retain concept; freeze anchors |
| AB=CD tolerance | unresolved | blocked |
| EMA filter | no canonical source evidence established | research-only |
| Round-level context | source-supported | exact deterministic filter still open |
| Session filter | no deterministic core filter established | research-only/descriptive |
| TP1 ≈ 1:1 | strongly source-supported | exact relation to AB=CD still open |
| 2X management | separate source module | do not merge into base target |

## 6. Source-video visual evidence

The uploaded source video was inspected directly at the key teaching sections.

- **36:00:** slide states `Valid BO = P-Gap`; multiple Spike constructions are shown and one is explicitly marked with a red X.
- **36:30–37:00:** instructor writes `AB=CD` above the SP2L example, confirming the relationship but not uniquely labelling A/B/C/D.
- **38:45–39:40:** teaching diagram is annotated with `BO`, `Limit` / `Buy Limit`, and `SL`; this directly corroborates pending-limit execution during correction.
- **~62:20–63:00:** real XAUUSD execution material shows numbered structural levels and subsequent results, but the compressed recording is insufficient to freeze an exact A/B/C/D OHLC mapping.

## 7. What can be said about output impact now

1. The baseline's close-reclaim trades are not valid representations of the source's pending-limit execution model.
2. The generic P-Gap detector cannot be treated as a canonical filter until its source geometry is frozen.
3. Round-level context is source-supported, but the baseline's exact numerical implementation remains unverified.
4. EMA and session filters remain unsupported as canonical core filters from the inspected material.
5. Baseline expectancy/PF cannot be carried forward as Strategy A evidence because entry, stop, target, and fill semantics are not source-frozen.
6. 1M and 5M baseline results already disagree in expectancy sign, reinforcing the need for untouched validation rather than parameter selection.

## 8. Required next executable comparison

Once P-Gap and A/B/C/D geometry are frozen, run the same immutable dataset through:

**A — Legacy baseline**: current repository baseline, unchanged.  
**B — Source-semantic shadow**: only source-confirmed gates and pending-limit mechanics; unresolved geometry returns an explicit blocked state.  
**C — Frozen canonical SP2L**: full deterministic source specification after geometry freeze.

Persist row-level dispositions such as `RETAINED`, `REMOVED_PGAP`, `REMOVED_SPIKE_VARIANT`, `REMOVED_CONTEXT`, `ENTRY_CHANGED`, `FILL_UNRESOLVED`, `STOP_CHANGED`, `TARGET_CHANGED`, and `BLOCKED_SOURCE_GEOMETRY`.

Compute candidate/trade attrition, pending-order fill rate, entry/stop/target deltas, R distribution and median R, expectancy, PF, drawdown, loss streak, long/short split, and descriptive time-of-day results.

## 9. Gate decision

**SOURCE RESOLUTION: PROGRESSING**  
**SHADOW IMPACT ANALYSIS: COMPLETE FOR CURRENT EVIDENCE**  
**FROZEN GEOMETRY: BLOCKED**  
**DEV/VAL: NOT AUTHORIZED**  
**PRODUCTION: UNCHANGED**

The next research target is source-geometry resolution using the recovered transcript, direct video frames, and synthetic fixtures, especially P-Gap boundaries, the pending-limit structural anchor, A/B/C/D mapping, and the relationship between 1R TP1 and the AB=CD endpoint.

## 10. Provenance

Source video SHA256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`  
Transcript SHA256: `47f867385338738a23b2d06dc48e67b852127243`
