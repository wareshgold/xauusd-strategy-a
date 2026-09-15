# MT5 Trailing Stop — Validation Plan

**Status:** PLANNED / NON-CANONICAL  
**Production:** OFF

## Validation layers

### Unit layer
- Disabled configuration produces no action.
- Missing/invalid distance produces no action.
- Proposed SL must never loosen an existing position SL.
- BUY and SELL favorable-direction semantics are tested independently.
- Non-finite prices are rejected.

### MT5 tester/runtime layer
- Validate native order-modification behavior only after execution parameters are frozen.
- Record broker stops/freeze constraints and modification failures explicitly.
- Verify that repeated ticks do not cause unintended repeated modifications.

### Research comparison layer
- Baseline: trailing OFF.
- Treatment: trailing ON under a separately frozen contract.
- Chronological, deterministic outcome labeling.
- No parameter optimization or selection from realized performance.

## Exit criteria

The feature remains OFF until deterministic unit tests, an explicit execution contract, and MT5 Strategy Tester/runtime verification all pass. A positive backtest result does not authorize production activation and cannot resolve SP2L source geometry.
