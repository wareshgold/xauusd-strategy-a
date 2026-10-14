# Factory Work Snapshot — Timestamp Sequence Audit

Date: 2026-10-14

## Scope

This branch adds a standalone, read-only diagnostic for timestamped CSVs. It is research infrastructure only; it does not change Strategy A rules, data artifacts, the live Forward runner, Factory readiness, or production authority.

## Branch provenance

- Base branch: `research/xauusd-availability-integrity-gate-20261013`
- Base commit: `5fa9d60be98a5ad8e4b9b5075557bc53a7ddc877`
- Work branch: `research/factory-timestamp-sequence-audit-20261014`

## Added files

- `scripts/sp2l_timestamp_sequence_audit.py`
- `tests/test_sp2l_timestamp_sequence_audit.py`
- `research/FACTORY_TIMESTAMP_SEQUENCE_AUDIT_CONTRACT.md`

## Diagnostic semantics

- Fails closed on invalid/non-UTC timestamps, duplicate instants, backward timestamp transitions, missing CSV/column, and read errors.
- Reports forward gaps separately. A gap is not classified as a market closure, holiday, provider issue, or missing-history cause.
- Reports SHA-256 before/after and never sorts, deduplicates, repairs, or writes to the input.
- Reports `canonical=false`, `market_session_approval=NOT_ESTABLISHED`, and `source_artifacts_modified=false`.

## Important data limitation

The committed `data/mt5-session-availability/` artifact is a daily summary, not a raw M1 bar stream. Its daily first/last timestamps cannot prove per-bar timestamp uniqueness. Do not claim that duplicate raw timestamps have been checked until this utility is run against an identified raw bar CSV with a confirmed timestamp column and its provenance preserved.

## Validation status

Tests have been authored but have not yet been executed in the Factory worktree in this session. Do not mark this work validated until the user pulls the branch and runs the targeted test and full suite.

## Next step

From the Factory worktree, run the focused test, then the full suite. Locate the exact immutable raw M1 artifact and inspect its CSV header before running the audit. Preserve the complete JSON report as a separate evidence artifact; do not rewrite source data to make a failing audit pass.
