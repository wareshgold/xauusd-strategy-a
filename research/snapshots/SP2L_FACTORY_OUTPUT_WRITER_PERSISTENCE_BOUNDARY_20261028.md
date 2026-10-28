# SP2L Factory Snapshot — Output Writer and Persistence Boundary — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-OUTPUT-WRITER-PERSISTENCE-BOUNDARY-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Audited source revision: `965f42947364081b0e5d97cac50836bfec5ca60f`
- Scope: follow-up source audit of Factory execution return values, output-artifact identifiers, dataset artifact export, and durable persistence boundaries.
- Method: read-only inspection of repository source and synthetic tests; no local execution or runtime interaction.

## Source-traced execution path

1. `FactoryOrchestrator.run_next` calls an injected executor. If it returns a dictionary, the orchestrator extracts `output_artifact`, `detail`, and optionally `run_fingerprint`; if it returns a string, that string is treated as the artifact identifier.
2. The orchestrator then persists a `COMPLETED` journal event containing the identifier and optional research-run fingerprint. It does not open the returned identifier as a path, serialize the executor's result object, hash output bytes, or verify an artifact manifest before recording completion.
3. `ResearchJobRunner.run` constructs and returns a `ResearchJobRunResult` composed of in-memory run, receipt, evidence, snapshot, audit, provenance, record, and gate objects. Its ledgers are passed in as in-memory objects; the runner itself does not provide a generic durable output-artifact writer.
4. `scripts/run_sp2l_factory_discovery_mt5.py` serializes a result summary to standard output. This is observable output, not a persisted generic Factory result artifact.
5. The Discovery dataset path is different: `DiscoveryFactory` passes an explicit `artifact_path` to `MT5M1ArtifactExporter`, and the dataset snapshot exposes a content SHA-256. That is a dataset-input persistence path, not a general output-artifact receipt protocol for research results.
6. `FactoryWorker.complete` and worker telemetry retain the artifact identifier only. The worker status JSON is operational telemetry, not an immutable evidence registry.

## Conclusion

The audited generic Factory path has no source-confirmed contract that maps a research output-artifact ID to a durable path, immutable serialized result, expected byte digest, and restart-time verifier. A journaled `COMPLETED` event records the executor's declared outcome; it is not independent verification of external artifact bytes. Dataset hashing must not be generalized into an output-artifact rule without an approved contract.

## Safe operating boundary

- Keep the current restart recovery behavior fail-closed for interrupted jobs.
- Do not invent a result-file path, serialization format, digest field, or receipt semantics.
- Do not automatically promote/replay a job from artifact existence, an artifact ID, worker telemetry, or a non-lifecycle marker.
- If a durable output receipt is required, first obtain a source-approved contract defining artifact ownership, serialization, path/ID mapping, digest calculation, atomic publication, lifecycle ordering, restart verification, and manual-reconciliation behavior. Then add isolated synthetic fixtures and tests before integrating any implementation.
- Preserve current dataset exporter behavior; this audit makes no changes to it.

## Verification and exclusions

This is a source audit and documentation snapshot, not a claim of newly executed tests. The prior synthetic recovery-boundary tests remain the applicable observed evidence; no fresh CI result for this documentation commit is implied.

No local pull, merge, cleanup, or runtime file mutation was performed. No MT5 terminal, Strategy A/Strategy B forward runner, Strategy A geometry, production decision path, or trading configuration was touched. No statistical edge or production readiness is inferred.
