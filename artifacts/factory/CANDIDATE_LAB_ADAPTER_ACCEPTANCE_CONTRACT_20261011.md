# Candidate Lab — Adapter Acceptance Contract

Date: 2026-10-11
Status: **Specification only — adapter implementation not yet approved**

## Purpose and boundary

Define the review gate for a future Candidate Lab adapter that consumes the exact verified dataset snapshot supplied by `run_candidate_matrix` and returns a provenance-bound `CandidateObservation`.

This document does not implement an adapter, define an input data schema, infer Strategy A geometry, resolve source ambiguities, choose execution/fill semantics, or establish a statistical edge. Those decisions require separately reviewed evidence. The generic `ExecutionAdapter` in `src/strategy_factory/adapter.py` is not, by itself, the Candidate Lab bytes-to-observation adapter described here.

## Required callable interface

The current Candidate Lab runner calls the adapter with:

```python
adapter(candidate: ResearchCandidate, dataset_snapshot: bytes) -> CandidateObservation
```

The adapter must treat `dataset_snapshot` as the sole dataset input for that run. It must not reopen the artifact path, fetch replacement data, read a mutable external dataset, or silently substitute another dataset. The runner independently checks the artifact's SHA-256 before and after adapter calls; the adapter must additionally prove through its implementation and tests that parsing/execution consumes the provided snapshot.

## Preconditions

Before an adapter is approved for any real historical run, reviewers must be able to verify all of the following:

1. **Input schema is explicit and reviewed.** A versioned dataset schema and parser contract must be supplied separately. No column names, timezone, candle ordering, missing-bar policy, duplicate handling, or price-field semantics may be guessed.
2. **Data integrity is fail-closed.** Invalid encoding, malformed records, unsupported schema versions, invalid numeric values, non-finite values, duplicate/out-of-order timestamps, or any other schema-defined violation must raise a typed error; no silent row dropping or coercion.
3. **Time and units are explicit.** Timestamp timezone, timestamp precision, price units, symbol/instrument identity, and any required volume/metadata meanings must come from the reviewed dataset contract, not adapter assumptions.
4. **Execution semantics are explicit.** Entry, fill, intrabar ordering, spread, commission, slippage, stop/target collision handling, and other execution assumptions must be represented by a reviewed `ExecutionSemantics` / execution fingerprint. Unknown semantics block execution rather than receiving defaults.
5. **Research boundary is enforced.** Only immutable `DEVELOPMENT` data is eligible for candidate optimization. Untouched Validation, Fresh Holdout, and Forward datasets must be rejected.
6. **No geometry is invented.** The adapter may only evaluate already approved, fingerprinted geometry/source-resolution rules. Unresolved source meanings must remain unresolved and block any dependent evaluation.

## Output acceptance rules

The adapter must return a valid `CandidateObservation` whose provenance and metrics are bound to the supplied candidate and plan. Acceptance requires:

- The exact candidate identity, candidate fingerprint, plan fingerprint, dataset SHA-256, execution fingerprint, geometry fingerprint, and source-resolution fingerprint are preserved without substitution.
- The output is complete and deterministic for the same immutable input bytes, candidate, and approved execution contract, subject only to explicitly documented deterministic engine/version identity.
- `trades`, `wins`, `losses`, and `ambiguous` are non-negative integers and `wins + losses + ambiguous == trades`.
- PnL and drawdown are finite; drawdown is non-negative; profit factor is either null for a documented mathematically undefined case or a finite non-negative value.
- The result is net of all costs required by the approved execution contract, and `costs_included=True` is evidence-backed rather than a caller-supplied assertion.
- The deterministic result fingerprint matches the exact candidate identity and returned metrics as enforced by Candidate Lab validation.
- Any incomplete run, adapter exception, unsupported condition, or provenance mismatch fails closed; it must not emit a successful observation or silently omit a candidate.

The current result fingerprint detects stale fingerprints when bound metrics change. It is an integrity check, not a digital signature and not proof that the underlying execution or cost model is correct.

## Required tests before approval

The adapter-specific test suite must include at least:

1. Known synthetic fixture with independently hand-checked expected output.
2. Identical-input repeatability test for metrics and fingerprints.
3. Proof that parsing consumes the passed `bytes` snapshot, with filesystem/network access unavailable or instrumented to fail during adapter execution.
4. Dataset byte mutation / wrong dataset identity rejection.
5. Malformed, truncated, unsupported-version, invalid-numeric, and schema-violation rejection according to the reviewed schema.
6. Candidate, plan, dataset, execution, geometry, and source-resolution provenance mismatch rejection.
7. Missing-cost or unsupported-cost-model rejection.
8. Ambiguous/collision cases handled exactly as the approved execution contract specifies; unresolved behavior must block rather than be guessed.
9. No partial successful result after exceptions or interrupted execution.
10. Regression test proving the adapter cannot read or optimize against Validation, Fresh Holdout, or Forward data.

Synthetic fixtures validate software behavior only; they are not XAUUSD performance evidence.

## Review artifacts required

Before implementation is accepted for a real historical run, attach or reference:

- Versioned dataset schema and parser specification.
- Source-resolution and frozen-geometry approvals, including fingerprints and a list of unresolved items.
- Explicit execution-semantics and cost-model specification.
- Adapter design/code review recording how the provided byte snapshot is consumed.
- Adapter-specific test report and whole-suite test report.
- A reproducible run manifest binding code revision, adapter/engine revision, plan fingerprint, dataset content SHA-256, execution fingerprint, geometry fingerprint, source-resolution fingerprint, and result fingerprints.

## Non-goals and stop conditions

- No production BUY/SELL authority.
- No automatic canonical-winner selection.
- No optimization against Untouched Validation, Fresh Holdout, or Forward data.
- No use of synthetic results as trading-performance evidence.
- No change to the Forward Runner, MT5 runtime, Holdout artifacts, or canonical Strategy A geometry as part of this contract.
- If required source rules, schema meaning, or execution semantics remain unresolved, stop at the relevant gate and record the blocker; do not fill gaps with plausible assumptions.

## Current status

Candidate Lab's dataset identity and result fingerprint guards have unit-test coverage. The real historical adapter described here is **not implemented or approved**. Passing Candidate Lab tests alone does not authorize a real historical research run.
