# SP2L Output Impact Analysis

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION → shadow-impact analysis  
**Production:** unchanged

## 1. Objective

Measure how much of the existing Strategy A output is attributable to assumptions that are not source-confirmed, without using profitability to resolve source meaning.

This is an impact analysis, not a canonical backtest and not a validation result.

## 2. Baseline actually present in repository

The baseline runner uses:

- breakout lookback = 5 bars;
- follow-through window = 2 bars;
- spike maximum = 8 candles;
- directional fraction = 0.5;
- overlap fraction = 0.8;
- EMA/context filter;
- round-number location filter;
- London/New York session context;
- correction-extreme close-reclaim entry;
- candidate Leg2 projection from the correction.

The runner then produces one candidate per replay event and evaluates SL/TP against subsequent OHLC bars.

These are implementation choices of the legacy baseline, not source-frozen Strategy A rules.

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

Expected output effect:

- some baseline entries disappear because no pending order would have been placed at that later close;
- some canonical entries will occur earlier as pending orders;
- fill status becomes a separate state from signal detection;
- entry price, risk, target, and R can all change.

No numerical attrition percentage is asserted because the pending-limit price is not yet source-frozen.

### 4.2 P-Gap: hard gate, but geometry unresolved

The source slide explicitly states `Valid BO = P-Gap`. The transcript also links P-Gap to breakout location and describes a non-overlap/gap relationship in multiple candle constructions.

The source does **not** yet provide a sufficiently unambiguous formula for candle boundaries, indices, wick/body treatment, or tolerance.

Therefore the existing generic P-Gap detector cannot be used as a canonical replacement. Historical output cannot honestly be filtered by it and called source-aligned until the geometry is frozen.

### 4.3 Spike: semantic alignment is stronger, executable taxonomy remains open

The source identifies Spike as a strong directional movement following range and describes breakout/follow-through and several visually distinct constructions as Spike. The source slide also rejects at least one visually similar construction.

Therefore the baseline spike heuristic should not be treated as canonical. A deterministic variant taxonomy still needs to be frozen from the source examples.

### 4.4 Leg2 / AB=CD: concept confirmed, anchors unresolved

The source explicitly writes `AB=CD` and connects it to the 2Leg concept. However, the source material inspected does not uniquely define A/B/C/D from OHLC coordinates.

Consequently:

- the equality concept is canonical;
- the executable anchor mapping is not frozen;
- no AB=CD tolerance is invented;
- `entry = C` is not assumed.

### 4.5 Stop/invalidation: semantic alignment

The source demonstrates structural SL placement and says the scenario is invalid if price returns to the invalidation area. Exact structural anchor mapping still needs final geometry confirmation.

### 4.6 TP / 2X: keep separate

The source teaching material distinguishes TP1/TP2 and separately discusses a 2X-style level. These must not be collapsed into one canonical target rule until the relationship is explicitly resolved.

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
| Round-number filter | no canonical source evidence established | research-only |
| Session filter | no canonical source evidence established | research-only |
| 2X management | separate source module | do not merge into base target |

## 6. Source-video visual evidence added in this pass

The uploaded source video was inspected directly at the key teaching sections.

### 36:00

The slide visibly states `Valid BO = P-Gap` and presents multiple Spike constructions. One construction is explicitly marked with a red X. This strengthens the conclusion that P-Gap is a validity condition and that Spike has a source-defined visual taxonomy, but it does not yet expose an executable P-Gap formula.

### 36:30–37:00

The instructor writes `AB=CD` above the SP2L example and connects the 2Leg explanation to the equality relationship. This confirms the concept but still does not uniquely label A/B/C/D on the price series.

### 38:45–39:40

The teaching diagram is annotated with `BO` and `Limit` / `Buy Limit`, followed by an SL level. The order is shown as a pending level during the correction rather than a close-reclaim trigger. This is direct visual corroboration of the transcript entry semantics.

### ~62:20–63:00

Real XAUUSD execution material shows numbered structural levels and subsequent trade/order results. It demonstrates that the source uses concrete structural price levels in execution, but the compressed recording does not provide enough unambiguous annotation to promote the visible A/B/C/D-style labels into an exact OHLC mapping.

## 7. What can be said about output impact now

The strongest currently provable impact is **qualitative**:

1. The baseline's close-reclaim trades are not valid representations of the source's pending-limit execution model.
2. The generic P-Gap detector cannot be treated as a canonical filter, so any apparent improvement from applying it would be methodology leakage unless the source formula is first frozen.
3. Baseline context filters (EMA, round-number, sessions) cannot be allowed to define canonical output without source evidence.
4. The distribution of R is likely to change materially once pending-limit price and structural SL are frozen; therefore baseline expectancy/PF cannot be carried forward as Strategy A evidence.
5. 1M and 5M baseline results already disagree in expectancy sign, which reinforces the need for untouched validation rather than parameter selection from these two outputs.

## 8. Required next executable comparison

Once P-Gap and A/B/C/D geometry are frozen, run the same immutable dataset through:

**A — Legacy baseline**  
Current repository baseline, unchanged.

**B — Source-semantic shadow**  
Only source-confirmed gates and pending-limit mechanics; unresolved geometry returns an explicit blocked state.

**C — Frozen canonical SP2L**  
Full deterministic source specification after geometry freeze.

For each candidate/setup, persist a row-level disposition:

- `RETAINED`
- `REMOVED_PGAP`
- `REMOVED_SPIKE_VARIANT`
- `REMOVED_CONTEXT`
- `ENTRY_CHANGED`
- `FILL_UNRESOLVED`
- `STOP_CHANGED`
- `TARGET_CHANGED`
- `BLOCKED_SOURCE_GEOMETRY`

And compute at minimum:

- candidate count and trade count;
- attrition by rule;
- filled vs unfilled pending orders;
- entry-price delta;
- stop/risk delta;
- target delta;
- R distribution and median R;
- expectancy and PF;
- drawdown and loss streak;
- long/short split;
- session/time-of-day only as descriptive analysis, not as a filter unless source-confirmed.

## 9. Gate decision

**SOURCE RESOLUTION: NOT COMPLETE**  
**SHADOW IMPACT ANALYSIS: COMPLETE FOR CURRENT EVIDENCE**  
**FROZEN GEOMETRY: BLOCKED**  
**DEV/VAL: NOT AUTHORIZED**  
**PRODUCTION: UNCHANGED**

The correct next move is source-geometry resolution, not optimization.

## 10. Provenance

Source video SHA256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`  
Transcript SHA256: `47f867385338738a23b2d06dc48e67b852127243`
