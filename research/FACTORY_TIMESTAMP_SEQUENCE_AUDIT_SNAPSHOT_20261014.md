# Factory Work Snapshot — Timestamp Sequence Audit

Date: 2026-10-14

## Scope

This branch adds a standalone, read-only diagnostic for timestamped CSVs. It is research infrastructure only; it does not change Strategy A rules, data artifacts, the live Forward runner, Factory readiness, or production authority.

## Branch provenance

- Base branch: `research/xauusd-availability-integrity-gate-20261013`
- Base commit at branch creation: `0a03411d648f3bceb178410cd4a792c9a3c89087`
- Work branch: `research/factory-timestamp-sequence-audit-20261014`
- Latest code/snapshot commit: updated after local test validation

## Added files

- `scripts/sp2l_timestamp_sequence_audit.py`
- `tests/test_sp2l_timestamp_sequence_audit.py`
- `research/FACTORY_TIMESTAMP_SEQUENCE_AUDIT_CONTRACT.md`

## Diagnostic semantics

- Fails closed on invalid/non-UTC timestamps, duplicate instants, backward timestamp transitions, missing CSV/column, and read errors.
- Rejects non-finite or non-positive expected intervals.
- Reports forward gaps separately. A gap is not classified as a market closure, holiday, provider issue, or missing-history cause.
- Reports SHA-256 before/after and never sorts, deduplicates, repairs, or writes to the input.
- Reports `canonical=false`, `market_session_approval=NOT_ESTABLISHED`, and `source_artifacts_modified=false`.

## Validation evidence

Validated by the user in isolated worktree `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-timestamp-audit-20261014`:

- Focused tests: **14 passed in 0.46s**
- Full Factory suite: **830 passed in 13.37s**
- Test run commit: `6b1f2bc1afcf3e531a35cecd8cba47a082e8b56e`
- `PYTHONPATH` included the branch's `scripts` and `src` directories.
- No tests failed. This is local test evidence, not a claim that GitHub CI ran.

## Important data limitation

The committed `data/mt5-session-availability/` artifact is a daily summary, not a raw M1 bar stream. Its daily first/last timestamps cannot prove per-bar timestamp uniqueness. No claim is made that the real raw M1 dataset has been checked or that duplicates have been found.

## Next step

Locate the exact immutable raw M1 artifact and inspect its CSV header before running the audit. Preserve the complete JSON report as a separate evidence artifact; do not rewrite source data to make a failing audit pass.

## Governance

This utility is diagnostic only. It does not connect to MT5, alter Factory state, infer session closures, modify SP2L geometry, rank candidates, or authorize trading. A structural pass is not proof of historical completeness, canonical Strategy A rules, a statistical edge, or production eligibility.
