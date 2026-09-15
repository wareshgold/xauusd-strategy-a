# MT5 Trailing Stop — Synthetic Request Contract

## Status

RESEARCH / EXECUTION-LAYER ONLY. Non-production.

The synthetic request layer validates control-flow and safety invariants. It does not define a broker-specific trailing formula.

## Required gates

A modification request may reach broker submission only when:

1. trailing is enabled;
2. the execution contract is frozen;
3. broker constraint state is known and complete;
4. the request contains finite, valid prices;
5. the proposed stop is favorable-only relative to the current stop.

The broker result then determines `MODIFICATION_ACCEPTED` or `MODIFICATION_REJECTED`.

## Synthetic request matrix

| Case | Direction | Current SL | Proposed SL | Broker | Expected |
|---|---|---:|---:|---|---|
| BUY-FAVORABLE | BUY | 3300 | 3310 | accept | ACCEPTED |
| BUY-LOOSENING | BUY | 3300 | 3290 | accept | BLOCKED locally |
| SELL-FAVORABLE | SELL | 3300 | 3290 | accept | ACCEPTED |
| SELL-LOOSENING | SELL | 3300 | 3310 | accept | BLOCKED locally |
| BROKER-REJECT | BUY | 3300 | 3310 | reject | REJECTED |

## Explicitly unresolved

No minimum stop distance, freeze distance, activation price, trailing distance, step, or evaluation cadence is selected by this contract. Values used in synthetic tests are fixtures only and must not be interpreted as production parameters.
