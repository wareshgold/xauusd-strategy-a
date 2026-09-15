# MT5 Adapter Implementation Gate — 2026-09-15

## Status

RESEARCH / EXECUTION-LAYER ONLY

This gate defines the boundary for a future MT5-native position-modification adapter. It does not define Strategy A geometry, trailing parameters, or production execution behavior.

## Implemented now

- Position modification request type with position identity, direction, current stop-loss, and proposed stop-loss.
- Deterministic request validation for identity and finite prices.
- Explicit `BROKER_CONSTRAINTS_UNFROZEN` refusal boundary.
- Adapter interface that can later be implemented by an MT5-native runtime.
- Unit tests for the boundary invariants.

## Deliberately not implemented

- No `.mq5` expert advisor.
- No broker stop-level or freeze-level numbers.
- No trailing distance, activation, or step values.
- No tick/bar evaluation convention.
- No fill or order-execution semantics.
- No Strategy A BUY/SELL generation.
- No automatic position modification.

## Required freeze before native adapter implementation

1. Execution parameters are explicitly frozen independently of backtest performance.
2. Broker constraints and their runtime representation are defined.
3. Favorable-only stop movement is preserved for BUY and SELL.
4. Existing structural SL interaction is explicitly defined.
5. Research/runtime parity is testable.
6. MT5 Strategy Tester and runtime verification are available.

Until those conditions are satisfied, an implementation may expose interfaces and deterministic refusal paths, but must not issue live modification requests.
