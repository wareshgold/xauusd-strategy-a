# Branch Governance & Archive Plan — 2026-10-15

Status: **Phase 0 / read-only inventory initiated. No branches deleted, moved, merged, or retagged by this document.**

## Why this audit exists

The repository currently has a large number of long-lived and short-lived branches spanning Factory/Candidate Lab, backtest/research, source resolution, and Forward Test/RR2-TRAIL4. Branch names alone are not sufficient evidence to decide that a branch is safe to delete or that its work is present in another branch.

## Safety contract

Until the inventory is complete and reviewed:

- Do not bulk-delete branches.
- Do not force-move refs, rebase shared branches, or merge unrelated work to make the branch list shorter.
- Do not use a broad pull/merge as a substitute for local working-tree reconciliation.
- Do not overwrite or clean local modifications, event logs, snapshots, audit evidence, or untracked files.
- Do not treat the newest commit, best backtest score, or a branch's name as proof of canonical strategy validity.
- Keep Factory/Candidate Lab, Backtest/Validation, and Forward Test operationally isolated.
- Preserve the source-resolution → synthetic fixtures → frozen geometry → development → untouched validation → robustness/stability → fresh holdout → production gates.
- Forward-runner fixes must not silently alter strategy geometry, entry/order semantics, RR2/TRAIL4 parameters, or execution authority.

## Proposed work areas

1. **Factory / Candidate Lab** — candidate orchestration, acquisition integrity, worker lifecycle, immutable research evidence. Current known work branch: `research/factory-candidate-lab-20261010`. Newer Factory-specific audit/fix branches exist and require ancestry/content review before any consolidation.
2. **Backtest / Validation / Source Research** — source evidence, unresolved geometry, deterministic fixtures, dataset integrity, backtest reports and holdout controls. These must remain explicitly non-canonical until source gates permit promotion.
3. **Forward Test / RR2-TRAIL4** — runner lifecycle, pending-order safety, MT5 history reconciliation, Telegram notifications, dashboards, and append-only runtime evidence. Current local working trees are not represented by one known clean remote branch; local state must be inspected separately.
4. **Shared governance** — CI checks, manifest/provenance requirements, branch protection and auditable release decisions.

## Initial remote inventory observations (not yet a deletion list)

The GitHub branch search returned at least 300 branch names across three pages, with additional pagination still available. The names include:

- Operational and checkpoint branches: `main`, `checkpoint/*`, `dev/*`, `hardening/*`.
- Factory work: `research/factory-candidate-lab-20261010`, `feat/factory-raw-m1-audit-candidate-lab-20261015`, `feat/factory-raw-m1-integrity-audit-20261015`, `fix/factory-*`, and `research/factory-*`.
- Forward and lifecycle work: `fix/rr2-trail4-*`, `fix/forward-*`, `hardening/forward-*`, and `research/rr2-trail4-*`.
- Source/research work: many `research/sp2l-*`, `research/phase*`, and `research/g*` branches. These may contain unique forensic evidence and must not be deleted based on age or naming alone.
- The local branch `fix/rr2-trail4-pending-lifecycle-list-local-20261008` was previously observed in the user's Windows working tree but was not found as a remote branch. Treat it as local-only until rechecked; do not assume its work is disposable.

## Open pull requests observed during the initial pass

These appeared in the GitHub open-PR query and require status, head/base SHA, CI, and content review before any branch cleanup:

- #323 — Fix CRLF normalization byte escapes in raw M1 audit
- #287 — deterministic Factory candidate lab / tick Bid-Ask acquisition
- #315 — RR2/TRAIL4 session vs no-trailing research comparison
- #306 — Factory worker journal audit findings
- #302 — suppress stale MT5 lifecycle notifications
- #288 — restart-safe RR2/TRAIL4 pending expiry
- #297 — entry geometry research audit
- #293 — Forward market-data availability diagnostics
- #285 and #284 — pending lifecycle collection fixes
- #236, #263, #260, #261, #257, #256, #255, #254, #252, #251 — source-resolution and validation research PRs
- Other older PRs also appeared in the query; this list is not exhaustive. Re-query GitHub before making decisions.

Note: the query response can be stale or normalized; verify the live PR state and merge commit directly before relying on it.

## Required inventory schema

For each remote and local branch, record:

- Branch name and whether local/remote.
- Exact HEAD SHA and commit date.
- Upstream/tracking branch, if any.
- Ancestry relationship to the relevant area reference branch (ahead/behind counts and merge-base).
- Open PRs, PR state, base/head SHA, merge commit, and CI state.
- Files changed relative to the area reference; unique commits and unique evidence/artifacts.
- Area: Factory / Backtest-Research / Forward / Shared Infrastructure / Unknown.
- Proposed status: `KEEP_ACTIVE`, `FREEZE`, `ARCHIVE_CANDIDATE`, or `REVIEW_REQUIRED`.
- Rationale, recovery reference (tag or immutable commit SHA), and reviewer decision.

## Decision rules

- `KEEP_ACTIVE`: active work or required integration source.
- `FREEZE`: useful checkpoint or completed research whose evidence remains relevant.
- `ARCHIVE_CANDIDATE`: only after proving no unique commits, files, evidence, or open-PR dependency would be lost, and after creating/verifying a recovery reference.
- `REVIEW_REQUIRED`: ambiguous ancestry, local-only work, unmerged PR, unique evidence, runtime impact, or insufficient metadata.

## Next steps

1. Finish paginated remote branch enumeration and collect exact HEAD SHA for every branch.
2. Query all open PRs and map PR head branches to their base branches and merge state.
3. Inspect relevant local repositories/worktrees read-only, including dirty and untracked state, without changing files.
4. Build a CSV/Markdown inventory with one row per branch and evidence-backed classifications.
5. Present a proposed archive batch for approval. Only then archive/delete eligible remote refs in small, logged batches.
6. Keep this plan separate from actual archival actions; no archive action is authorized by the initial inventory alone.

## Initial status

- Governance plan created on an isolated documentation branch.
- No application code changed.
- No runner, dashboard, MT5 process, order, runtime state, or event log touched.
- No existing branch deleted, renamed, force-moved, or merged by this plan.
