# F13 2X Worked-Example Reconciliation — 2026-09-21

## Source retrieval result

A fresh web retrieval of the author-controlled page returned the full indexed article text:

**SP2L Strategy (Spike–2Leg) by Mohammad Ali Poursamadi**

Source:
https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

The page explicitly states that, in addition to the initial entry, a secondary entry can be added at 50% of the distance from the entry point to the stop-loss.

It also states:
- bullish corrective candle reaches the previous candle Low;
- bearish corrective candle reaches the previous candle High;
- SL is behind the candle from which the spike originated;
- default TP is 1:1 R:R.

## Discrimination

This resolves the author-source numeric relationship at the wording level:

SecondaryEntry = Entry + 0.5 * (StopLoss - Entry)

for a midpoint in price space between Entry and SL.

The page explicitly describes the secondary entry as an addition to the position, not as a separately named target.

## Primary-video comparison

The archived primary-video transcript still contains the separate worked-example statement that the 2X entry occurs when price reaches approximately half the target.

That statement is not sufficient to replace the author-page relationship because:
- the video transcript does not provide the full numerical equation;
- the author page explicitly identifies the two endpoints as Entry and Stop-Loss;
- default TP is separately stated as 1:1 on the author page.

Therefore the evidence is represented as:
1. Author-controlled executable relationship: 50% Entry-to-SL = SOURCE-CONFIRMED.
2. Primary-video half-target wording: SOURCE-CONFIRMED example/context, but exact reference anchor remains UNRESOLVED.
3. Universal 2X lifecycle: UNRESOLVED.

## What is now source-confirmed

- 2X/secondary entry exists.
- It is optional/additional to the initial entry.
- The author-controlled source defines its price relationship as the midpoint between Entry and SL.
- Default TP is 1:1.
- Directional corrective-candle references are stated.

## What remains unresolved

- Whether the primary-video half-target statement refers to the same secondary-entry construction.
- Whether the 50% Entry-to-SL level is always used after Entry/SL refresh.
- pending/market order semantics;
- activation vs fill;
- sizing and risk aggregation;
- shared vs separate SL;
- behavior when initial entry is unfilled;
- TP allocation/closure semantics;
- replacement precedence.

## Canonical boundary

The 50% Entry-to-SL relationship is source-confirmed relationship evidence, but the complete F13 execution state machine remains non-canonical until lifecycle fields are uniquely source-resolved.

No production BUY/SELL behavior is changed.

## Gate

F13 relationship: SOURCE-CONFIRMED
F13 complete execution: UNRESOLVED
Frozen Geometry: BLOCKED
Untouched Validation: LOCKED
Robustness/Stability: LOCKED
Fresh Holdout: BLOCKED
Production: DISABLED
Forward Test: UNTOUCHED
