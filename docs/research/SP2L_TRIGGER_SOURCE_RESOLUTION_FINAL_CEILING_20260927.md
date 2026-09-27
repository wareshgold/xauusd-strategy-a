# SP2L Trigger Source Resolution — Current Evidence Ceiling — 2026-09-27

## Primary-source search result

A fresh search of the official author material found the same authoritative SP2L wording:

- SP2L is described as Power → Correction → Continuation.
- After the spike, the market makes a correction.
- In an uptrend, the corrective candle should reach the Low of the previous candle.
- In a downtrend, the corrective candle should reach the High of the previous candle.
- The author also describes the correction as brief.
- Entry follows the spike direction after the Second Leg is triggered.

Source: official author SP2L page:
https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

## What changed

The fresh primary-source search did NOT locate new author-published text that specifies an exact OHLC index, a scan-forward rule, or an explicit touch/penetration/close acceptance condition.

The word "brief" describes the correction qualitatively, but it is not a deterministic maximum-candle rule and therefore cannot be converted into an algorithmic scan window.

## Current evidence ceiling

Source-confirmed:
- corrective candle is the trigger context;
- BUY references previous-candle Low;
- SELL references previous-candle High;
- trigger is described as price reaching that level;
- correction is described as brief.

Still unresolved:
- exact array/candle index for "previous candle";
- whether eligibility is strictly the first correction candle;
- whether a later correction candle can trigger;
- equality/touch versus penetration;
- exact entry price and fill semantics.

## Decision

Do not promote A or C from the synthetic matrix.

Do not promote B or D.

The current trigger rule remains SOURCE-UNRESOLVED beyond the source-confirmed semantic constraint.

The synthetic fixture matrix is retained as a regression/diagnostic instrument only.

## Workflow gate

SOURCE RESOLUTION: OPEN / EVIDENCE CEILING REACHED

Next legitimate route:
1. obtain new author-primary evidence (annotated example, transcript, or explicit instructional text), OR
2. keep trigger geometry unresolved and proceed only with research infrastructure that does not require canonical trigger promotion.

No backtest optimization may decide this ambiguity.
