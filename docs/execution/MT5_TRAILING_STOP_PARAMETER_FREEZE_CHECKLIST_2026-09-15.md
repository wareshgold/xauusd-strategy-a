# MT5 Trailing Stop — Parameter Freeze Checklist

**Status:** ENGINEERING GATE / NON-CANONICAL  
**Production:** OFF

This checklist defines what must be explicitly decided before a trailing-stop formula can be implemented. It does not choose the values.

## Required decisions

1. Distance: fixed price distance or another explicitly defined method.
2. Activation: exact condition under which trailing becomes eligible.
3. Step: exact minimum movement between SL modifications, or explicit no-step policy.
4. Evaluation clock: tick-based, bar-based, or another deterministic runtime event.
5. Direction: favorable-only movement; exact BUY/SELL inequalities must be tested.
6. Existing SL interaction: exact rule when proposed trailing SL is worse than current SL.
7. Broker constraints: stops level, freeze level, spread, precision, and rejection handling.
8. Research/runtime parity: whether research simulation must reproduce the same execution semantics.

## Gate rule

Until every item has an explicit written value/semantic, the implementation must remain inert and must not modify an open position's SL.

No value may be selected because it improves backtest performance. Performance evaluation belongs to a separately preregistered experiment after the execution contract is frozen.

## Baseline protection

- Strategy A geometry is unchanged.
- Current research baseline remains no trailing stop.
- Initial SL working test remains 50/60/70/80 pips with target 2.0R.
- Trailing-on results, if tested later, are a separate treatment.
- This document does not authorize BUY/SELL or production activation.
