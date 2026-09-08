# SP2L P-Gap Synthetic Discriminators V2 — 2026-09-08

## Objective

Convert the remaining P-Gap ambiguity into deterministic source-resolution fixtures without using historical performance.

## Fixture matrix

| Fixture | Wick ranges | Bodies | Breakout context | Purpose | Expected status |
|---|---|---|---|---|---|
| PG2-01 | separated | overlap | yes | distinguish wick-range from body-range | wick candidate survives; body unresolved |
| PG2-02 | overlap | separated | yes | inverse discriminator | body candidate only if source evidence supports it |
| PG2-03 | separated | separated | yes | both definitions agree | non-discriminating |
| PG2-04 | touch/equality | touch/equality | yes | equality rule | unresolved |
| PG2-05 | separated | overlap | no | gap without breakout | tests mandatory breakout association |
| PG2-06 | separated | overlap | yes, gap before/after sequence variant | timing discriminator | unresolved until source distinguishes |
| PG2-07 | no gap | overlap | yes | breakout without P-Gap | should not become valid P-Gap |
| PG2-08 | separated | overlap | yes | same geometry with different entry/SL levels | tests that P-Gap does not define Entry/SL automatically |

## Deterministic comparison rule

A fixture is useful only if two candidate interpretations produce different classifications from identical OHLC input. If both candidates classify the fixture identically, the fixture does not resolve the ambiguity.

## Source-resolution policy

Historical win rate, expectancy, profit factor, or drawdown must never select between PG2 candidates. The surviving interpretation must be justified by source evidence.

## Current conclusion

The deep visual inspection strengthens the semantic statement:

`P-Gap = breakout-associated non-overlap / gap concept`

but does not establish the exact OHLC boundary formula. Therefore the P-Gap formula remains **UNRESOLVED**.

The next source-first action is to seek a source frame where the highlighted gap endpoints can be read against candle highs/lows or bodies with enough precision to discriminate PG2-01/02/04/06. Until such evidence exists, no canonical detector should be implemented.

## Gate

FROZEN GEOMETRY remains BLOCKED. Production remains unchanged.
