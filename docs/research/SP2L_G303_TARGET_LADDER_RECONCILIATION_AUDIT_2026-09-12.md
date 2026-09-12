# SP2L G303 — Target Ladder Reconciliation Audit

**Date:** 2026-09-12  
**Status:** `TARGET_CONCEPTS_CONFIRMED__EXECUTABLE_MAPPING_UNRESOLVED`

## Source-confirmed target vocabulary

The reviewed source sequence establishes that the target construction discusses:

- TP1
- TP2
- Round Level
- Point Distance
- numerical point examples including 250, 500 and 1000

This confirms the concepts are source-relevant, but does not uniquely define their executable mapping.

## Unresolved mappings

The following are explicitly not frozen:

- TP1 = 1R
- TP2 = 2R
- TP1 = 250 points
- TP2 = 500 points
- 1000 = total Entry→TP2 distance
- Round Level 2 as terminal target
- Round Level overriding AB=CD
- AB=CD endpoint as TP2
- final order TP as TP2
- exact XAUUSD point/tick unit
- rounding/spread treatment

## Order-panel cross-check

Previously reviewed worked order panels show different Entry/SL combinations while terminal TP values remain approximately clustered around the same price. This rejects the use of a universal `final TP = final Entry ± 2R` rule as a research assumption. It does not prove the source's alternative target formula.

## Decision

`TP1_CONCEPT = SOURCE-CONFIRMED`

`TP2_CONCEPT = SOURCE-CONFIRMED`

`ROUND_LEVEL_CONCEPT = SOURCE-CONFIRMED`

`POINT_DISTANCE_CONCEPT = SOURCE-CONFIRMED`

`TARGET_FORMULA = UNRESOLVED`

`ROUND_LEVEL_SELECTOR = UNRESOLVED`

`POINT_MAPPING = UNRESOLVED`

`TERMINAL_TP_SELECTOR = UNRESOLVED`

`CANONICAL_TARGET_ENGINE = NOT_AUTHORIZED`

No production implementation changes are authorized.
