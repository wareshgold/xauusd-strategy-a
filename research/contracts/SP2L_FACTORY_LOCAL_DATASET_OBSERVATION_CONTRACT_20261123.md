# Factory Local Dataset Observation Contract

**Status:** research engineering contract proposal implemented on branch `research/factory-dataset-observation-contract-20261123`.
**Scope:** local filesystem artifacts only. URI, stream, remote object-store, and network-backed readers are out of scope.

## Required behavior

For every non-synthetic dataset-backed job, the runner requires:

- a registered `DatasetArtifact`;
- an adapter exposing `dataset_artifact_path`;
- the adapter path and artifact location resolving to the same existing local file;
- an independently computed SHA-256 and byte size matching the caller-declared dataset identity and registered artifact before execution;
- the same SHA-256 and byte size after adapter execution;
- a Receipt v2 `dataset_content_sha256` matching the runner-observed digest.

Missing paths, non-files, path mismatches, digest mismatches, byte-size mismatches, or a file changed during execution fail closed.

The built-in Discovery adapter exposes its M1 bars artifact through `dataset_artifact_path`. The built-in Stability adapter already has a `dataset_artifact_path` field. Injected adapters used by Robustness and Validation must implement the same local-path contract.

## Synthetic exception

The exact built-in `SyntheticExecutionAdapter` remains restricted to `SYNTHETIC_INFRASTRUCTURE_TEST` on `DEVELOPMENT` datasets. Its Receipt v2 must carry `dataset_content_sha256 = null`. The synthetic E2E report names the fixture digest `synthetic_fixture_content_sha256`; it must not present that value as a real dataset observation.

## Trust boundary and limitations

The runner independently hashes the same resolved file immediately before and after adapter execution. This verifies the file identity at those observation points; it does **not** cryptographically attest that arbitrary in-process adapter code consumed those bytes. A malicious adapter can lie, read another source, or modify and restore a file between observations. Adapter implementations therefore remain a trusted-code boundary requiring source review and controlled execution.

The current contract intentionally supports local `Path` artifacts only. A future remote/stream contract requires an explicit reader/snapshot abstraction and must not be inferred from this implementation.

## Governance

This contract changes software provenance checks only. It does not define SP2L geometry, source meaning, fill semantics, execution rules, canonical strategy rules, statistical edge, Holdout eligibility, or production authority. It does not run MT5 or touch any forward runner.
