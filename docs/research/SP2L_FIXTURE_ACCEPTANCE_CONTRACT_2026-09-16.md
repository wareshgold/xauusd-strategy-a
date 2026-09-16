# SP2L Fixture Acceptance Contract — 2026-09-16

## Status

RESEARCH-ONLY. This contract defines how F8–F15 fixtures will be judged; it does not define Strategy A geometry.

## Acceptance states

- `SOURCE_DISCRIMINATED`: fixture behavior is uniquely supported by the resolved source evidence.
- `UNRESOLVED`: multiple interpretations remain compatible with the source or fixture does not discriminate them.
- `IMPLEMENTATION_ERROR`: fixture/test infrastructure is incorrect or non-deterministic.

## Rules

1. Never select an interpretation because it improves win rate, expectancy, PF, drawdown, or any other performance metric.
2. Never convert an unresolved geometry question into a numeric parameter search.
3. Every fixture must assert observable structural relationships, not profitability.
4. Bearish fixtures must mirror the exact question tested by their bullish counterpart where source symmetry is established.
5. Execution semantics remain separate from geometry semantics.
6. A passing fixture suite is necessary but not sufficient for Frozen Geometry; source evidence must also support the rule.

## F8–F15 acceptance intent

F8: distinguish structural reference candidates for relevant Low/High.

F9: demonstrate that Entry and Start-of-Leg-2 are not accidentally conflated.

F10: distinguish structural invalidation from risk-budget stop and expose wick/body differences.

F11: verify pending-order state transitions without inventing a replacement threshold.

F12: enumerate 1-, 2-, and 3-candle trigger observations without choosing a taxonomy unsupported by source.

F13: expose competing 2X interpretations without selecting one by performance.

F14: expose competing A/B/C/D anchors for AB=CD without introducing an undocumented tolerance.

F15: mirror source-supported questions for bearish direction.

## Gate

If any fixture exposes multiple source-consistent outcomes, the corresponding geometry remains `UNRESOLVED` and Frozen Geometry remains blocked.
