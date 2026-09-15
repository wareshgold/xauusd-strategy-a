# SP2L Spec Kit Pilot — Deterministic Coverage Infrastructure — 2026-09-15

## Status

`PILOT_SPECIFICATION_ONLY`

This is a controlled Spec Kit adoption pilot for a strategy-neutral engineering component. It does not install Spec Kit, define trading geometry, or change execution behavior.

## Pilot Target

The pilot targets the deterministic historical coverage component under `research/engine/dataset_coverage.py`.

The component is appropriate because its concern is engineering infrastructure rather than Strategy A signal semantics.

## Pilot Objective

Evaluate whether a specification-driven workflow improves:

- requirement traceability;
- deterministic behavior documentation;
- testability;
- reviewability;
- reproducibility;
- separation between requirement and implementation.

## Explicit Non-Goals

The pilot must not:

- add executable Strategy A rules;
- resolve P-Gap geometry;
- resolve entry/fill semantics;
- resolve Leg-2 geometry;
- resolve AB=CD anchors or tolerance;
- resolve targets/2X;
- resolve pending refresh semantics;
- resolve bearish mirror behavior;
- authorize BUY/SELL decisions;
- optimize parameters from backtest results.

## Proposed SDD Flow

```text
Pilot Requirement
      ↓
Specify
      ↓
Clarify
      ↓
Plan
      ↓
Tasks
      ↓
Implement
      ↓
Converge
      ↓
Independent Review
```

The pilot may use the workflow conceptually before installing repository-wide Spec Kit scaffolding. This keeps the assessment reversible.

## Required Pilot Contract

The implementation must preserve the existing engineering meaning of the coverage component. Any proposed change must be demonstrably equivalent with respect to its existing contract, or be separately reviewed as a behavior change.

No trading-specific semantics may be introduced as an implied requirement during clarification or planning.

## Evaluation Matrix

| Dimension | Pass condition |
|---|---|
| Traceability | Requirement maps to implementation and tests |
| Determinism | Same inputs produce the same result |
| Reproducibility | Another engineer can reproduce the workflow |
| Governance isolation | No unresolved Strategy A geometry is promoted |
| Reviewability | Scope and acceptance criteria are explicit |
| Overhead | Process cost is justified by the above gains |

## Adoption Gate

Pilot result must be one of:

- `ADOPT_SELECTIVELY` — measurable engineering benefit with no governance leakage;
- `REVISE_BOUNDARY` — useful but boundary/process needs adjustment;
- `REJECT_FOR_NOW` — insufficient benefit or excessive process overhead.

The result must not be selected from trading performance.

## Next Gate

No full Spec Kit installation is authorized by this document. Installation requires a separate decision after the pilot is reviewed.
