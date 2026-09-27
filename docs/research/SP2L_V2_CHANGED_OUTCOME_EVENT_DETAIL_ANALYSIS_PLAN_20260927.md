# SP2L V2 Changed-Outcome Event Detail Analysis Plan — 2026-09-27

## Status

RESEARCH-ONLY. This checkpoint does not define or promote canonical execution semantics.

## Current evidence

The changed-outcome forensic population contains 18 common signals:

- 12 FIRST_EVENT_DIFFERENCE cases, accounting for +24R.
- 4 SAME_BAR cases.
- 2 UNRESOLVED cases.

The detailed event artifact is generated locally at:

artifacts/forensic/2026-09-27/SP2L_V2_CHANGED_OUTCOME_EVENT_DETAIL_FORENSICS_20260927.json

## Next deterministic analysis

For each selected case:

1. Preserve the original fingerprint and R delta.
2. Record the Baseline first event and Reference first event.
3. Count event-pair directions, including TP→SL, SL→TP, BOTH_SAME_M1, and unresolved combinations.
4. Preserve exact event timestamps and M1 OHLC where present.
5. Aggregate R delta by event-pair type.
6. Keep UNRESOLVED separate.
7. Do not infer that an event-pair is caused by fill timing, gaps, or execution semantics without complete M1 path coverage.

## Important coverage constraint

The existing event forensic tool unions four recorded context windows. A NO_LEVEL_TOUCH result is not proof that no touch occurred outside those stored windows. Therefore this analysis is descriptive and must not be used to select canonical fill/exit rules.

## Promotion gate

No canonical rule change is permitted from this artifact alone. If event-pair evidence points to a possible execution-semantic issue, the next stage is complete-path reconstruction from raw MT5 M1 data for the affected cases, followed by deterministic comparison.

Search token: SP2L_V2_CHANGED_OUTCOME_EVENT_DETAIL_ANALYSIS_PLAN_20260927
