# G399 — SP2L Semantic Core Freeze

Date: 2026-09-13  
Gate: SOURCE RESOLUTION / FROZEN GEOMETRY  
Status: **SEMANTIC CORE FROZEN / EXECUTABLE GEOMETRY BLOCKED**

## Purpose

Freeze only the meaning that is supported by the current authoritative source corpus. This document is not an executable Strategy A specification and does not authorize DEV/VAL optimization.

G398 established that the semantic core is source-confirmed/source-supported while executable geometry remains unresolved. G399 turns that boundary into an explicit research artifact and code guard.

## Frozen semantic core

1. Strategy A is SP2L: Spike → 2 Leg.
2. The first directional movement is associated with breakout and follow-through.
3. A valid breakout is associated with P-Gap.
4. A correction follows the first leg/spike structure.
5. Entry uses a pending-limit order during the correction until activation.
6. The setup has structural invalidation/stop semantics.
7. The setup seeks continuation as a second leg.
8. The source explicitly defines an AB = CD relationship between the legs.
9. TP1/TP2 and R1/R2 are source-defined outcome terminology.

## Explicitly unresolved

- P-Gap OHLC geometry and formula.
- Exact A/B/C anchors and wick/body semantics.
- AB=CD equality tolerance.
- Exact pending-limit price and fill semantics.
- Trigger timing, pending persistence, activation, and invalidation-before-fill.
- Exact structural stop boundary and executable stop price.
- Executable mapping from TP1/TP2 terminology to target prices.

## Guard rules

The semantic core must not create a `ResearchCandidate` or any executable canonical order. No candidate formula is selected by this gate.

The G396 provenance registry remains authoritative for unresolved hypotheses. All G395 hypotheses remain noncanonical until a later authoritative source bridge resolves the corresponding executable dimension.

## Gate decision

`G399 = PASS`

`SEMANTIC CORE = FROZEN`
`EXECUTABLE GEOMETRY = UNRESOLVED`
`FROZEN GEOMETRY = BLOCKED`
`DEV = BLOCKED`
`VAL = BLOCKED`
`FRESH HOLDOUT = NOT AUTHORIZED`
`PRODUCTION = BLOCKED`

## Permitted next step

Continue with non-canonical deterministic research harness work: provenance, dataset reproducibility, fixture coverage, and counterfactual evaluation. The next executable strategy gate requires genuinely new authoritative source evidence for the unresolved geometry/execution dimensions.
