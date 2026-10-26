# Factory Research Experiment Ledger Contract — 2026-10-26

## Purpose

The research ledger records experiment identity, hypothesis version, immutable input and code hashes, result status, evidence status, evidence references, counterexamples, and explicit links to prior failed/inconclusive/blocked runs. It is a provenance mechanism, not a detector, backtest engine, source interpreter, or production decision-maker.

## Integrity rules

- Records are immutable values with deterministic canonical JSON serialization and SHA-256 content hashes.
- Each record links to the previous record hash; sequence numbers are contiguous and record IDs unique.
- Inputs and code are bound by SHA-256, not by mutable filenames alone.
- Result summaries are required for failures and blocked runs as well as passes.
- Counterexample references and evidence references participate in the record hash.
- A retest can append a new PASS, but cannot rewrite an earlier FAIL. It must explicitly reference earlier non-success records when claiming to retest them.
- A caller should pin the expected record count and/or tip hash outside the ledger. Without an external anchor, a valid chain can be truncated and still look internally consistent.
- Canonical and production authorization fields are hard-false; attempts to set them are rejected.
- Evidence labels describe provenance scope only. `SYNTHETIC_ONLY`, `DATA_ONLY`, or a recorded source citation do not by themselves establish canonical geometry.

## Status vocabularies

Experiment status: `PLANNED`, `PASS`, `FAIL`, `INCONCLUSIVE`, `BLOCKED`.

Evidence status: `EVIDENCE_INCOMPLETE`, `SYNTHETIC_ONLY`, `DATA_ONLY`, `SOURCE_CITATION_RECORDED`, `SOURCE_REVIEW_REQUIRED`, `CONTRADICTED`.

## Limits

The ledger does not itself discover evidence, execute tests, guarantee that the referenced inputs still exist, or authenticate external sources. SHA-256 establishes byte identity only when the bytes are available and independently hashed. A source citation recorded is not equivalent to source interpretation approved by a human. No canonical SP2L geometry or BUY/SELL decision is produced.
