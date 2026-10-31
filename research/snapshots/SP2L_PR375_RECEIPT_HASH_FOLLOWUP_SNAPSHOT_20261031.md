# PR #375 Receipt Dataset Hash — Follow-up Snapshot

- Snapshot date: 2026-10-31
- Snapshot branch: `research/snapshot-pr375-receipt-hash-20261031`
- Follow-up to: `SP2L_PR375_RECEIPT_HASH_REVIEW_SNAPSHOT_20261031.md`
- Original reviewed PR head: `d2b6c15597e0b1ad720f1e8afbc80ada67724c0f`
- Corrected PR head: `e1fe34078b87b8e6d2a41eb38dfa8910c5206808`
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/375
- PR title: Factory: bind execution receipts to dataset content SHA-256
- PR head branch: `research/factory-receipt-dataset-hash-contract-20261031`
- PR base branch: `research/factory-candidate-lab-20261010`
- Base SHA: `a39877d4f3c04e71890792995ac82ef1b76e4823`

## Corrected implementation

- `DatasetProvenanceResult` exposes raw `registered_content_sha256` and `observed_content_sha256` separately from composite fingerprints.
- Standalone Acceptance and Research Provenance compare dataset-backed V2 receipt SHA-256 with both independent raw values.
- Mirrored null and mismatching digests fail at both standalone gates.
- Explicit null is restricted to exact built-in `SyntheticExecutionAdapter`, purpose `SYNTHETIC_INFRASTRUCTURE_TEST`, and DEVELOPMENT role. Subclasses/wrappers do not inherit this exception.
- Legacy V1 remains readable but is not dataset-verified; new Runner executions continue to reject V1.
- Runner fail-closed checks remain in place.
- No Strategy A geometry, canonical SP2L rules, production decision capability, or BUY/SELL generation changed.

## CI evidence at corrected head

| Workflow | Run ID | Result |
|---|---:|---|
| Factory Research Tests | 41195484996 | PASS — 159 passed in 1.93s |
| SP2L forensic deterministic checks | 41195484997 | PASS |
| Factory Journal Lock Cross-Platform Tests | 41195485002 | PASS — Ubuntu and Windows |

An intermediate CI run identified two Validation Factory fixture failures after the stricter standalone Provenance contract was introduced. The fixtures were updated to pass adapter/purpose context; all three workflows passed at the corrected head.

## Exact PR state at follow-up capture

- PR state: OPEN
- Draft: false (Ready for review)
- Merged: false
- Mergeable: true
- Commits: 63
- Changed files: 30
- Additions/deletions: +1057 / -113
- Full repository test suite: not run
- Independent human approval: none recorded
- Formal self-authored REQUEST_CHANGES review: unavailable because the connected GitHub identity is the PR author.

## Decision and limits

The identified standalone-gate dataset identity gap is corrected in code and covered by focused tests/CI. This is not merge approval. Human review and explicit user authorization remain required before merge.

This snapshot does not establish statistical edge, canonical SP2L geometry, untouched validation, Fresh Holdout completion, or production readiness.


## Final follow-up verification — corrected run-purpose binding

A final trust-boundary review identified that a caller-supplied synthetic purpose also needed to match the immutable `ResearchRunIdentity.purpose`. The shared Acceptance/Provenance policy now enforces this binding; a synthetic adapter cannot obtain the null exception merely by passing a purpose string that differs from the registered run. A dedicated negative Acceptance test covers this case.

- Final PR head: `9f02552d30e4869c47daac0e59060b82c6d6348a`
- Factory Research Tests: **PASS — 160 passed in 1.82s** (run 41195675387)
- SP2L forensic deterministic checks: **PASS** (run 41195675404)
- Factory Journal Lock Cross-Platform Tests: **PASS — Ubuntu + Windows** (run 41195675419)
- Final PR state: OPEN, Ready for review, mergeable, not merged
- Final PR size: 66 commits, 30 changed files, +1083/-115
- Full repository suite remains unrun; independent human approval remains outstanding.

This final verification supersedes the earlier `e1fe340...` / 159-test values above.
