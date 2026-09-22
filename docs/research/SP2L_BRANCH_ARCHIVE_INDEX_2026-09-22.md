# SP2L Branch Archive & Cleanup Index — 2026-09-22

## Purpose

This document is the preservation index for the historical SP2L Git branches before branch cleanup.

The cleanup rule is:

1. Preserve source evidence, decisions, audit results, test contracts, and reproducibility information in repository documents.
2. Do not use old branch names as the source of truth once their useful information is represented in the current documentation.
3. Consolidate duplicate branches that point to the same commit.
4. Remove temporary/redundant historical branches only after their commit is represented by another retained branch or its useful evidence is documented.
5. Never remove the active forward-test branch:
   - `research/sp2l-f13-demo-forward-slfixed-2026-09-21`
6. Never promote historical research conclusions to canonical rules merely because they survive branch cleanup.

## Current retained anchor

- Active branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`
- Current HEAD: `b598ca1574aa7b8993fee79344fb768e019ebfb9`
- Purpose: live/demo forward observability and lifecycle validation.
- Canonical Strategy A status: unchanged; forward-test telemetry is research-only.

## Historical branch families confirmed as duplicate snapshots

The following families were observed to contain multiple branch names pointing to the same commit. Their duplicate names do not provide independent evidence.

### 2026-09-15 session snapshots
- Commit: `a49fa5134336c0c9bb78bf3693afe13494da95c5`
- Duplicate family includes:
  - `checkpoint/session-snapshot-2026-09-15`
  - `checkpoint/session-snapshot-2026-09-15-c`
  - `checkpoint/session-snapshot-2026-09-15-d`
  - `checkpoint/session-snapshot-2026-09-15-e`
  - `checkpoint/session-snapshot-2026-09-15-f`
  - `checkpoint/session-snapshot-2026-09-15-final`
  - `checkpoint/session-snapshot-2026-09-15-z`
  - `checkpoint/session-snapshot-2026-09-15-zz`
  - `checkpoint/session-snapshot-2026-09-15-zz2`
  - `checkpoint/session-snapshot-2026-09-15-zz3`
  - `checkpoint/session-snapshot-2026-09-15b`
- Also observed at the same commit: `research/mt5-trailing-stop-execution-2026-09-15`

### 2026-09-15 session snapshot final variants
- Commit: `cf1234647f0da9ddde9dd8ddc63d0c82250dc8b6`
- Duplicate family:
  - `checkpoint/session-snapshot-2026-09-15-final2`
  - `checkpoint/session-snapshot-2026-09-15-unique`
  - `checkpoint/session-snapshot-2026-09-15-unique2`
  - `checkpoint/session-snapshot-2026-09-15-unique3`

### Entry-trigger mechanics
- Commit: `f0f6f1168d59e022601b396a4c3bd75f0bf7a837`
- Multiple `research/entry-trigger-*` branches point to the same snapshot.
- These are candidates for consolidation after confirming their useful findings are represented in the current source/evidence documents.

### Excursion / stop-stress research
- Commit: `c8d4a6ae89a2a0f282c31df4d82f9f5050c1c25d`
- Multiple `research/excursion-topology-*` and `research/outcome-stop-stress-*` variants point to the same snapshot.
- Preserve only the resulting evidence/decision documents, not every temporary branch name.

### Gate-preparation variants
- Commit: `851ae2eef29c1e909a364f1f4790d32d90b27f43`
- `research/sp2l-gate-preparation-v1` through `v19` and `final` variants were observed on the same commit.
- These are duplicate snapshots, not separate research states.

### G368 hypothesis-layer variants
- Commit: `a3731aeee903fe5cb8f5a2c3b0403259b28117bc`
- Numerous `research/sp2l-g368-hypothesis-layer-*` variants point to the same snapshot.
- Preserve the evidence represented in the current research documents; duplicate branch names are not required.

### G350 official-source audit variants
- Commit: `4ff65ab126bc382ff2ec539e88a0ff9432975e25`
- Multiple G349/G350 official-source audit variants point to the same snapshot.

### G413 source-geometry reconciliation variants
- Commit: `c50f3dafa48? `
- Multiple G413 v2-v8 variants were observed as duplicate snapshots. Exact commit should be re-read before deletion; this entry is intentionally not a deletion authority.

## Important single-branch historical anchors

These should not be deleted merely because they are old. Their evidence must first be confirmed in the current documentation:

- `research/sp2l-pgap-source-reconstruction-2026-09-21`
- `research/sp2l-batch40-pgap-contamination-audit-2026-09-21`
- `research/sp2l-batch42-pgap-sl-synthetic-fixtures-2026-09-21`
- `research/sp2l-batch43-pgap-mt5-candidate-comparison-2026-09-21`
- `research/sp2l-batch44-source-code-pgap-reconciliation-2026-09-21`
- `research/sp2l-batch46-source-blocker-closure-2026-09-21`
- `research/sp2l-author-site-f13-source-update-2026-09-21`
- `research/sp2l-f13-source-reconciliation-2026-09-21`
- `research/sp2l-f13-2x-synthetic-fixtures-2026-09-21`
- `research/sp2l-f13-2x-tp1-fixture-2026-09-14`

These names are evidence pointers only. They do not by themselves establish that a rule is canonical.

## Cleanup status

- Phase A — inventory: COMPLETE (initial inventory)
- Phase B — duplicate-family identification: IN PROGRESS
- Phase C — evidence preservation into current docs: IN PROGRESS
- Phase D — branch deletion: NOT YET PERFORMED
- Phase E — post-cleanup branch audit: REQUIRED

## Safety rule

No deletion should remove the only copy of a source artifact, forensic result, synthetic fixture, gate decision, or reproducibility record.

No cleanup action changes Strategy A geometry, P-Gap semantics, AB=CD anchors/tolerance, fill semantics, execution semantics, or canonical status.
