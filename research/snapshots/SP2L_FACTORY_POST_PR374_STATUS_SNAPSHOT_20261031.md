# SP2L Factory Status Snapshot — Post PR #374 Closure

- Snapshot date: 2026-10-31
- Snapshot branch: `research/snapshot-factory-post-pr374-20261031`
- Snapshot base: `research/factory-candidate-lab-20261010`
- Base commit SHA: `83939ec42e76ed362f510f974af88a3b0da2f630`
- Scope: Strategy A Factory / SP2L research infrastructure only.
- Nature: immutable status checkpoint; this branch is separate from the active Factory branch and is not a promotion or merge.

## 1. Actions completed in this checkpoint

### PR #374 closed, not merged
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/374
- State: CLOSED; merged=false; closed at 2026-10-31T11:49:25Z.
- Head at closure: `91158d626635ecfe77b864201ef985e72b7c4c48`.
- A conversation comment records the rationale: superseded by merged PR #375; binding `input_fingerprint` to raw Dataset SHA conflicts with Design B.
- No code from #374 was merged.
- Correct contract: preserve `input_fingerprint` as the adapter's existing identity (which may be composite); use independent `dataset_content_sha256` for exact raw dataset identity.

### PR #375 — receipt dataset hash contract
- Merged into Factory branch through merge commit `d8190b03599ed108607bcaa69cd6425999d2850b`.
- Schema v1 remains readable but not dataset-verified.
- Schema v2 carries independent `dataset_content_sha256`.
- Dataset-backed receipts are checked against registered and observed raw content digests in Acceptance and Research Provenance.
- Exact synthetic adapter exception remains narrowly scoped to infrastructure tests; no Strategy A geometry or production authority was added.

### PR #376 — full repository test workflow
- Merged through `83939ec42e76ed362f510f974af88a3b0da2f630`.
- Full Repository Test Suite: 821 passed.
- All four workflows on the merge commit succeeded:
  - Full Repository Test Suite — run 41197939501
  - Factory Research Tests — run 41197939576
  - SP2L forensic deterministic checks — run 41197939557
  - Factory Journal Lock Cross-Platform Tests — run 41197939516

## 2. Active Factory branch baseline

- Branch: `research/factory-candidate-lab-20261010`
- Verified remote HEAD: `83939ec42e76ed362f510f974af88a3b0da2f630`
- Working-tree status: not inspected by this GitHub-only checkpoint; no claim is made about local uncommitted changes, untracked files, worktrees, or MT5 state.
- CI at this exact commit: 4/4 successful as listed above.

## 3. Relevant PR queue at snapshot time

| PR | State | Head | Relationship / disposition |
|---|---|---|---|
| #374 | CLOSED, unmerged | `91158d6` | Superseded by #375; do not reopen or merge as-is |
| #375 | MERGED | `9f02552d30e4869c47daac0e59060b82c6d6348a` | Receipt dataset hash contract integrated |
| #376 | MERGED | `4508542840009b32268a6c6849f44608906ddd1e` | Full repository CI integrated |
| #365 | OPEN, Draft | `90401a47c4f89ca6a313117c297e326596ce8f9d` | 50 commits ahead / 72 behind current Factory base; keep Draft and unmerged per its DEVELOPMENT-only registration proposal |
| #368 | OPEN, Draft | `80da727e7c21944968a3d59091b15fb3c971f20e` | 186 ahead / 72 behind current Factory base; audit independently before any update/merge; cannot authorize Fresh Holdout while source/geometry remain unresolved |
| #353 | OPEN, Draft | `9d6ee131075101179c2b45cb4fd78ac0491b5c2f` | 119 commits; stale base; separate tick-gate/synthetic-fixture proposal requiring dependency and scope reconciliation |
| #352 | OPEN, Draft | `ffb22153cfe2a04d10e547101971116d0333315d` | One-file journal-quarantine documentation; stale base; review separately |
| #337 | OPEN, Draft | `9dd199eb1fa32ac39e1d24aa15c8a0c913963e1c` | 21 commits; stale base; read-only tick audit work, reconcile with #365 before action |

PR #365 and #368 each diverge from the current Factory base at merge-base `a39877d4f3c04e71890792995ac82ef1b76e4823`. The current base has advanced 72 commits since that merge base. Do not blindly update, rebase, or merge these branches.

Strategy V4 PRs #370/#372/#373 are a separate workstream and are intentionally outside this Strategy A Factory snapshot.

## 4. Dataset and source constraints

- DEVELOPMENT tick artifact previously audited:
  - File SHA-256: `412a535b8d5f0413f329e5fde8a1f851591ee83c95fc25af38b287d6170a1347`
  - Size: 111,124,585 bytes
  - Rows: 10,817,858
  - Coverage: 2026-08-21 01:00:05.864Z through 2026-09-18 23:57:56.609Z
  - Acquisition/manifest provenance remains unanchored; do not treat a matching file hash as proof of acquisition provenance.
- Existing audit observations include duplicate timestamps and long gaps; duplicates must be preserved and gaps must not be calendar-interpreted without a source-backed session calendar.
- PR #365 is a fixed-scope DEVELOPMENT audit proposal only. It does not authorize performance backtests, Fresh Holdout, canonical geometry, execution/fill semantics, or production.
- Source Resolution remains unresolved/skipped by the current project decision. No source-confirmed P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules may be inferred.

## 5. Workflow progress and gate state

| Workflow stage | Status | Evidence / blocker |
|---|---|---|
| SOURCE RESOLUTION | BLOCKED / NOT COMPLETE | Source geometry and execution semantics are not confirmed |
| SYNTHETIC FIXTURES | PARTIAL | Receipt schema and provenance contract tests exist; strategy-geometry fixtures cannot be frozen before source resolution |
| FROZEN GEOMETRY | NOT STARTED | Must not invent or freeze unresolved geometry |
| DEV | BLOCKED FOR STRATEGY PERFORMANCE | Infrastructure/CI is green; no source-authorized strategy replay basis yet |
| UNTOUCHED VALIDATION | NOT STARTED | No frozen candidate/ruleset to validate |
| ROBUSTNESS / STABILITY | NOT STARTED | Requires frozen development result and protocol |
| FRESH HOLDOUT | BLOCKED | Source gate and frozen geometry are not PASS; no holdout access/registration |
| PRODUCTION | NOT AUTHORIZED | No validated statistical edge or production eligibility |

No single overall completion percentage is asserted: the stages are gated and are not interchangeable. Infrastructure/CI readiness has advanced materially, but strategy research readiness is still blocked upstream.

## 6. Next route

1. Preserve the current green Factory baseline and this snapshot.
2. Read-only audit the current #368 diff against the merged base; verify it fails closed and cannot self-assert source PASS, frozen geometry, or canonical eligibility. Keep Draft.
3. Reconcile #365 with #337 and its explicit DEVELOPMENT-only proposal. Keep #365 Draft/unmerged; do not register the dataset as validation or holdout.
4. Review #353 and #352 only after their dependency and stale-base relationships are understood; do not bulk-rebase or merge.
5. Resume SOURCE RESOLUTION only when authoritative source material is available. Record unresolved items explicitly.
6. Only after source confirmation: define synthetic fixtures from source-confirmed rules, freeze geometry, then proceed through DEV → untouched validation → robustness/stability → fresh holdout.
7. Production remains out of scope until a reproducible statistical edge is demonstrated and all governance gates pass.

## 7. Safety and non-claims

- This snapshot does not change Strategy A geometry, datasets, manifests, MT5 runners, order state, runtime journals, or trading configuration.
- No local worktree or local runtime was inspected or modified.
- No strategy performance backtest was run by this checkpoint.
- Green CI validates software tests, not trading edge, source correctness, Fresh Holdout eligibility, or production readiness.
- No BUY/SELL production decisions are generated or authorized.
