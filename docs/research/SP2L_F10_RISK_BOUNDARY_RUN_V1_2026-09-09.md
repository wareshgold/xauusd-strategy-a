# SP2L F10 Risk Boundary Run V1 — 2026-09-09

## Scope

F10 tests the boundary between source-defined Strategy A geometry and account-level risk management. It is synthetic only; no historical data or profitability result is used to select stop geometry.

## Test result

PASS for the risk-management invariant:

> Changing the risk budget changes position size, while Entry and the supplied structural stop remain unchanged.

The fixture also keeps competing stop anchors distinct: wick extreme, body edge, base/deeper structural swing, and relevant/current swing. The fixture does not claim any one of them is canonical.

## Interpretation

This validates the architectural rule:

`Strategy geometry → Entry + Structural Invalidation/Stop → Stop Distance → Risk Budget → Position Size`

Therefore a risk percentage cannot be used to infer or move the Strategy A stop.

## Important limitation

F10 does **not** resolve which OHLC point the source uses for structural invalidation. Wick-vs-body, base-vs-relevant swing, and any stop buffer/offset remain unresolved source questions.

No ATR stop, fixed-point stop, percentage stop, or risk-derived stop is introduced.

## Gate decision

**F10 SYNTHETIC INVARIANT: PASS**

**SOURCE RESOLUTION: unchanged / partial pass**

**FROZEN GEOMETRY: BLOCKED**

Historical DEV/VAL/Fresh Holdout and production implementation remain locked.

## Next step

Proceed to F11: dynamic pending-order update. Test KEEP/DELETE/REPLACE state transitions while deliberately refusing to invent the teacher's qualitative "materially different" replacement threshold.
