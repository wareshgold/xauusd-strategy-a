# SP2L Synthetic Discrimination Fixtures V2 — 2026-09-09

## Purpose

These fixtures are designed to distinguish source-supported interpretations before historical optimization. They are not backtest data and do not select the winning interpretation by performance.

## Fixture F1 — First-low entry

Construct a bullish Spike with three source-recognized candles, then a correction that first trades below the first low.

Expected source behavior:
- setup remains valid before structural invalidation;
- a pending Buy Limit opportunity exists at the source-relevant first-low / first-pullback location;
- a later close-reclaim must not replace the pending-limit event.

Discrimination:
- candidate A: exact first-low price;
- candidate B: interior correction price;
- candidate C: later higher-low.

Status: source semantics favor first-low / first-pullback; exact price remains unresolved.

## Fixture F2 — P-Gap temporal variants

Create three bullish examples matching the source's three teaching constructions:
1. breakout then follow-through with P-Gap;
2. higher-low structure first, then P-Gap;
3. immediate higher-low followed by the next bearish candle.

Expected behavior:
- all three may belong to the same Spike family;
- the P-Gap detector must not assume one fixed candle index unless source evidence proves it.

Discrimination:
- fixed 3-candle FVG formula;
- breakout-context non-overlap candidate;
- source-variant state machine.

Canonical decision: remain unresolved until exact boundary semantics are source-confirmed.

## Fixture F3 — Wick/body P-Gap ambiguity

Construct identical directional sequences where wick ranges overlap but candle bodies do not, then the inverse.

Purpose:
- determine whether source P-Gap is wick-to-wick, body-to-body, or another boundary.

No historical performance is allowed to decide this fixture.

## Fixture F4 — SL anchor

Construct a Spike whose origin candle wick is materially below its body and whose structural swing low is materially separated from that wick.

Candidates:
- origin wick extreme;
- origin body boundary;
- structural swing extreme;
- source-defined invalidation line.

Source semantics favor the Spike-origin structural invalidation concept, but exact OHLC convention is unresolved.

## Fixture F5 — AB=CD anchor discrimination

Construct a Spike with:
- a clear origin;
- a clear extreme;
- a correction extreme;
- a continuation extreme;
while deliberately separating all candidate candle-level anchors.

Candidates:
- A=origin / B=spike extreme;
- A=breakout reference / B=spike extreme;
- A=source-marked candle / B=source-marked extreme;
- C=correction extreme vs entry level.

Expected result before source freeze: multiple candidates must remain representable without choosing by profitability.

## Fixture F6 — Base TP vs 2X

Create a setup where:
- base entry reaches 1R;
- the 2X trigger condition would occur later;
- an AB=CD projection differs from 1R.

Purpose:
- keep base TP, AB=CD projection, and 2X as independently versioned modules.

Source evidence currently supports base TP1 around 1R in the demonstrated management context and treats 2X separately, but exact 2X geometry remains unresolved.

## Fixture F7 — Pending-order invalidation / replacement

Create a setup where a pending order is placed, then the next candle materially changes the entry-to-SL distance.

Expected source behavior:
- pending order may be deleted/replaced when risk distance changes materially;
- exact deterministic replacement threshold is intentionally unresolved.

## Gate rule

A fixture is passed only when the implementation can represent the source-supported semantics and explicitly preserve unresolved candidates. Passing a fixture does not freeze unresolved geometry.

Historical DEV remains blocked until the source-resolution gate explicitly freezes the required geometry.
