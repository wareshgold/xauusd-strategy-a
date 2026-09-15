# MT5 Trailing Stop — Deterministic Execution State Machine

## Status

RESEARCH / EXECUTION-LAYER ONLY.

This document freezes only the **control-flow states**, not trailing-stop parameters.

## Deterministic state order

1. `TRAILING_DISABLED`
2. `CONTRACT_BLOCKED`
3. `BROKER_CONSTRAINT_BLOCKED`
4. `REQUEST_INVALID`
5. `MODIFICATION_REJECTED`
6. `MODIFICATION_ACCEPTED`

The first failing gate wins. No later state may be reached after an earlier gate fails.

## Synthetic scenarios

| ID | Condition | Expected state |
|---|---|---|
| A | trailing disabled | `TRAILING_DISABLED` |
| B | execution contract not frozen | `CONTRACT_BLOCKED` |
| C | broker constraints unknown | `BROKER_CONSTRAINT_BLOCKED` |
| D | request invalid | `REQUEST_INVALID` |
| E | BUY proposed SL is favorable; broker accepts | `MODIFICATION_ACCEPTED` |
| F | BUY proposed SL loosens risk | `REQUEST_INVALID` |
| G | SELL proposed SL is favorable; broker accepts | `MODIFICATION_ACCEPTED` |
| H | SELL proposed SL loosens risk | `REQUEST_INVALID` |
| I | local gates pass; MT5/broker rejects | `MODIFICATION_REJECTED` |
| J | all gates pass; MT5/broker accepts | `MODIFICATION_ACCEPTED` |

## Explicit non-decisions

This state machine does **not** define:

- trailing distance
- activation threshold
- step size
- tick vs bar evaluation
- broker minimum/freeze-distance values
- fill semantics
- Strategy A geometry
- production BUY/SELL generation

Those remain separately frozen or unresolved under their respective contracts.

## Safety invariant

A stop modification is never accepted when it moves the stop against the position's favorable direction. For BUY, proposed SL must not be below the current SL; for SELL, proposed SL must not be above the current SL.
