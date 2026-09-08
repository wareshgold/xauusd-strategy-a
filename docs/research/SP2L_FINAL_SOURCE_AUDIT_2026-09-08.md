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

The visual rectangles do not uniquely identify an OHLC boundary pair. The audit cannot defensibly distinguish:
- prior High -> next Low;
- body top -> body bottom;
- wick-to-wick;
- another manually illustrated boundary;
- equality/touch behavior;
- minimum gap size;
- a universal candle index/timing rule.

Decision: semantic meaning resolved; executable formula unresolved.

### 2. Entry
Source transcript states that when the correction reaches the low of the relevant previous candle in bullish structure, an order can be placed manually or as a pre-set limit; bearish logic is mirrored to the previous high. Source diagrams explicitly show `Buy Limit` / `Entry` as a separate execution level.

The audit does not establish one universal candle index across all Spike variants, nor does it establish a numeric buffer, body-vs-wick substitution, or equivalence to P-Gap boundary / classical C / 50% retracement.

Decision: direction + pending-limit semantics resolved; exact executable candle/price convention unresolved.

### 3. SL
Source semantics: stop is placed behind the candle from which the Spike originated. The visual entry diagram places SL structurally below/behind the origin in bullish structure; bearish mirror is consistent.

Exact executable OHLC price is not source-resolved: wick/body, strict beyond vs touch, tick/spread buffer, and origin identity across every variant remain open.

Decision: structural anchor resolved; exact price unresolved.

### 4. Leg 1 / AB=CD
Source confirms Spike -> correction -> second leg and explicitly describes AB=CD / approximately equal Leg-1 and Leg-2 magnitude. The source also contrasts its candle-level approach with classical internet A/B/C/Fibonacci treatment.

Strongest candidate for Leg-1 magnitude is source-defined Spike-origin -> source-defined Spike extreme, but exact OHLC anchor remains unresolved. No classical A/B/C mapping or Fibonacci ratio is imported.

Decision: equal-leg semantic resolved; exact geometry and tolerance unresolved.

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
