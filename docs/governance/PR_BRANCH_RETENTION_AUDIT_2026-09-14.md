# PR / Branch Retention Audit — 2026-09-14

## Purpose

Record a deterministic classification of the current research/development pull-request and branch surface before any cleanup action. This is repository governance only; it does not alter Strategy A geometry or validation gates.

## Governing rule

A branch is not deleted merely because it is inactive. Classification precedes cleanup.

Allowed classifications:

- `ACTIVE` — current workstream or checkpoint still in use.
- `PROTECTED SNAPSHOT` — immutable reference that must be retained.
- `MERGED` — historical branch whose work is already represented in the target branch.
- `CLOSED / DEAD` — no open PR and no open issue reference, with no documented retention reason.
- `DUPLICATE` — redundant branch/PR superseded by a newer equivalent checkpoint; retain the authoritative newer record until cleanup is explicitly executed.
- `HISTORICAL EVIDENCE` — retained because its source/research record is evidence even if no longer active.

## Current authoritative records

| Record | Classification | Reason / action |
|---|---|---|
| `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | `ACTIVE BASELINE` | Controlled baseline for current source-resolution work. Do not rewrite. |
| `dev/deterministic-engine-foundation-clean-2026-09-14` | `ACTIVE` | Current deterministic infrastructure branch; latest audited foundation head is `2ba192865a29cc6722ccc28097ffc4ec2af5e715`. |
| `dev/sp2l-deterministic-engine-foundation-2026-09-14` | `HISTORICAL EVIDENCE` | Superseded by the clean foundation branch; preserve until explicit cleanup because it documents the earlier foundation attempt. |
| `snapshot/replay-backtest-audit-2026-09-14` | `PROTECTED SNAPSHOT` | Official replay/backtest audit checkpoint; must not be deleted or modified. |
| PR #147 / `research/sp2l-source-resolution-stop-condition-2026-09-14` | `ACTIVE CHECKPOINT` | Current finite source-resolution stop condition. Keep open until a newer authoritative evidence checkpoint supersedes it. |
| PR #145 / `research/sp2l-source-resolution-batch-2026-09-14` | `HISTORICAL EVIDENCE` | Source-resolution batch documenting SL/refresh/F12-F15 conclusions. Superseded as current checkpoint by #147, but useful as research provenance. |
| PR #144 / `research/sp2l-entry-resolution-pass-2026-09-14` | `HISTORICAL EVIDENCE` | Documents P-Gap/Entry evidence boundary used by later consolidation. |
| PR #143 / `research/sp2l-source-resolution-priority-pass-2026-09-14` | `HISTORICAL EVIDENCE` | Defines the finite priority ordering used by later source-resolution work. |
| PR #142 / `research/sp2l-source-resolution-consolidation-2026-09-14` | `HISTORICAL EVIDENCE` | Consolidates F8-F15 source adjudication before the later stop-condition checkpoint. |
| PRs #131, #134-141 | `HISTORICAL EVIDENCE / SUPERSEDED` | Earlier source-resolution fixture and checkpoint records. They should not be treated as active workstreams. Cleanup may be considered only after provenance references are verified. |
| PRs #120-123 | `HISTORICAL EVIDENCE / SUPERSEDED` | Earlier G-series discrimination and source-closure records. Preserve as provenance until references are checked. |
| PRs #88, #90, #100, #103, #117 | `HISTORICAL EVIDENCE` | Material source-resolution evidence and prior closure records. Preserve. |

## Duplicate branch families observed

The branch inventory contains repeated suffix variants for earlier experiments, including:

- `research/entry-trigger-mechanics-dev-val-*`
- `research/entry-trigger-root-cause-*`
- `research/excursion-topology-*`
- `research/outcome-excursion-topology-*`
- `research/outcome-path-stop-stress-*`
- `research/outcome-stop-stress-*`
- `research/sp2l-entry-trigger-2x-resolution-v2-*`

These are **not automatically deleted** by this audit. Many point to identical commits or represent historical evidence. They require an explicit cleanup pass that checks open PR/issue references and retained evidence before deletion.

## Cleanup decision

No branch deletion is authorized by this document alone.

The immediate governance action is to stop treating superseded research branches as active development paths. Future cleanup should:

1. verify no open PR references the branch;
2. verify no open issue or documented evidence record requires it;
3. preserve protected snapshots and historical evidence;
4. classify exact duplicate branches pointing to the same commit;
5. delete only branches classified `CLOSED / DEAD` or explicitly approved `DUPLICATE` after provenance is retained elsewhere.

## Strategy boundary

This audit makes no Strategy A geometry canonical. It does not alter P-Gap, Entry, SL, pending refresh, trigger, 2X/TP, AB=CD, or bearish-mirror status. Frozen Geometry and all downstream validation/holdout/production gates remain locked.

## Next governance step

Run an exact branch-to-PR reference audit for the duplicate families above, then perform cleanup only on branches proven safe to remove. Keep PR #147 as the current source-resolution checkpoint unless genuinely new Tier-1/2 evidence supersedes it.
