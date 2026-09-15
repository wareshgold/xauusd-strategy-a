# MT5 Native Mapping Contract — 2026-09-15

## Status

RESEARCH / EXECUTION-LAYER ONLY

This document defines an adapter mapping boundary only. It does not freeze trailing-stop parameters or define Strategy A signals.

## Boundary

The research/runtime layer produces a position-modification request containing:

- position identity
- position direction
- current stop-loss, when known
- proposed stop-loss

The future MT5-native adapter is responsible for translating that request into a native position-modification operation.

## Mandatory refusal conditions

The adapter must not submit a modification when:

- the request identity is invalid;
- any required price is non-finite;
- broker stop/freeze constraints are unknown or incomplete;
- the execution contract is not frozen;
- the proposed stop would loosen the existing stop;
- required MT5 runtime state is unavailable.

## Explicit non-goals

This boundary does not decide:

- trailing distance;
- activation condition;
- step size;
- evaluation clock;
- broker-specific numeric limits;
- Strategy A entry, stop, target, P-Gap, AB=CD, or bearish geometry.

Those remain separately governed decisions.

## Verification path

1. Unit-test the adapter boundary with synthetic requests.
2. Verify native mapping in MT5 Strategy Tester after the execution contract is frozen.
3. Verify broker/runtime rejection handling.
4. Compare research and runtime behavior without changing the research baseline.
5. Keep trailing treatment separate from the no-trailing baseline.
