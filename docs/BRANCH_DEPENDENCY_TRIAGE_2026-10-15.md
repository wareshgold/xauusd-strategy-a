# Branch Dependency Triage — 2026-10-15

This is a first-pass dependency analysis derived from the current open PR metadata. It is intentionally conservative. It is **not** a deletion authorization.

Companion inventory: `docs/GITHUB_BRANCH_INVENTORY_2026-10-15.md`.

## Findings that affect archive safety

1. **54 open PRs were returned by GitHub's open-PR endpoint.** Their head branches and base branches are recorded in the inventory. Any branch referenced as an open PR head or base must remain protected until that PR is resolved and dependent branches are reviewed.
2. **There are nested PR chains, not independent feature branches.** Closing or deleting a parent branch before rebasing/re-targeting dependent PRs could make reviews confusing or discard work.
3. **Factory has an explicit integration chain.** PR #287 proposes `research/factory-candidate-lab-20261010` against `research/sp2l-starnet-engine-integration-20261007`; PR #323 proposes a raw-M1 normalization fix against the Factory branch. The Factory branch is therefore not an archive candidate while these PRs are open.
4. **Forward lifecycle has a dependency chain.** PR #288 is based on `fix/rr2-trail4-pending-lifecycle-list-20261008`; PR #293 and PR #302 are based on the safe-lifecycle branch; PR #315 is based on the Telegram deal-time branch. Do not archive these parent branches before checking the exact commit ancestry and resolving the open PRs.
5. **Source-resolution work has long chains.** PRs #222, #223, #225, #226, #227, #228, #229, #230, #231, #232, #233 form a sequence of research heads/bases. PRs #254, #255, #256, #257 form another chain. They contain source-resolution and fixture work and must not be bulk-archived by date.
6. **Some PRs share the same head branch.** PRs #260 and #261 both point to `research/sp2l-pgap-synthetic-fixtures-2026-09-21` but have different base branches. This requires PR-level review; branch deletion would affect both.
7. **Remote branch inventory is not local state.** The user's Windows worktrees may have local-only branches, dirty files, and untracked evidence. The previously reported `fix/rr2-trail4-pending-lifecycle-list-local-20261008` branch must be inspected locally before any cleanup.

## Priority work areas

### Factory / Candidate Lab
- Keep the current Factory candidate branch and all open dependent PRs.
- First resolve the raw-M1 normalization PR and the worker journal audit PR dependency.
- Do not make Factory's candidate score a canonical strategy rule.
- Archive research branches only after proving that all unique data, audit artifacts, and candidate provenance are preserved.

### Backtest / Source Research / Validation
- Keep source-resolution and synthetic-fixture PR chains intact until the PR bases are consolidated or explicitly closed with a recorded reason.
- Treat source evidence, geometry fixtures, data split manifests, and holdout boundary tests as high-value artifacts even when the branch is old.
- Do not merge a branch solely because its backtest result is better.
- Preserve unresolved P-Gap, AB=CD anchors/tolerances, fill semantics, and execution rules as unresolved until authoritative source evidence resolves them.

### Forward Test / RR2-TRAIL4
- Keep pending lifecycle, history-query guard, Telegram reconciliation, clock-offset, market-data diagnostics, and dashboard fixes separate until commit ancestry and behavior are reviewed together.
- Do not alter RR2/TRAIL4 parameters or strategy/order semantics as part of branch cleanup.
- Do not restart PS1/PS2 or touch MT5 because of this inventory work.
- Do not overwrite event logs, snapshots, or untracked local evidence.

## Safe archive candidate criteria

A branch can be proposed as `ARCHIVE_CANDIDATE` only if:
- it is not an open PR head or required base;
- no active branch depends on its unique commits;
- comparison with the relevant area reference proves all required changes/evidence are present elsewhere;
- any unique evidence files have an immutable copy/reference;
- local working-tree state has been checked if the branch exists locally;
- recovery SHA/tag is recorded and verified.

## Next concrete pass

1. Fetch all open PR details, including exact base/head SHAs and statuses.
2. Build a parent→child graph from PR base/head branch references.
3. Query merged/closed PRs and mark remote branches whose changes are already represented on an approved reference.
4. Compare commit ancestry and file deltas for small candidate groups (do not use branch age alone).
5. Produce a shortlist of *proposed* archival candidates, with evidence and recovery SHA, for human review.
6. Only after approval, archive in small batches. Do not delete refs in the current triage pass.

## Actions performed in this pass

- Read-only remote branch enumeration: 329 branch refs across paginated GitHub API responses.
- Open PR metadata snapshot: 54 PRs.
- Wrote the inventory and this triage document on `chore/branch-governance-inventory-20261015`.
- No application code changed; no existing branch deleted/renamed/force-moved; no local files or running processes touched.
