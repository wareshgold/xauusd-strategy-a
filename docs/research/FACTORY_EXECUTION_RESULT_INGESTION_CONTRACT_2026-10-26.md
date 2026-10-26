# Factory Execution Result Ingestion Contract — 2026-10-26

## Purpose

`execution_result_ingestion.py` accepts an explicitly supplied captured execution report and appends a hash-chained result record to a prior `PLANNED` record. It does not execute tests, fetch CI artifacts, inspect the process that produced them, or independently authenticate the report.

## Required captured fields

- Non-empty run ID and command.
- Integer exit code (zero maps to `PASS`; nonzero maps to `FAIL`).
- SHA-256 hashes of captured output and environment description.
- At least one non-empty evidence/artifact reference.
- Non-empty result summary.
- The exact prior plan record and its hash as the preceding chain record.

The output hash, environment hash, command, run ID, exit code, plan ID, evidence references, and counterexample references are included in the record hash. Missing evidence fails closed. The caller must preserve the referenced artifact bytes and independently compute the hashes.

## Scope limits

- A record means the caller supplied metadata claiming an execution occurred; the ingestion function cannot prove that claim by itself.
- The simple exit-code mapping is only for a captured test process. It is not a trading result, statistical validation, or source review.
- `PASS` is limited to the supplied run/fixture. It does not establish source meaning, broker behavior, canonical SP2L geometry, or an edge.
- `FAIL` and its counterexamples remain immutable and must not be overwritten by later runs.
- Canonical and production authorization remain hard-false.
- No historical replay, live runner, MT5, Strategy A forward test, or Strategy B run is invoked.
