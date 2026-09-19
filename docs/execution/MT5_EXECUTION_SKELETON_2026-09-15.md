# MT5 Execution Skeleton — 2026-09-15

## Status

RESEARCH / ENGINEERING ONLY. No live execution and no production authorization.

## Layering

1. Strategy A research specification produces an already-authorized signal/position intent.
2. MT5 adapter maps the intent to broker/terminal operations.
3. Initial SL/TP are applied according to the separately frozen strategy/execution contract.
4. Position management operates only on an already-open position.
5. Optional trailing stop is a position-management capability and is OFF by default.

## Non-goals

This skeleton does not define P-Gap, entry geometry, trigger classification, AB=CD anchors, fill semantics, invalidation geometry, or any BUY/SELL production decision.

## Trailing boundary

The current adapter may represent trailing configuration, but must not calculate or modify SL until distance, activation, step, tick/bar semantics, and broker constraints are explicitly frozen.

## Safety invariant

A trailing-stop module must never loosen an existing protective stop. This is an engineering invariant to test; it is not a source-derived Strategy A rule.
