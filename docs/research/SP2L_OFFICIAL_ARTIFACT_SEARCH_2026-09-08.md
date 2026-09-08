# SP2L Official Artifact Search — 2026-09-08

## Objective

Search official Mohammad Ali Poursamadi resources for a source artifact that could resolve the remaining OHLC geometry blockers: exact P-Gap boundary/timing, exact Entry candle identity, exact SL price convention, and exact Leg-1/AB=CD anchors.

## Sources searched

1. Official SP2L strategy page: https://poursamadi.com/sp2l-strategy/
2. Official English SP2L strategy page: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/
3. Official tools/indicators index: https://poursamadi.com/tools/
4. Official English tools/indicators index: https://poursamadi.com/en/auxiliary-tools-and-indicators/
5. Official site navigation and strategy/tool sections.

The official SP2L pages currently expose semantic material including: valid Spike requires P-Gap; bullish correction reaches the low of the previous candle; bearish correction reaches the high of the previous candle; SL is behind the candle from which the Spike originated; default TP is 1:1; and exact entry conditions should be defined and backtested before live use.

## Artifact-search result

No publicly indexed official downloadable SP2L indicator/template/source-code artifact was found that exposes the exact P-Gap OHLC formula or exact Entry/SL numeric convention.

The official tools index lists general tools such as Weekly Map, Candle Time, Open & Close, Round Levels, Spread, and Pip Value, but does not expose a public SP2L source-code implementation in the indexed material.

## Important negative evidence

The absence of a public official implementation is itself relevant: it means the remaining exact geometry cannot be safely recovered from an official executable artifact found through the public site index.

Do NOT substitute the closed-source TradingView/TradingFinder implementation for the primary source. Third-party claims such as three-candle definitions, body-percentage thresholds, spike-size thresholds, or alternative entry triggers remain external hypotheses only.

## Resolution impact

### Source-confirmed / semantic

- Spike requires P-Gap in the source-defined sense.
- P-Gap is associated with valid breakout/spike context.
- Bullish correction references a previous/relevant Low.
- Bearish correction references a previous/relevant High.
- Entry is executed in the Spike direction.
- Source video demonstrates manual/pre-set pending-limit execution.
- SL is structurally behind the Spike-origin candle.
- Base TP is 1:1.
- Second leg follows the first-leg magnitude relationship / AB=CD concept.

### Still unresolved

- Exact P-Gap boundaries: wick vs body vs other source geometry.
- Exact P-Gap candle timing/pair relation across all accepted Spike variants.
- Equality/touch rule and minimum gap threshold.
- Exact universal Entry candle identity across variants.
- Exact pending-limit price convention beyond the source-level semantic.
- Exact executable SL price: wick/body/offset/buffer.
- Exact Leg-1 OHLC anchors and AB=CD tolerance.
- Intrabar fill ordering semantics.

## Gate decision

No new canonical formula is promoted from this search.

FROZEN GEOMETRY remains BLOCKED.
DEV / VAL / Fresh Holdout remain locked.
Production remains unchanged.

## Next research action

Use the already-uploaded authoritative source video and existing timestamped transcript as the primary evidence. Perform one final source-frame audit focused only on the remaining discriminators. If the source still does not uniquely identify the exact OHLC geometry, formally close SOURCE RESOLUTION as "semantic resolved / executable geometry unresolved" rather than importing third-party implementation details.
