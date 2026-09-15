# MT5 Trailing Stop — MQL5 Adapter Boundary

**Status:** DESIGN ONLY / NON-CANONICAL  
**Production:** OFF

## Responsibility

The future MQL5 adapter may translate a frozen execution contract into native MT5 position modification requests. It must not calculate or redefine Strategy A geometry.

## Required adapter inputs

- position ticket/identity;
- position direction;
- current position Stop Loss;
- current market price/tick;
- frozen trailing execution contract;
- broker symbol constraints and terminal modification result.

## Required invariants

1. Disabled or unfrozen contract => no modification request.
2. Proposed SL may not loosen the existing SL.
3. BUY and SELL direction rules are tested independently.
4. Invalid/non-finite price inputs are rejected.
5. Broker rejection is observable and does not mutate research state.
6. Adapter has no authority over Strategy A entry, P-Gap, correction, AB=CD, trigger, invalidation, or target geometry.

## Not implemented here

No MQL5 EA is claimed by this document. Exact trailing distance, activation, step, evaluation clock, and broker-handling semantics remain unresolved until explicitly frozen.
