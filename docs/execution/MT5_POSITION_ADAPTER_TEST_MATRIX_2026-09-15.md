# MT5 Position Adapter — Test Matrix — 2026-09-15

**Status:** RESEARCH / ENGINEERING ONLY  
**Production:** OFF  
**Strategy geometry:** UNCHANGED

## Purpose

Define deterministic adapter-boundary cases without choosing trailing parameters or MT5 broker values.

| Case | Expected result |
|---|---|
| Execution disabled | No modification request |
| Execution enabled but any required execution state is unfrozen | No modification request |
| Empty position ticket | Invalid input |
| Non-finite proposed Stop Loss | Invalid input |
| BUY proposed Stop Loss below current Stop Loss | Reject / no modification |
| SELL proposed Stop Loss above current Stop Loss | Reject / no modification |
| Favorable BUY proposal | Adapter request may be constructed once the contract is frozen |
| Favorable SELL proposal | Adapter request may be constructed once the contract is frozen |

## Deliberate exclusions

This matrix does not define:

- trailing distance;
- activation threshold;
- step size;
- tick/bar evaluation semantics;
- stops level or freeze level numeric values;
- spread policy;
- fill semantics;
- Strategy A geometry;
- BUY/SELL production decisions.

Those remain separate engineering/source-resolution gates.

## Acceptance boundary

A request constructed by this layer is only an adapter-level intent. Native MT5 order modification, broker acceptance/rejection, and runtime verification remain a later integration step after the execution contract is explicitly frozen.
