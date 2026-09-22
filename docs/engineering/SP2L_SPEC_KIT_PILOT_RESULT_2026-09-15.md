# SP2L Spec Kit Pilot Result — 2026-09-15

## Status

`ADOPT_SELECTIVELY`

This result applies only to the engineering SDD workflow demonstrated by the strategy-neutral deterministic coverage pilot. It does **not** authorize repository-wide Spec Kit installation and does not modify Strategy A research governance.

## Evidence

The pilot target is `research/engine/dataset_coverage.py`, which remains strategy-neutral and contains only deterministic historical coverage-window planning and overlap validation.

The pilot CI run for head commit `d9a666a4bd4dabdbb1abdd48c17d406b1af9110d` completed successfully:

- Workflow: `Research - SP2L Spec Kit Coverage Pilot`
- Run: `34933927018`
- Job: `coverage-pilot`
- Deterministic coverage tests: success
- Re-run of deterministic coverage tests: success
- Governance scan of executable pilot component: success

The implementation contract and tests are directly aligned: deterministic window generation, boundary handling, invalid-input rejection, adjacent-window acceptance, and overlap rejection.

## Decision

`ADOPT_SELECTIVELY` means the project may use the Spec Kit-style SDD sequence for **engineering-only, strategy-neutral work** where it improves traceability and reviewability without becoming an authority for trading semantics.

The accepted boundary is:

```text
Engineering requirement
    -> Specify
    -> Clarify
    -> Plan
    -> Tasks
    -> Implement
    -> Converge
    -> Independent review
```

This workflow is subordinate to SP2L research governance.

## Explicitly Not Adopted

No authority is delegated to the SDD workflow for:

- source interpretation;
- P-Gap geometry;
- entry/fill semantics;
- Leg-2 anchors;
- structural invalidation geometry;
- pending-order refresh thresholds;
- trigger classification;
- AB=CD anchors or tolerance;
- TP1/TP2/2X formulas;
- bearish mirror rules;
- buffers or execution thresholds;
- production BUY/SELL decisions.

Those remain governed by source evidence, manual adjudication, frozen-geometry review, and the existing research gates.

## Installation Gate

A full GitHub Spec Kit installation remains a **separate decision**. This pilot result does not install scaffolding, modify the repository constitution, or replace the existing SP2L governance layer.

Before installation, the repository should first define the exact integration boundary and confirm that Spec Kit artifacts cannot be mistaken for source-authoritative Strategy A specifications.

## Next Engineering Step

Proceed with a second small, strategy-neutral SDD pilot only if it tests a materially different engineering concern. Otherwise, stop pilot expansion and return focus to the source-resolution/evidence pipeline.
