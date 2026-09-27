# SP2L Trigger Source-to-Matrix Review — 2026-09-27

## Primary source

Official author page:
https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

The page states that after the spike the market makes a correction and:
- in an uptrend, the corrective candle should reach the low of the previous candle;
- in a downtrend, the corrective candle should reach the high of the previous candle;
- once the Second Leg is triggered, entry follows the spike direction. citeturn0search0

## What the source resolves

The source supports the following semantic facts:

1. Trigger is associated with the corrective candle.
2. BUY references a previous-candle Low.
3. SELL references a previous-candle High.
4. The wording is "reach", not an explicit candle-close condition.

Therefore, the source is more consistent with an OHLC extreme reaching a reference level than with a close-only interpretation.

## What the source does not resolve

The page does not specify:
- an exact OHLC array index for "previous candle";
- whether only the immediately following correction candle is eligible;
- whether multiple correction candles may be scanned;
- whether equality/touch counts identically to penetration;
- exact entry-price/fill semantics.

## Candidate matrix disposition

| Candidate | Source disposition |
|---|---|
| A: immediate + touch/penetration | Partially supported; immediate eligibility is not explicitly stated |
| B: immediate + close | Not supported by the wording "reach"; still not formally disproven as an implementation interpretation |
| C: scan-forward + touch/penetration | Partially supported; scan-forward duration is not specified |
| D: scan-forward + close | Weakly supported; conflicts with "reach" as a natural OHLC reading |

## Decision

Do NOT freeze A, B, C, or D as canonical.

The strongest source constraint currently is:

**A corrective candle must reach the previous candle's Low/High in the appropriate direction.**

The remaining candle-indexing and acceptance/fill semantics remain SOURCE-UNRESOLVED.

## Gate

SOURCE RESOLUTION remains open.

No backtest result is used to select an interpretation.
No canonical detector or production execution rule is changed.

Next evidence target: primary-source material that explicitly shows the candle sequence around the trigger (diagram, example, or author instruction identifying the exact previous candle and whether equality/touch is sufficient).
