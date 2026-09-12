# SP2L G232 — P-Gap Source Frame Review

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `P_GAP_DISTINCTION_CONFIRMED_GEOMETRY_UNRESOLVED`

## Raw source frame pass

A targeted pass was made over the original SP2L video around 29:00–32:30 and the explicit P-Gap teaching section around 35:45–36:16.

### Findings

1. Around 29:00 the source presents multiple spike-candle constructions. The drawings distinguish different spike shapes, but they do not provide a numeric OHLC definition for P-Gap.
2. Around 31:50 the source explicitly writes `P-GAP`.
3. Around 32:00–32:20 the source places `P-GAP` beside a separately written `GAP / Common` classification. This is direct evidence that the source presentation treats the SP2L P-Gap label as distinct from an unqualified Common Gap label in that teaching context.
4. Around 32:20 horizontal reference lines are drawn on an example, but the frame does not uniquely expose their candle-index/OHLC mapping.
5. Around 35:55–36:16 the source explicitly labels the examples `Valid BO = P-Gap`, with one rejected example and three numbered positive examples.

## Cross-source corroboration

The creator's official SP2L page independently states that a valid spike contains a price gap identified as P-Gap and that a sharp movement without that gap is invalid. The page does not specify the exact candle indexing or OHLC boundary formula.

## Non-inferences

This pass does **not** establish:

- P-Gap = generic three-candle Gap;
- P-Gap = Breakout Gap;
- P-Gap = Pressure Gap;
- P-Gap = FVG;
- exact `t-2/t-1/t` indexing;
- wick versus body boundaries;
- minimum gap size;
- close-at-previous-high as a mandatory P-Gap condition;
- bearish mirror formula;
- overlap/touch tolerance.

## Decision

The new evidence strengthens the semantic distinction of P-Gap as a first-class SP2L term and confirms its role in valid breakout/spike qualification. It does **not** cross the threshold for executable geometry.

Therefore B1 remains **SOURCE-UNRESOLVED** and no production P-Gap predicate is authorized.

## Next source task

Continue targeted inspection of the P-Gap teaching examples and any later first-four-trades/order walkthrough where the actual candles and P-Gap region coexist. The objective is to find a source frame where the gap boundaries can be mapped uniquely to candle OHLC without relying on visual similarity or backtest performance.
