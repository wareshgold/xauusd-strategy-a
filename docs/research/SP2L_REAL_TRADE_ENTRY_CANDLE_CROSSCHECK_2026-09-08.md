# SP2L Real-Trade Entry Candle Cross-Check — 2026-09-08

## Objective
Determine whether the four source-visible XAUUSD SELL trades identify a repeatable candle-level Entry formula, especially whether the executed Entry price is demonstrably the High of the relevant previous candle.

## Source observations
The real-trade frames around the first four trades show SELL structures with horizontal entry/reference levels drawn in the corrective area. The order-history table provides four executed prices:

| Trade | Entry | SL | Entry→SL |
|---|---:|---:|---:|
| T1 | 3229.08 | 3237.73 | 8.65 |
| T2 | 3223.84 | 3235.50 | 11.66 |
| T3 | 3228.88 | 3235.50 | 6.62 |
| T4 | 3232.41 | 3237.80 | 5.39 |

The chart annotations and horizontal order/reference levels are consistent with the source-described SELL correction context: price corrects upward toward a relevant previous High and the pending SELL order is prepared there.

## Candidate interpretation cross-check

| Candidate | Evidence from real trades | Decision |
|---|---|---|
| Relevant previous High context | Repeated structural alignment of SELL entries with corrective/reference highs | **Supported semantically** |
| Entry = exact previous-candle High | Source frame resolution does not expose an unambiguous candle-to-price mapping for all four trades | **Unresolved** |
| Entry = first correction candle High | Not uniquely distinguishable from previous/relevant High in the rendered chart | **Unresolved** |
| Entry = Spike-origin High | Not demonstrated repeatedly by the four examples | **Unresolved** |
| Body-edge entry | Cannot be distinguished from wick-based level at source-frame resolution | **Unresolved** |
| Fixed entry buffer | No source evidence; trade prices alone cannot establish one | **Unresolved** |

## Important negative evidence
T1 and T3 have very close but distinct executed prices (3229.08 vs 3228.88) while sharing the same observed SL (3235.50). This is compatible with separate structural reference levels and does not support collapsing Entry to a fixed price or fixed stop-distance rule.

T2 and T4 further show materially different Entry/SL distances, reinforcing structural rather than fixed-distance placement. This does not identify the exact candle field used for Entry.

The source allows pending-order deletion/replacement when the stop distance changes materially. Therefore the observed prices cannot be reverse-engineered into a universal mathematical formula from the trade table alone.

## Conclusion
The four real trades strengthen the source-safe semantic rule:

`SELL correction -> relevant previous/reference High -> pending SELL limit`

They do **not** prove:

`EntryPrice = High(previous candle)`

for every accepted Spike variant, nor do they resolve wick/body convention, exact candle identity, touch/fill semantics, or buffer.

## Gate impact
- Entry direction: **resolved**
- Pending-limit semantics: **resolved**
- Previous/relevant High/Low structural context: **strongly supported**
- Exact Entry candle: **UNRESOLVED**
- Exact Entry OHLC field: **UNRESOLVED**
- Exact Entry price/buffer: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**

No profitability result was used to select an interpretation. No production code was changed.
