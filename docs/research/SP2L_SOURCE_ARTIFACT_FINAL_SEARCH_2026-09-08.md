# SP2L Official Source Artifact Final Search — 2026-09-08

## Objective

Perform a final targeted search for additional first-party material that could resolve the remaining executable geometry questions for Strategy A / SP2L, without importing third-party implementation assumptions.

## First-party findings

The official Poursamadi SP2L page confirms the following semantics:

- SP2L is Power -> Correction -> Continuation.
- A valid Spike requires a price gap (P-Gap); a sharp movement without a gap is not valid.
- Bullish correction reaches the low of the previous candle.
- Bearish correction reaches the high of the previous candle.
- Entry is in the Spike direction.
- SL is behind the candle from which the Spike originated.
- Default TP is 1:1.
- The page explicitly instructs traders to backtest and define exact entry conditions before live use.

The official site also exposes a public SP2L strategy page and a set of general trading tools, but the searched public material does not expose an open SP2L implementation, source code, P-Gap formula, exact wick/body convention, numeric buffer, universal candle index, or exact AB/CD tolerance.

## Source-video artifact cross-check

The uploaded source video remains the highest-authority artifact. Its transcript and visual evidence establish:

- four candle-level Spike variants are discussed;
- P-Gap is explicitly associated with valid breakout;
- the instructor describes a gap/non-overlap relationship but does not provide a machine-readable OHLC formula;
- pending/manual limit ordering during correction is explicitly demonstrated;
- the bullish prior-low / bearish prior-high correction reference is stated;
- SL is tied to the Spike-origin structure;
- Leg 2 is intended to match Leg 1 magnitude and AB=CD is explicitly named;
- the instructor contrasts the source's candle-level treatment with classical internet A/B/C/Fibonacci treatment.

## External-source boundary

TradingView/TradingFinder material is useful only as secondary corroboration/hypothesis. Closed-source implementations and third-party rules such as generic FVG, 65% body thresholds, spike-size thresholds, or close-reclaim entries are not promoted to canonical Strategy A rules.

A Telegram index was also found that lists the same source video's topics, including four Spike types, P-Gap, order placement, 2X, levels/context, and ten entry examples. Because the indexed Telegram channel is not established as the official first-party publication, it is treated as corroboration only, not authority.

## Final resolution matrix

| Question | Resolution | Canonical status |
|---|---|---|
| Is P-Gap required for valid Spike/BO? | Yes | SOURCE_CONFIRMED |
| Is P-Gap a generic FVG? | Not established | REJECTED_AS_CANONICAL |
| Exact P-Gap OHLC boundary | Not uniquely recoverable | UNRESOLVED |
| Exact P-Gap candle timing | Not uniquely recoverable across variants | UNRESOLVED |
| Equality/touch/minimum-gap rule | Not source-confirmed | UNRESOLVED |
| Bullish correction reference | Previous/relevant Low | SOURCE_CONFIRMED_SEMANTIC |
| Bearish correction reference | Previous/relevant High | SOURCE_CONFIRMED_SEMANTIC |
| Pending-limit execution | Yes | SOURCE_CONFIRMED |
| Exact Entry candle index | Not uniquely resolved across variants | UNRESOLVED |
| Entry = P-Gap boundary | Not supported | REJECTED |
| Entry = classical C | Not supported | REJECTED |
| Entry = 50% retracement | Not source-confirmed | REJECTED_AS_CANONICAL |
| SL anchored to Spike-origin candle | Yes | SOURCE_CONFIRMED_SEMANTIC |
| Exact SL wick/body price | Not uniquely recoverable | UNRESOLVED |
| Numeric SL buffer | Not source-confirmed | UNRESOLVED |
| Leg 1 / Leg 2 equal-magnitude concept | Yes | SOURCE_CONFIRMED_SEMANTIC |
| Exact Leg 1 OHLC anchors | Not uniquely recoverable | UNRESOLVED |
| Classical Fibonacci A/B/C implementation | No source basis | REJECTED_AS_CANONICAL |
| AB=CD tolerance | Not source-confirmed | UNRESOLVED |
| Base TP = 1:1 | Yes | SOURCE_CONFIRMED |

## Gate decision

The source-resolution effort has reached the point of diminishing returns using the currently available first-party public artifacts.

**SOURCE SEMANTICS: RESOLVED ENOUGH FOR A FROZEN SEMANTIC CONTRACT.**

**EXECUTABLE OHLC GEOMETRY: NOT RESOLVED.**

Therefore **FROZEN GEOMETRY remains BLOCKED**. No P-Gap formula, Entry candle index, SL buffer, AB=CD tolerance, or classical A/B/C mapping may be invented or selected by backtest performance.

## Next permitted path

1. Freeze the semantic contract only.
2. Keep executable-geometry work in research status.
3. Do not start DEV/VAL/Holdout as if the geometry were canonical.
4. If a new first-party artifact becomes available (annotated source chart, open indicator/template, source worksheet, or equivalent), reopen SOURCE RESOLUTION.
5. Otherwise, treat any deterministic geometry implementation as a separately labelled research hypothesis, never as Strategy A production.

## Production impact

No production code is changed by this document. No live BUY/SELL logic is promoted.
