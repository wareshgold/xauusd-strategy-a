# G295 — Fixed Target vs Final Entry Audit

Date: 2026-09-12
Source: primary SP2L video `7HEC5mO3d3U`; same worked order sequence reviewed at high resolution.

## Finding
The worked order panel provides a strong negative test against the hypothesis that the terminal TP is always calculated from the final order Entry and SL.

Observed rows:

| Row | Entry | SL | TP | Entry→TP | Risk | TP distance / Risk |
|---|---:|---:|---:|---:|---:|---:|
| A | 3229.08 | 3237.12 | 3213.44 | 15.64 | 8.04 | 1.945R |
| B | 3223.84 | 3235.50 | 3213.33 | 10.51 | 11.66 | 0.901R |
| C | 3228.88 | 3235.50 | 3213.45 | 15.43 | 6.62 | 2.331R |

## Interpretation boundary

The near-constant TP across A/B/C while Entries and SLs vary means at least one of the following must be true:

1. the target was established independently before later order variations;
2. the target is a source price/level projection independent of final Entry;
3. the visible rows represent distinct order states sharing a preconstructed target.

The evidence does not distinguish these alternatives.

## Important consequence

A production engine must not calculate terminal TP from the final filled Entry merely because the measurement ladder visually resembles R-multiple levels.

The correct source question is now narrower:

> What source-defined reference generates the fixed target level that survives changes in Entry?

Candidates remain research-only: original measurement ladder, Leg 1/AB=CD projection, Point Distance, Round Level, or another source-defined level.

## Status
`TARGET_ANCHOR_DEPENDENCE = UNRESOLVED`
`FINAL_ENTRY_RECALCULATION = NOT_SUPPORTED_BY_WORKED_EXAMPLE`
`CANONICAL_TARGET_FORMULA = BLOCKED`

No production target rule is authorized by this audit.
