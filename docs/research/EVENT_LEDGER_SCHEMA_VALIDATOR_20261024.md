# Event ledger schema validator (2026-10-24)

**Research-only structural validation. This is not a trade execution validator.**

Script: `scripts/validate_sp2l_event_ledger_readonly.py`

Tests: `tests/test_validate_sp2l_event_ledger_readonly.py`

## What it checks

- Every JSONL record is a JSON object and contains the proposed event envelope keys.
- Identity fields and event/evidence labels use the expected types/vocabulary.
- `event_id` is unique within a `run_id`.
- Optional SHA-256 fields are either null or exactly 64 hexadecimal characters.
- A populated `event_time_utc` parses as timezone-aware UTC, retains an original timestamp, and names a timezone-evidence basis.
- A missing/unresolved UTC conversion is allowed when `event_time_utc` is null; the validator does not invent a mapping.
- Warnings/notes have the expected shape, and malformed JSONL is reported.
- The raw input bytes are SHA-256 hashed before parsing. Optional reports refuse to overwrite existing output paths.

## What it does not check

It does not prove that source events happened, that timestamps are correct, that a fill or exit occurred, that two events are causally ordered, that Strategy B and RR2/TRAIL4 are equivalent, or that any strategy is profitable. A structurally valid event can still contain incorrect or incomplete source information. Source-row/artifact references and evidence review remain necessary.

## Run locally against an existing copy

```powershell
python scripts/validate_sp2l_event_ledger_readonly.py --input .\path\to\existing-events.jsonl
```

The input is read-only. Do not point the command at a live output that is actively being written if a stable snapshot is not available. For a report, choose a new output filename that does not already exist:

```powershell
python scripts/validate_sp2l_event_ledger_readonly.py --input .\path\to\snapshot.jsonl --output .\artifacts\event-ledger-validation-new.json
```

The script exits with status 0 for structurally valid records and 1 for validation errors. This validator is an instrumentation gate only; historical paired comparison remains blocked by unresolved timestamp mapping, fill/exit evidence, trailing order, overlap, and common cost accounting.
