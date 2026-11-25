# SP2L Factory Fresh Holdout Prior-Use Call-Path Audit
Date: 2026-11-25

## Status

Read-only source audit completed against branch `research/synthetic-characterization-tests-20261125`, head `a06b2aee7f7415538d49387e4af40591952198fb`.

This document records observed implementation behavior only. It is not a Holdout policy decision, approval, or evidence that a real Fresh Holdout has been reused or contaminated.

## Scope and safety

Reviewed the in-memory Dataset Registry, Dataset Usage Ledger, Research Run Ledger, Research Job Runner, dataset provenance evaluator, and the Discovery, Stability, Robustness, Validation, Holdout, and Forward Gate paths.

No source implementation or tests were changed for this audit. No Factory runtime, market data, MT5 terminal, Runner, real Validation/Holdout dataset, or historical journal was accessed or executed.

## Findings

### 1. The prior-use helper exists, but its enforcement is not wired into the reviewed execution path

`DatasetRegistry.assert_no_holdout_reuse(dataset, content_fingerprint)` is defined in `src/strategy_factory/datasets.py` (lines 171-179).

Observed behavior:
- It scans records currently held in that Registry instance whose role is `UNTOUCHED_VALIDATION` or `FRESH_HOLDOUT`.
- It raises when the candidate has the same content SHA or composite dataset fingerprint as one of those records under a different `dataset_id`.
- It deliberately does not reject a match under the same `dataset_id`.

The method is not called from `DatasetRegistry.register` (lines 100-149), `DatasetRegistry.validate_spec` (lines 155-167), or the reviewed Factory/Runner orchestration paths below. The corresponding test in `tests/test_dataset_registry.py` calls the helper directly; that proves helper behavior, not automatic enforcement by a Factory path.

Consequently, this helper is not presently an end-to-end prior-use guard. Even if called, its current same-ID exception means it is not a one-time-consumption rule for a dataset identity.

### 2. Reviewed Factory paths register and bind datasets, but do not call the prior-use helper

Observed registration/execution paths:
- Discovery: `DiscoveryFactory.prepare_and_run` delegates dataset registration to `snapshot.register(self.runner.runs.registry, ...)` before creating the job and invoking the Runner (`src/strategy_factory/discovery_factory.py`, around lines 95-140).
- Stability: registers through `self.runner.runs.registry.register(...)` before invoking the Runner (`src/strategy_factory/stability_factory.py`, around lines 145-175).
- Robustness: registers through the same Registry method (`src/strategy_factory/robustness_factory.py`, around lines 120-145).
- Validation: registers through the same Registry method (`src/strategy_factory/validation_factory.py`, around lines 125-150).
- Holdout: registers through the same Registry method (`src/strategy_factory/holdout_factory.py`, around lines 150-180).
- Forward Gate: consumes the supplied Holdout result, verifies run/record/provenance/handoff identity, validates the supplied event-ledger snapshot, and requires exactly one matching Holdout completion for that job. It also requires the Forward dataset ID, SHA, and artifact ID to differ from the Holdout identity (`src/strategy_factory/forward_gate_factory.py`, around lines 140-245). This is job/event and Holdout-to-Forward binding; it does not query prior Holdout consumption across research runs.

No reviewed call site invokes `assert_no_holdout_reuse`.

### 3. The Runner's provenance gate verifies the registered identity, not historical prior use

`ResearchJobRunner.run`:
1. checks the job fingerprint against the supplied dataset/spec;
2. calls `evaluate_dataset_provenance`;
3. creates a research run through `ResearchRunLedger.create`;
4. then invokes the adapter.

See `src/strategy_factory/runner.py`, around lines 175-285.

`evaluate_dataset_provenance` compares the current spec and observed SHA/artifact with the identity already registered for that `dataset_id`. It does not enumerate prior usages or call `assert_no_holdout_reuse` (`src/strategy_factory/dataset_provenance.py`, lines 43-122).

### 4. Dataset Usage records consumption but does not reject repeated Holdout use

`DatasetUsageLedger.record` validates the registered identity, observed fingerprint, optional artifact, and a limited Purpose blocklist. It appends an `ALLOWED` usage entry; there is no lookup that rejects a prior usage of the same Fresh Holdout identity (`src/strategy_factory/usage.py`, around lines 51-100).

For Validation/Holdout roles, the current blocklist rejects `DEVELOPMENT`, `OPTIMIZATION`, and `PARAMETER_FIT`. It is not an exhaustive stage-specific Purpose allowlist. The synthetic characterization test added in PR #433 demonstrates that an unrecognized non-empty Purpose string is currently accepted; that acceptance is not Purpose approval (`tests/test_dataset_usage.py`, around lines 120-137).

### 5. Registry, Usage, and Run ledgers are in-memory; Runner duplicate protection is instance-local

- `DatasetRegistry` explicitly documents that persistence is deferred and stores records in in-memory dictionaries (`src/strategy_factory/datasets.py`, lines 89-100).
- `DatasetUsageLedger` stores entries in an in-memory list (`src/strategy_factory/usage.py`, lines 51-57).
- `ResearchRunLedger` stores run records in an in-memory dictionary (`src/strategy_factory/runs.py`, lines 77-83).
- `ResearchJobRunner` tracks completed job IDs in an instance-local set. Its docstring explicitly permits a fresh Runner to replay the same immutable job (`src/strategy_factory/runner.py`, lines 175-205).

These structures do not establish durable, cross-process prior-use history.

## Current enforcement boundary (code-observed)

| Concern | Observed behavior |
|---|---|
| Exact registered dataset/spec identity | Checked by Registry/provenance/usage path |
| Observed bytes and registered artifact binding | Checked by Factory and Runner/provenance path |
| Same-content Fresh Holdout under a different dataset ID | Helper exists, but no reviewed automatic call site |
| Repeated consumption under the same dataset ID | No prior-use rejection found in the reviewed path |
| Prior use across independent processes/restarts | Not established by in-memory ledgers |
| Holdout-to-Forward identity separation | Checked by Forward Gate |
| Exactly one matching Holdout completion for a job | Checked against supplied event-ledger snapshot |
| Exhaustive stage-specific Purpose authorization | Not implemented by current blocklist |

## What this audit does not establish

- It does not prove that any actual Holdout was reused.
- It does not prove that all possible application entry points outside the reviewed Factory package have been exhaustively enumerated.
- It does not define what the policy owner intends “prior use” or “reuse” to mean.
- It does not establish temporal independence, interval overlap rules, timezone semantics, derived-data lineage rules, or cross-run persistence requirements.
- It does not approve any Purpose label, route, freeze authority, or Holdout lifecycle.

## Unresolved policy-owner decisions (do not infer)

Before enforcement tests or implementation are designed, the policy owner must explicitly decide:
1. Whether Fresh Holdout is single-use, or whether any defined repeated use is permitted.
2. Which identity dimensions constitute reuse: content SHA, artifact ID, dataset ID, composite fingerprint, time interval, derived data, or a declared combination.
3. Whether same-`dataset_id` repeat use is prohibited, and whether retry/recovery is distinct from a new research use.
4. Which durable record is authoritative across process restarts and how incomplete/failed runs affect prior-use state.
5. Whether and how Validation prior-use should share the same mechanism as Fresh Holdout.

Until those decisions are made, no prior-use policy tests, allowlists, new guard calls, or lifecycle semantics should be added on assumption.

## CI context

On commit `a06b2aee7f7415538d49387e4af40591952198fb`, the four associated PR-triggered workflow runs were reported completed with success:
- Factory Research Tests
- Factory Journal Lock Cross-Platform Tests
- SP2L forensic deterministic checks
- Full Repository Test Suite

CI success validates the associated checks; it does not resolve the policy questions above.
