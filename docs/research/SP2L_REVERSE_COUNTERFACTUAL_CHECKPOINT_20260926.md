# SP2L Reverse Counterfactual Research Checkpoint — 2026-09-26

## Purpose

Register the next research step without changing canonical Strategy A geometry.

We will evaluate a **counterfactual direction-reversal hypothesis** using the same detected SP2L signal set. This is a research experiment only.

## Current evidence boundary

The 2026-09-26 XAUUSD MT5-local replay produced 53 research signals over 2026-09-14 through 2026-09-25.

The replay currently contains 19 ambiguous outcomes. Tick-level forensics found tick coverage for all 19 ambiguous bars and showed that raw threshold chronology can differ materially from actual pending-order execution chronology.

Therefore:

- no BUY/SELL reversal is promoted to canonical;
- no direction is removed;
- no fill semantics are inferred from the backtest;
- no fixed-SL distance is selected by performance;
- the existing Strategy A geometry remains research-only and source-gated.

## Counterfactual definition

For the next experiment, keep the detected signal timestamps and signal geometry unchanged, then reverse the hypothetical trade direction:

- original BUY -> counterfactual SELL
- original SELL -> counterfactual BUY

The experiment must not alter the signal detector, P-Gap interpretation, trigger geometry, session filter, or source claims.

The reversal is a mathematical counterfactual, not a claim about the author's Strategy A.

## Required execution semantics

Because the source-confirmed fill semantics remain unresolved, any reverse test using the existing historical outcome engine must preserve and report the same ambiguity treatment. It must not convert ambiguous bars into wins/losses merely to obtain a higher apparent performance.

## Decision gate

Results may be used to compare hypotheses and design further tests, but cannot select canonical Strategy A rules.

A useful result would justify a fresh, independently defined validation experiment. It would not by itself establish a production edge.

## Next step

Implement/run a research-only reverse-direction replay on the same signal population, record all ambiguity counts and outcome bounds, then compare it with the non-reversed counterfactual under identical data and execution assumptions.
