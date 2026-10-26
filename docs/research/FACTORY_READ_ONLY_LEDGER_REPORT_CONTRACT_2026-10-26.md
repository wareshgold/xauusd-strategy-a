# Factory Read-only Ledger Report Contract — 2026-10-26

## Purpose

`src/strategy_factory/ledger_report.py` builds a deterministic read-only summary from a complete ordered sequence of ledger records. It first validates the hash chain against both a separately supplied expected tip SHA-256 and expected record count. Both pins must come from outside the ledger being checked; deriving the expected values from the same supplied records would not detect truncation.

## Report fields

- Record count and verified tip.
- Counts by experiment status and evidence status.
- IDs of PLANNED, FAIL, INCONCLUSIVE, and BLOCKED records.
- All counterexample references in ledger order.
- IDs with incomplete/missing evidence, source-review-required evidence, or contradicted evidence.

## Fail-closed behavior and limits

- Broken hashes, reordered/gapped records, duplicate IDs, incorrect tip, or incorrect count raise an error instead of returning a successful report.
- The report is read-only and deterministic; it does not rewrite records or promote statuses.
- `canonical_authorized` and `production_decision_authorized` remain false.
- It does not authenticate the external pin source or execution artifacts. Pin values must be managed independently and captured output bytes must be retained.
- Counts summarize the supplied ledger; they are not statistical performance results and do not prove source meaning, broker behavior, canonical SP2L geometry, or a trading edge.
