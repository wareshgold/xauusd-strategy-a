# SP2L Final Source Audit — 2026-09-08

## Scope
Final source-only audit of executable geometry for P-Gap, Entry, SL, and Leg-1 / AB=CD using the uploaded authoritative video, its timestamped transcript evidence, extracted source frames, and external TradingView/TradingFinder material only as secondary corroboration.

## Evidence hierarchy
1. Authoritative source video/transcript.
2. Source visual evidence.
3. Existing source ledger / meaning map.
4. External implementations only as non-canonical corroboration.

## Findings

### 1. P-Gap
Source explicitly links a valid breakout to P-Gap and describes a gap/non-overlap relationship in the breakout/follow-through context. The source slide states `Valid BO = P-Gap` and shows three accepted-looking constructions plus one rejected construction.

A deeper visual inspection confirms an important semantic invariant: the three accepted-looking constructions are deliberately different candle arrangements, yet each is illustrated with a gap/non-overlap region; the red-X construction does not provide the same visible gap/non-overlap evidence. This strengthens the semantic rule without resolving the executable formula.

The visual rectangles do not uniquely identify an OHLC boundary pair. The audit cannot defensibly distinguish:
- prior High -> next Low;
- prior Low -> next High for bearish symmetry;
- body top -> body bottom;
- wick-to-wick;
- a multi-candle boundary;
- another manually illustrated boundary;
- equality/touch behavior;
- minimum gap size;
- a universal candle index/timing rule.

The three accepted variants also show that a single rigid three-candle timing formula must not be imported merely because it is convenient to code.

Decision: semantic meaning + non-overlap invariant resolved; executable formula unresolved.

### 2. Entry
Source transcript states that when the correction reaches the low of the relevant previous candle in bullish structure, an order can be placed manually or as a pre-set limit; bearish logic is mirrored to the previous high. Source diagrams explicitly show `Buy Limit` / `Entry` as a separate execution level.

The primary-source entry cross-check also reviewed the real entry sequence around the first trade examples. It does not show a source-required later last-Spike-candle breakout/reclaim before the pending order is prepared. The strongest source sequence remains:

`SPIKE -> CORRECTION -> PENDING LIMIT -> FILL`

A secondary TradingFinder implementation does use a later last-Spike-candle breakout, but this conflicts with the primary video semantics and therefore remains a secondary hypothesis only.

The four real trade examples were also cross-checked. Their observed execution prices are 3229.08, 3223.84, 3228.88, and 3232.41. The charts show horizontal order/reference levels associated with the corrective structure, but the source visuals do not uniquely map each fill to one universal candle index or wick/body boundary.

Decision: direction + pending-limit semantics resolved; last-Spike-candle breakout rejected as a canonical entry prerequisite; exact executable candle/price convention unresolved.

### 3. SL
Source semantics: stop is placed behind the candle from which the Spike originated. The visual entry diagram places SL structurally below/behind the origin in bullish structure; bearish mirror is consistent.

The four source-visible trade records provide the following descriptive fill-to-stop distances:

| Trade | Entry | SL | Absolute distance |
|---|---:|---:|---:|
| T1 | 3229.08 | 3237.73 | 8.65 |
| T2 | 3223.84 | 3235.50 | 11.66 |
| T3 | 3228.88 | 3235.50 | 6.62 |
| T4 | 3232.41 | 3237.80 | 5.39 |

The variation is consistent with a structural stop rather than a single fixed entry-to-stop distance, but it does **not** prove the exact OHLC boundary.

The real-trade frames support an invalidation level on the far side of the originating structure. They do not uniquely resolve:
- wick extreme vs body edge;
- strict beyond vs touch;
- tick/spread/point buffer;
- exact origin candle identity for every Spike variant.

The source also allows deletion/replacement of a pending order when the resulting stop distance changes materially, so observed stop prices must not be reverse-engineered into a universal fixed formula.

Decision: structural anchor resolved; exact price unresolved.

### 4. Leg 1 / AB=CD
Source confirms Spike -> correction -> second leg and explicitly describes AB=CD / approximately equal Leg-1 and Leg-2 magnitude. The source also contrasts its candle-level approach with classical internet A/B/C/Fibonacci treatment.

Strongest candidate for Leg-1 magnitude is source-defined Spike-origin -> source-defined Spike extreme, but exact OHLC anchor remains unresolved. No classical A/B/C mapping or Fibonacci ratio is imported.

Decision: equal-leg semantic resolved; exact geometry and tolerance unresolved.

## Four-trade SL/origin audit

A dedicated research audit and fixture set preserves the four source-visible Entry/SL observations without promoting them into executable geometry. The fixture contract requires:

- `BEHIND_SPIKE_ORIGIN_CANDLE` as the semantic stop anchor;
- exact stop boundary remains unresolved;
- fixed stop buffer remains unresolved;
- observed risk distances remain descriptive only.

This is a source-evidence preservation layer, not a trading-rule implementation.

## P-Gap visual resolution audit

A dedicated research fixture set records three accepted-looking source constructions and one red-X rejected construction. The fixtures encode only the source-safe observation that accepted-looking constructions show a non-overlap/gap relationship in breakout context. They intentionally keep the following unresolved:

- exact OHLC boundary;
- exact candle timing/index;
- minimum gap size;
- equality/touch convention.

No generic FVG formula is promoted.

## Entry geometry hypothesis matrix

A research-only fixture matrix now separates candidate executable Entry interpretations:

- previous/relevant candle extreme;
- first correction candle extreme;
- Spike-origin candle extreme;
- previous/relevant candle body edge;
- first correction candle body edge.

Synthetic fixtures deliberately separate these anchors and mirror BUY/SELL cases. The fixtures are guardrails, not evidence selecting a winner. All candidates remain `UNRESOLVED` until primary-source visual evidence establishes a repeated relationship.

## External cross-check
TradingView/TradingFinder public material corroborates some concepts (previous low/high entry context, spike-origin stop, gap/imbalance terminology), but the implementation is protected/closed-source and contains additional third-party rules. Those rules are not canonical Strategy A rules.

In particular, no third-party claim is promoted for:
- generic FVG = P-Gap;
- 65% body threshold;
- spike-size threshold;
- three-candle formula;
- market-break entry instead of pending limit.

## Final source-resolution decision
The authoritative material is sufficient to define the **semantic contract** but not sufficient to produce a unique deterministic OHLC formula for all executable geometry.

### Frozen semantic contract
`Spike -> source-defined P-Gap-valid breakout context -> correction -> relevant prior Low/High -> pending limit -> structural invalidation behind Spike-origin -> Leg 2 with source-confirmed equal/approximately equal Leg-1 magnitude.`

### Explicitly unresolved
- exact P-Gap boundaries and timing;
- exact relevant Entry candle across all variants;
- exact Entry price convention/buffer;
- whether Entry uses wick or body boundary;
- whether the pending level is fixed at first qualification or revised as correction evolves;
- exact fill/touch semantics;
- exact SL price convention/buffer;
- exact Leg-1 OHLC anchors;
- exact AB=CD tolerance;
- exact target module relationship where TP1/TP2/2X are involved.

## Gate decision
SOURCE RESOLUTION: semantic contract complete.
FROZEN GEOMETRY: BLOCKED.
DEV: LOCKED.
VALIDATION: LOCKED and untouched.
FRESH HOLDOUT: LOCKED and untouched.
PRODUCTION: unchanged.

No historical backtest result may be used to resolve any item above. No unresolved item may be promoted to canonical production logic.
