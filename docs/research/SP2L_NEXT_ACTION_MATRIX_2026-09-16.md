# SP2L Next Action Matrix — 2026-09-16

## Purpose

Prevent research-looping after the evidence-gate infrastructure is complete. This document defines the next legitimate action based on available evidence, not on a desire to produce more artifacts.

## Decision matrix

| Condition | Action | Do not do |
|---|---|---|
| New primary media/transcript/frame evidence arrives | Intake and audit against EG-01..EG-07 | Do not infer missing rules before audit |
| Existing primary evidence is unchanged | Keep source state unchanged | Do not reopen broad source hunting |
| A field passes its evidence acceptance gate | Record promotion candidate and update source-resolution audit | Do not unlock downstream validation yet |
| All 7 fields become `SOURCE_CONFIRMED` | Re-evaluate Frozen Geometry gate | Do not skip gate or directly enter production |
| Frozen Geometry becomes `READY` | Build/execute the authorized validation path on untouched data | Do not mix development and holdout data |
| Validation completes | Run predefined robustness/stability checks | Do not optimize against holdout |
| Robustness/stability passes | Run fresh holdout | Do not revise geometry after seeing holdout outcomes |
| Fresh holdout passes | Prepare production-readiness review | Do not autonomously generate live BUY/SELL decisions |

## Current actionable state

At this checkpoint:

- New primary evidence is **not present in the repository**.
- All seven evidence packages remain open.
- `SOURCE_CONFIRMED = 0/7`.
- Frozen Geometry remains `BLOCKED`.

Therefore the next substantive research event is **evidence intake**, not another planning document or another backtest.

## Loop-break rule

If no new primary evidence is available, the project must not create additional evidence-planning artifacts merely to simulate progress. Engineering may continue only where it directly improves reproducibility or gate enforcement without defining unresolved strategy meaning.

## Integrity

- No geometry change.
- No BUY/SELL generation.
- No performance-based source promotion.
- 125R remains untouched, unmodified, unclipped, and unreclassified.
