# SP2L Synthetic Discrimination Fixtures V2 — 2026-09-09

## Purpose

These fixtures distinguish source-supported interpretations before historical optimization. They are not backtest data and do not select the winning interpretation by performance.

## Fixture F1 — Relevant higher-low entry

Construct a bullish Spike with a chain of successively higher lows. Show the source-style state where a pending Buy Limit is placed at the currently relevant/latest completed higher-low while the structural invalidation remains below the original/base low.

Expected source behavior:
- a pending Buy Limit exists during correction;
- the entry level and invalidation level are distinct;
- a later close-reclaim must not replace the pending-limit event.

Discrimination:
- candidate A: latest/relevant completed higher-low;
- candidate B: original/base low;
- candidate C: interior correction price;
- candidate D: later market close-reclaim.

Status: direct visual evidence favors candidate A for the demonstrated sequence; universal rule across all Spike variants remains unresolved.

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

Construct a Spike whose origin candle wick is materially below its body and whose structural/base low is materially separated from that wick.

Candidates:
- origin wick extreme;
- origin body boundary;
- structural/base swing extreme;
- source-defined invalidation line.

Current source evidence favors a structural/base invalidation below the entry level, but exact OHLC convention is unresolved.

## Fixture F5 — AB=CD anchor discrimination

Construct a Spike with:
- a clear origin;
- a clear extreme;
- multiple higher lows;
- a correction extreme;
- a continuation extreme;
while deliberately separating all candidate candle-level anchors.

Candidates:
- A=origin / B=spike extreme;
- A=breakout reference / B=spike extreme;
- A=source-marked candle / B=source-marked extreme;
- C=correction extreme;
- C=entry level/current higher-low.

Expected result before source freeze: multiple candidates must remain representable without choosing by profitability.

## Fixture F6 — Base TP vs 2X

Create a setup where:
- base entry reaches 1R;
- the 2X trigger condition would occur later;
- an AB=CD projection differs from 1R.

Purpose:
- keep base TP, AB=CD projection, and 2X as independently versioned modules.

Source evidence supports a distinct 2X management module, but exact target linkage remains unresolved.

## Fixture F7 — Pending-order invalidation / replacement

Create a setup where a pending order is placed, then the next candle materially changes the entry-to-SL distance.

Expected source behavior:
- pending order may be deleted/replaced when the structure changes and the risk distance is materially different;
- exact deterministic replacement threshold is intentionally unresolved.

## Fixture F8 — Moving higher-low / pending-limit refresh

Construct a bullish Spike with at least three successively higher lows. Place a pending Buy Limit at the current relevant higher-low. Then add another higher-low before price retraces.

Candidates:
- retain original order;
- move order to newest relevant higher-low;
- move order to original/base low;
- replace with market-entry logic.

Source evidence currently favors the relevant/current higher-low for the demonstrated sequence and rejects replacing the pending-limit model with a close-reclaim. The universal refresh rule is still unresolved because the source describes qualitative handling when the distance to SL changes.

## Gate rule

A fixture passes only when the implementation can represent the source-supported semantics and explicitly preserve unresolved candidates. Passing a fixture does not freeze unresolved geometry.

Historical DEV remains blocked until the source-resolution gate explicitly freezes the required geometry.
