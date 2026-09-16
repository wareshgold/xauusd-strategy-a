# SP2L Batch 12 — Source Evidence F8/F10 — 2026-09-16

## Scope

P0 source retrieval for the remaining executable-geometry blockers:

- F8 — relevant/important swing selection
- F10 — stop-loss / invalidation price semantics

This record is source evidence only. It does not select geometry by backtest performance and does not promote secondary implementation details to canonical rules.

## Sources reviewed

### S1 — Primary author-controlled SP2L page

Author: Mohammad Ali Poursamadi
URL: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/
Authority: PRIMARY / author-controlled

Relevant statements exposed by the indexed page:

- SP2L consists of Spike, 2nd Leg, and Entry Level.
- In an uptrend, the corrective candle is described as reaching the low of the previous candle.
- In a downtrend, the corrective candle is described as reaching the high of the previous candle.
- Once the Second Leg is triggered, entry is taken in the direction of the Spike.
- Stop-loss is described as being placed "behind the candle from which the spike originated."
- The page does not define whether the relevant low/high is the first qualifying swing, latest/evolving swing, or another structural selection rule.
- The page does not define whether "behind" means wick extreme, body boundary, open/close, structural boundary, or a numerical buffer.

## F8 — Relevant swing selection

### Evidence

The primary page establishes a directional relationship for the Second Leg: bullish correction reaches the low of the previous candle; bearish correction reaches the high of the previous candle. It also describes the entry as occurring after the Second Leg is triggered.

However, this text does not uniquely answer the selection problem required for deterministic implementation:

1. If multiple higher-low/lower-high candidates exist, which one remains the Entry Level?
2. Is the first qualifying level retained, or can the reference evolve to a newer level before activation?
3. Is the reference specifically the previous candle's extreme, a structural swing, or another level representation?
4. What exact event makes a candidate level valid?

### Secondary corroboration

TradingFinder's TradingView description states that bullish spikes form Higher Lows and bearish spikes form Lower Highs; each previous low/high is described as a potential entry level and the actual entry activates when price returns to retest that level.

URL: https://www.tradingview.com/script/Qiv9aTi0-SP2L-Pour-Samadi-Indicator-TradingFinder-Spike-2-Legs-PA/
Authority: SECONDARY

This corroborates the existence of HL/LH-based entry levels and retest behavior, but it does not uniquely discriminate first-vs-latest selection or establish a canonical swing-selection algorithm. The source is also a protected indicator description rather than the author's executable source.

### F8 finding

**PARTIALLY CLOSED / EXECUTABLE SELECTION UNRESOLVED**

Source evidence supports that prior lows/highs and the Second Leg are material to entry, but no source reviewed in this batch uniquely determines the candidate-selection algorithm. Therefore F8 remains blocked for Frozen Geometry.

No first-swing, latest-swing, structural-pivot, wick/body, or replacement rule is promoted to canonical.

## F10 — Stop-loss / invalidation price semantics

### Evidence

The primary author-controlled page explicitly states that the SL is placed behind the candle from which the Spike originated.

This is a source-confirmed origin reference, but it is not a deterministic price definition. The page does not specify:

- wick extreme vs body edge;
- open vs close;
- structural high/low vs candle high/low;
- exact buffer, if any;
- whether the buffer is fixed, percentage-based, volatility-based, or absent;
- the exact invalidation event/timing.

TradingFinder's secondary description adds the wording that bullish SL is below the spike-origin candle, "usually the lowest point before the sharp move," and bearish SL is above the spike-origin candle, "usually the highest point before the sharp drop."

URL: https://www.tradingview.com/script/Qiv9aTi0-SP2L-Pour-Samadi-Indicator-TradingFinder-Spike-2-Legs-PA/
Authority: SECONDARY

This is useful corroboration for a mirrored origin reference, but "usually" is not sufficient to define a canonical deterministic price rule. It also cannot establish a numerical buffer.

### F10 finding

**PARTIALLY CLOSED / EXACT PRICE SEMANTICS UNRESOLVED**

The source closes the conceptual origin reference: the SL is tied to the candle from which the Spike originated. It does not close the exact executable price semantics.

Therefore the following remain explicitly unresolved:

- exact wick/body/open/close/structural boundary;
- exact buffer semantics;
- exact invalidation evaluation event.

No SL buffer or boundary is inferred from the backtest engine.

## Source-aligned gate impact

| Fixture | Status after Batch 12 | Canonical executable rule? | Freeze impact |
|---|---|---|---|
| F8 | PARTIALLY CLOSED / selection unresolved | No | BLOCKED |
| F10 | PARTIALLY CLOSED / exact price unresolved | No | BLOCKED |

Frozen Geometry remains **BLOCKED**.

Untouched Validation, Robustness/Stability, Fresh Holdout, and Production remain locked/off.

## Non-negotiables preserved

- No profitability metric was used to select an interpretation.
- No swing-selection algorithm was invented.
- No Entry=C assumption was introduced.
- No SL wick/body/open/close convention was invented.
- No SL buffer was invented.
- No pending-order lifecycle was inferred.
- Baseline R-multiple behavior remains forensic only.
- 125R remains untouched.

## Next source-retrieval target

P1 should move to F11 (pending-order lifecycle) and F12 (trigger taxonomy), while continuing to seek original training transcript/frame evidence that can uniquely close F8/F10. A primary-source worked chart or transcript is required before either fixture can become executable/canonical.
