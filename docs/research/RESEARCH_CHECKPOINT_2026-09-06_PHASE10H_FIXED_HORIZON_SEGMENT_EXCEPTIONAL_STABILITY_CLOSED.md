# Research Checkpoint — Phase 10H Closed

Date: 2026-09-06
Branch: `research/ny-sell-preentry-temporal-replication`

## Scope

Phase 10H audited the four fixed close-to-close exit horizons from Phase 10F (H3/H5/H10/H20) across exhaustive direction/session segments after removing canonical exceptional winners (`baseline rMultiple >= 5R`).

Population remained pre-holdout DELAY1 only: N=144, DEV=91, VAL=53. Fresh holdout remained locked.

Segments:
- SELL+NEW_YORK
- SELL+LONDON
- BUY+NEW_YORK
- BUY+LONDON
- OUT_OF_SESSION

## Integrity

- baseline pre-holdout: 210
- canonical DELAY1: 144
- matched: 144/144
- path complete: true
- deterministic rerun: true
- segmentation: 144/144
- Fresh accessed: no
- production changed: no
- optimization: no
- horizon selection: no
- new rule: no

## Results

After exceptional-winner removal:

| Horizon | ALL AvgR | PF | DEV AvgR | VAL AvgR |
|---|---:|---:|---:|---:|
| H3 | 3.5211 | 3.2508 | 1.1825 | 7.5106 |
| H5 | 4.3989 | 3.5324 | 2.2044 | 8.1425 |
| H10 | 2.3757 | 1.6118 | -0.3924 | 7.0978 |
| H20 | 1.8408 | 1.4369 | 1.8504 | 1.8245 |

## Segment findings

H20 was the most temporally balanced aggregate horizon, but segment stability failed:

- SELL+NEW_YORK: DEV +0.8311R vs VAL -27.4229R; PF 1.3140 vs 0.0378.
- SELL+LONDON: DEV +4.6209R vs VAL +12.2086R; PF 4.8190 vs 3.7086.
- BUY+NEW_YORK: DEV -0.6137R vs VAL +4.4353R; VAL N=5.
- BUY+LONDON: DEV +2.2969R vs VAL +8.6057R.
- OUT_OF_SESSION: DEV -0.8925R vs VAL +3.4884R.

H3/H5/H10 also show substantial segment heterogeneity and cannot be promoted as stable exits.

## Decision

`PHASE_10H = CLOSED`

`FIXED_HORIZON_EXIT_EDGE = NOT_ESTABLISHED`

`H3 = REJECTED_AS_STABLE`

`H5 = REJECTED_AS_STABLE`

`H10 = REJECTED_AS_STABLE`

`H20 = REJECTED_AS_VALIDATED_RULE`

H20 remains an observationally interesting candidate because aggregate DEV/VAL AvgR is unusually balanced, but selecting it would be post-hoc and is therefore prohibited. The SELL+NEW_YORK collapse demonstrates that the aggregate result is not a sufficiently stable system-wide exit edge.

## Methodological conclusion

The Phase 10 fixed-horizon family has not established a generalizable exit-management edge. The research should not continue by mining horizons, sessions, or segment-specific thresholds.

Next research should move away from fixed-horizon exit selection and investigate a new pre-entry/post-entry mechanism only if it can be defined ex ante and validated across independent temporal segments without opening Fresh holdout.
