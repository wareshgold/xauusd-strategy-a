# SP2L G284 — Target Geometry Gate

Date: 2026-09-12
Status: BLOCKED / FAIL-CLOSED

## Current source state

Source-confirmed target concepts:

- Entry exists;
- TP1 exists;
- TP2 exists;
- SL exists;
- Round level is discussed;
- point-distance is discussed;
- AB=CD is source-confirmed elsewhere.

## Missing deterministic bridge

Still unresolved:

- exact Entry price anchor;
- exact SL OHLC boundary;
- A/B/C/D executable anchors;
- executable AB=CD projection;
- exact point unit;
- 250/500 point mapping;
- Round Level definition and selector;
- terminal TP selection;
- mapping from schematic targets to order-panel TP;
- bearish target mirror;
- rounding/spread/execution semantics.

## Gate decision

The new visual evidence strengthens the source ledger but does not close the geometry gap. Therefore:

`SOURCE_RESOLUTION = PARTIAL`
`FROZEN_GEOMETRY = BLOCKED`
`CANONICAL_TARGET_ENGINE = NOT_AUTHORIZED`
`BACKTEST_OPTIMIZATION_FOR_TARGETS = PROHIBITED`
`LIVE_BUY_SELL_AUTHORIZATION = NO`

The next research step should search for a source example containing explicit price labels and an explicit statement tying those prices to TP1/TP2, 250/500 point distances, Round Level, or AB=CD. If that bridge cannot be found, the unresolved target geometry must remain an explicit production blocker rather than being selected by backtest performance.
