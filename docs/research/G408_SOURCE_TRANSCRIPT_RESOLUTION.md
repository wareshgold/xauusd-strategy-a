# G408 — Source Transcript Resolution

## Purpose

G408 records the recovery and source-controlled interpretation of the provenance-identified SP2L transcript already present in the project's File Library. This is a source-resolution artifact only. It does not freeze executable geometry and does not authorize optimization or production.

## Recovered artifact

- File: `پورصمدیSP2L TRANSCIBE.txt`
- File-library creation: 2026-09-12
- Source identity represented by transcript: SP2L YouTube video `7HEC5mO3d3U`
- The transcript contains timestamped Persian speech throughout the video, including the critical 31:00–45:00 strategy-definition window.

The transcript is now materially stronger evidence than the prior G407 state that said a provenance-identified transcript had not been recovered. It must nevertheless remain subordinate to the raw video when visual ambiguity remains.

## Critical source findings

### 1. Breakout / follow-through / P-Gap

At 31:02 the speaker defines breakout as a candle closing beyond a prior level followed by a next candle that cannot return into the relevant area. At 31:18 the follow-through candle is described as closing higher and not overlapping the preceding candle.

At 31:43 the speaker explicitly states that the breakout candle has P-Gap / pressure gap and that P-Gap is distinct from E-Gap. At 34:25 the transcript describes a case where the first candle's high and the following candle's low do not overlap and identifies the resulting gap as part of a breakout with follow-through.

At 34:44–35:37 two sequences are explicitly treated as the same strategy concept: breakout followed by higher lows then P-Gap, versus higher lows first and P-Gap afterward. The speaker says these can theoretically be separated but are currently treated as one strategy.

**Resolution:** P-Gap is source-defined and materially associated with breakout/follow-through and directional spike validity. The transcript still does not provide a sufficiently formal executable OHLC formula, tick threshold, or tolerance. No generic three-candle gap formula is promoted.

### 2. Spike and Leg 1 / Leg 2

At 36:15 the speaker identifies 2Leg with AB=CD. At 36:59 he states that after a spike, a correction is expected and the second leg is expected to complete with Leg 1 and Leg 2 equal.

At 37:57 the speaker again states that after the increase a correction is expected and the next leg should be built to the same size as the first leg.

At 38:18–38:38 the upward spike is described as a sequence of higher lows; the speaker says this constitutes the spike / first stage of the strategy.

**Resolution:** AB=CD / Leg1=Leg2 is directly source-confirmed. The transcript materially strengthens the semantic sequence. Exact A/B/C/D geometric anchors and equality tolerance remain unresolved.

### 3. Correction trigger and pending-limit entry

At 38:38 the speaker defines the correction as the next candle beginning to correct and coming below the first low. He states that the order can be placed manually or as a pre-defined limit order there.

At 38:53–39:11 he explains that after the gap/breakout and follow-through create an order-space associated with buyers entering, there is no need to wait for another candle; the limit order can be placed within the first three candles.

At 39:26 he explicitly identifies the order as a Buy Limit and states that the distance to the stop is known before activation. He further states that if price returns to the referenced invalidating area, the scenario is cancelled and is no longer valid.

At 39:48–40:16 he describes order relocation/adjustment if a later candle materially changes the distance to stop, while retaining the original order when the change is not large enough to disrupt money management.

At 41:18 he states that when the next candle begins activating the order, the resulting position is a Buy with an SL.

**Resolution:** pending-limit entry is directly confirmed; entry is tied to the correction / first-low reference and may be staged before the next candle. Exact executable price, whether it is exactly the first low or another source-defined point in/under that reference, fill semantics, and pre-fill cancellation algorithm remain unresolved. The source does not justify assuming fill price = C.

### 4. Stop / invalidation

The transcript explicitly links invalidation to the referenced area that price must not return to before activation (39:26), and explicitly shows a Buy with an SL after activation (41:18).

The creator's official web page independently states that SL is placed behind the candle from which the spike originated. This corroborates the spike-origin structural reference, but neither source currently supplies an exact executable wick/body field, buffer, or tick rule.

**Resolution:** structural stop reference is materially strengthened; exact executable stop boundary remains unresolved.

### 5. Target mapping

At 42:26 the speaker states that take-profits can be TP1 or TP2 and says he generally uses TP1 because the second position can make the combined result larger.

At 42:37 he states that TP2 is relatively large for this strategy because the stop is relatively large, and therefore the TP should be 1, while also saying the occurrence probability is good. At 43:00 he explicitly instructs viewers to backtest rather than accept the statement blindly.

At 1:04:19–1:04:32 a later example explicitly describes the position's TP at reward 1, with reward 2 as an optional extension.

**Resolution:** source evidence now strongly supports a default/core TP at 1R for the demonstrated primary trade, while TP2 remains an optional/larger target. Exact TP1/TP2 geometric mapping relative to the AB=CD projection is still not fully frozen.

## Source-vs-hypothesis boundary

The following remain **unresolved** and must not be promoted merely because the transcript narrows them:

- executable P-Gap OHLC formula;
- P-Gap minimum magnitude/tolerance;
- exact A/B/C/D anchor fields;
- AB=CD equality tolerance;
- exact pending-limit price;
- exact fill semantics;
- pre-fill order cancellation/invalidation algorithm;
- exact stop price field and buffer;
- exact TP1/TP2 geometric mapping.

The following are now **source-confirmed / materially strengthened**:

- breakout + follow-through;
- P-Gap as a distinct pressure-gap concept associated with valid directional movement;
- Spike → correction → second leg;
- AB=CD / Leg1 = Leg2 relationship;
- correction reaching below the first low for the bullish example;
- pending Buy Limit before the next candle completes;
- structural invalidation before activation;
- TP1 / TP2 distinction and default demonstrated TP ≈ 1R.

## Gate impact

G400 remains **BLOCKED**. G408 does not freeze geometry.

However, the evidence state has materially improved: the critical transcript is now available and can be reconciled directly against the registered frame windows. The next source-resolution step is no longer transcript acquisition; it is **transcript ↔ exact-frame reconciliation**, especially:

- 34:14–35:50 vs frames around 34:14–35:50 for P-Gap geometry;
- 36:15–37:08 vs 36:15–37:10 for AB=CD drawing/anchors;
- 38:18–39:48 vs 38:18–39:50 for first-low entry placement and invalidation;
- 41:18–42:37 vs 41:18–42:40 for SL and TP1/TP2;
- 1:04:19–1:04:32 for the later explicit 1R target example.

No backtest result is used to resolve source meaning.
