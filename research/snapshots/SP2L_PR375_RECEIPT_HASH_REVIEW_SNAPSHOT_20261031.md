# PR #375 Receipt Dataset Hash — Review Snapshot

- Snapshot date: 2026-10-31
- Snapshot branch: `research/snapshot-pr375-receipt-hash-20261031`
- Snapshot parent / reviewed PR head: `d2b6c15597e0b1ad720f1e8afbc80ada67724c0f`
- PR: https://github.com/wareshgold/xauusd-strategy-a/pull/375
- PR title: Factory: bind execution receipts to dataset content SHA-256
- PR head branch: `research/factory-receipt-dataset-hash-contract-20261031`
- PR base branch: `research/factory-candidate-lab-20261010`
- Base SHA: `a39877d4f3c04e71890792995ac82ef1b76e4823`

## Exact GitHub state at capture

- PR state: OPEN
- Draft: false (Ready for review)
- Merged: false
- Mergeable: true
- Compare: 54 commits ahead, 0 behind; merge base equals the recorded base SHA
- Changed files: 26
- Reviews: none
- Inline review threads: none
- Conversation comments: none

## CI evidence at reviewed HEAD

All three workflows associated with `d2b6c15597e0b1ad720f1e8afbc80ada67724c0f` completed successfully:

| Workflow | Run ID | Result |
|---|---:|---|
| Factory Journal Lock Cross-Platform Tests | 41193894218 | success |
| Factory Research Tests | 41193894312 | success |
| SP2L forensic deterministic checks | 41193894221 | success |

Factory Research Tests reported 153 passed in 1.90s. Journal Lock tests passed on Ubuntu and Windows.

## Scope and approved contract

Implements approved design B:
- Preserve historical `input_fingerprint` semantics.
- Add independent `dataset_content_sha256`.
- Keep legacy v1 receipts readable but not dataset-verified.
- Require v2 dataset-backed receipts to carry the actual artifact SHA-256.
- Allow explicit null only for the exact built-in synthetic infrastructure adapter under `SYNTHETIC_INFRASTRUCTURE_TEST` on DEVELOPMENT datasets.
- Bind receipt schema and dataset digest into evidence, acceptance, and research provenance.
- Do not add a standalone `execution_identity` field.

No Strategy A geometry, canonical SP2L rules, datasets, runtime journals, MT5 runner behavior, or production BUY/SELL capability is changed.

## Validation limitations / review gate

- The entire repository test suite was not run; the focused Factory tests and listed CI workflows passed.
- No independent human review is recorded as of this snapshot.
- PR is ready for review, but is not approved or merged.
- Do not merge until the user has reviewed the change and explicitly authorizes merge.

## Follow-up

Human review should focus on:
1. Exact-type synthetic trust boundary and DEVELOPMENT-only restriction.
2. Legacy v1 readability and fail-closed behavior for new dataset-verified runs.
3. V2 evidence summary revision and acceptance/provenance compatibility.

This snapshot records repository/PR/CI state only. It does not establish statistical edge, canonical SP2L geometry, untouched validation, Fresh Holdout completion, or production readiness.
