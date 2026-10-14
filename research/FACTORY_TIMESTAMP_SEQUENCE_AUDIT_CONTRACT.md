# Factory — Timestamp Sequence Audit Contract

## Purpose

`scripts/sp2l_timestamp_sequence_audit.py` is a read-only structural diagnostic for an existing CSV containing timestamped observations. It validates UTC timestamp parsing, exact duplicate timestamps, and backward ordering. It reports forward time gaps separately.

## Invocation

From the repository root, point the audit at a **raw timestamped bar file**, not the daily availability summary:

```powershell
.\.venv\Scripts\python.exe scripts\sp2l_timestamp_sequence_audit.py <raw-bars.csv> --timestamp-column time --interval-minutes 1
$LASTEXITCODE
```

Replace `<raw-bars.csv>` and `time` with the actual input path and timestamp column from that dataset. Do not assume the column name without inspecting the CSV header.

## Interpretation and fail-closed behavior

- Duplicate timestamps, invalid/non-UTC timestamps, backward transitions, missing files, and missing timestamp columns fail the structural audit.
- Forward gaps are reported, not automatically failed. A gap may reflect a market schedule, acquisition limitation, provider behavior, or a data issue; this tool does not determine which.
- The report records the source SHA-256 and checks that the source hash is unchanged across the audit.
- The input file is never rewritten, sorted, deduplicated, or repaired.
- Examples are capped to ten records per category to keep output bounded.
- A structural pass is not proof of historical completeness, session approval, data-provider correctness, canonical Strategy A rules, backtest approval, or production eligibility.

The availability matrix currently committed under `data/mt5-session-availability/` is a daily summary, not a raw bar-by-bar timestamp stream. It cannot prove that every individual M1 timestamp is unique. Run this audit against a raw M1 CSV only when that exact artifact is available and its provenance is recorded.

## Governance

The report must preserve:

- `canonical: false`
- `market_session_approval: NOT_ESTABLISHED`
- `source_artifacts_modified: false`
- `research_interpretation: TIMESTAMP_STRUCTURE_ONLY_GAPS_UNCLASSIFIED`

This utility is standalone research diagnostics. It does not connect to MT5, alter Factory state, infer session closures, modify SP2L geometry, rank candidates, or authorize trading.
