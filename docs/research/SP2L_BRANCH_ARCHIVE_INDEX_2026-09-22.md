# SP2L Branch Archive & Cleanup Index — 2026-09-22

## Purpose

This document preserves the historical branch-cleanup record before redundant branches are removed.

Cleanup rules:
1. Preserve source evidence, decisions, audit results, test contracts, and reproducibility information in repository documents.
2. Old branch names are not evidence by themselves once their useful content is preserved elsewhere.
3. Consolidate duplicate branches that point to the same commit.
4. Remove temporary/redundant branches only after their useful information is preserved and the commit has another retained reference.
5. Never remove the active forward-test branch `research/sp2l-f13-demo-forward-slfixed-2026-09-21`.
6. Branch cleanup never promotes a research result to a canonical Strategy A rule.

## Current retained anchor

- Branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`
- HEAD at audit start: `b598ca1574aa7b8993fee79344fb768e019ebfb9`
- Role: demo forward observability/lifecycle validation.
- Canonical status: unchanged; telemetry remains research-only.

## Confirmed duplicate branch families

These families were observed with multiple branch names pointing to the same commit.

### 2026-09-15 session snapshots
Commit `a49fa5134336c0c9bb78bf3693afe13494da95c5`.

Duplicate names include:
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
- `research/mt5-trailing-stop-execution-2026-09-15`

### 2026-09-15 final/unique snapshots
Commit `cf1234647f0da9ddde9dd8ddc63d0c82250dc8b6`.

Duplicate names:
- `checkpoint/session-snapshot-2026-09-15-final2`
- `checkpoint/session-snapshot-2026-09-15-unique`
- `checkpoint/session-snapshot-2026-09-15-unique2`
- `checkpoint/session-snapshot-2026-09-15-unique3`

### Entry-trigger mechanics
Commit `f0f6f1168d59e022601b396a4c3bd75f0bf7a837`.

Multiple `research/entry-trigger-*` variants point to this same snapshot.

### Excursion / stop-stress
Commit `c8d4a6ae89a2a0f282c31df4d82f9f5050c1c25d`.

Multiple `research/excursion-topology-*` and `research/outcome-stop-stress-*` variants point to this same snapshot.

### Gate preparation
Commit `851ae2eef29c1e909a364f1f4790d32d90b27f43`.

The `research/sp2l-gate-preparation-v1...v19` and final variants are duplicate snapshots.

### G368 hypothesis layer
Commit `a3731aeee903fe5cb8f5a2c3b0403259b28117bc`.

Numerous `research/sp2l-g368-hypothesis-layer-*` variants point to this same snapshot.

### G350 official-source audit
Commit `4ff65ab126bc382ff2ec539e88a0ff9432975e25`.

Multiple G349/G350 variants point to the same snapshot.

### G413 source-geometry reconciliation
Exact tip must be re-queried from the retained G413 branch family before deletion; the earlier recorded SHA was inconsistent with GitHub and is not treated as authoritative.

Multiple `research/sp2l-g413-source-geometry-reconciliation-2026-09-14-v2...v8` variants point to this same snapshot.

## Historical branches requiring evidence-preservation check before deletion

These are not automatically deletable merely because they are old:

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

These are evidence pointers, not canonical-rule authorities.

## Preserved evidence archive

Durable historical evidence from the 2026-09-08 source-resolution/gate work and 2026-09-15 MT5 execution-layer work is consolidated in:
`docs/research/archive/SP2L_HISTORICAL_EVIDENCE_ARCHIVE_2026-09-22.md`

The archive preserves source conclusions, unresolved geometry, execution-layer boundaries, and the rule that historical performance cannot choose source semantics. Obsolete implementation files and duplicate generated outputs are not copied unless they are uniquely evidentiary.

## Cleanup phases

- Inventory: COMPLETE (initial inventory)
- Duplicate-family identification: COMPLETE for the families listed above
- Evidence preservation: COMPLETE for G350/G368 and previously deleted families
- Branch deletion: G350 COMPLETE (13 branches); G368 COMPLETE (29 branches); prior listed duplicate families COMPLETE
- Post-cleanup audit: IN PROGRESS

## Safety

No deletion should remove the only copy of a source artifact, forensic result, synthetic fixture, gate decision, or reproducibility record.

No cleanup action changes Strategy A geometry, P-Gap semantics, AB=CD anchors/tolerance, fill semantics, execution semantics, or canonical status.


### 2026-09-15 snapshot cleanup decision

The 2026-09-15 snapshot family was rechecked by exact branch-tip SHA. The family contains:
- `a49fa5134336c0c9bb78bf3693afe13494da95c5` — shared by the standard/session/final/z/zz/zz2/zz3/b/trailing-stop refs;
- `cf1234647f0da9ddde9dd8ddc63d0c82250dc8b6` — shared by final2/unique/unique2/unique3;
- `3682250ec551ac84fcac07ea7a658a9d5c7e8a2e` — unique4, separately reviewed and its durable evidence preserved in `docs/research/archive/SP2L_HISTORICAL_EVIDENCE_ARCHIVE_2026-09-22.md`.

Conclusion: the duplicate refs in the first two groups add no distinct commit evidence. The unique4 checkpoint is now archived at the durable-document level. Branch-ref deletion can therefore be handled as a separate cleanup operation; no source evidence depends on retaining all duplicate names.


### 2026-09-22 cleanup execution

G350 official-source audit family: all 13 remote branch refs were deleted after durable evidence preservation in the historical archive.

G368 hypothesis-layer family: all 29 remote branch refs were deleted after durable evidence preservation in the historical archive.

No canonical Strategy A rule, P-Gap executable formula, AB=CD anchor/tolerance, fill semantics, or production execution rule was changed by this cleanup.

Next cleanup control: re-audit remaining remote branches, then review the G413 family as a separate lineage-control item before any deletion.
