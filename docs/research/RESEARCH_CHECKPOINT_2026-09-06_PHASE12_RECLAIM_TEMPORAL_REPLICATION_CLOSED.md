# Research Checkpoint — Phase 12 Reclaim Temporal Replication — 2026-09-06

## Status

- PHASE_12_RECLAIM_TEMPORAL_REPLICATION: CLOSED
- `triggerReclaimToRange`: descriptive association only; stable trading edge NOT ESTABLISHED
- threshold search: NONE
- optimization: NONE
- new rule: NONE
- fresh holdout: LOCKED
- production strategy: UNCHANGED

## Integrity

- Baseline pre-holdout population: 210
- Geometry join: 210/210
- Replay integrity from preceding Phase 12 geometry audit: 210/210, mismatch=0, noReplay=0
- Fresh holdout was not accessed.

## Temporal replication result

The audit tested the existing `triggerReclaimToRange` feature using fixed consecutive temporal index windows and direction/session splits. No best-window selection or threshold mining was performed.

Fixed windows with sufficient population:

| Window | N | AvgR | PF | WR | Spearman | No-exceptional Spearman |
|---|---:|---:|---:|---:|---:|---:|
| W1 | 87 | +0.3815 | 1.5353 | 28.74% | +0.3880 | +0.4997 |
| W2 | 91 | -0.1253 | 0.8298 | 26.37% | +0.2637 | +0.3486 |
| W3 | 32 | -0.1539 | 0.7762 | 31.25% | +0.1704 | +0.1830 |

The feature/outcome association remains positive in all three populated windows, including after exceptional winners are removed. This is useful descriptive replication evidence.

However, the direction/session breakdown does not establish a robust tradable edge:

- SELL+LONDON: ALL Spearman +0.3360, DEV +0.2021, VAL +0.5779, but segment performance reverses from DEV AvgR +1.3860 to VAL AvgR -0.3107.
- SELL+NEW_YORK: ALL Spearman +0.2685, DEV -0.0092, VAL +0.4175. The association does not replicate in DEV, and the segment has only N=29.
- BUY+LONDON: ALL +0.0683, DEV +0.4072, VAL -0.3645. Direction reverses out of sample.
- BUY+NEW_YORK: ALL +0.3244, DEV +0.2956, VAL +0.3267, but N=36 with only VAL N=9, and aggregate segment performance is near zero/negative.
- OUT_OF_SESSION segments are weak and not suitable as a basis for a strategy rule.

## Interpretation

The evidence supports the statement:

> `triggerReclaimToRange` is a reproducible descriptive feature association across fixed temporal windows.

It does **not** support:

> `triggerReclaimToRange` is a validated trading edge.

In particular, no fixed reclaim threshold has been validated, and the feature does not produce sufficiently stable direction/session out-of-sample evidence to justify promotion to a deterministic entry filter.

## Decision

Close the reclaim temporal replication axis. Do not reopen it through threshold optimization, best-window selection, or arbitrary session/time segmentation.

Retain `triggerReclaimToRange` as a descriptive research variable for future reporting only. No BUY/SELL rule should depend on it at this stage.

## Next research direction

Move to a new pre-entry or post-entry mechanism only if its hypothesis can be defined ex ante and tested across independent temporal segments without accessing the fresh holdout. The next axis must not be a disguised attempt to rescue reclaim geometry through threshold mining.
