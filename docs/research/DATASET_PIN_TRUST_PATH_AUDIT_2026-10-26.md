# Dataset Pin Trust-Path Audit — 2026-10-26

## Scope and inspected path

This audit follows the current research-branch implementation from manifest construction through pin-ledger verification and comparison-gate consumption. It is a code-path audit only; it does not claim that a production or live holdout workflow has been authenticated.

1. `DatasetManifest.create(...)` computes a deterministic SHA-256 fingerprint from manifest fields. This establishes content consistency, not publisher identity.
2. `DatasetManifestPinLedger.append(manifest)` adds the manifest fingerprint to a hash-chained ledger. `to_json()` serializes it, but the module does not persist it to durable storage or publish an external attestation.
3. `DatasetManifestPinLedger.from_json(..., expected_external_tip_fingerprint=...)` verifies the chain and supplied expected tip. It does not fetch or authenticate the source of that expected tip.
4. `DatasetManifestRegistry(trusted_pins=...)` accepts a caller-provided mapping. The registry validates mapping format and manifest equality, but cannot independently establish that the mapping came from a trusted authority.
5. `evaluate_comparison_validation_gate(..., dataset_manifest_registry=...)` requires a registry for `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT`. The gate blocks these roles with `DATASET_PIN_TRUST_ROOT_UNAUTHENTICATED` whenever a registry is supplied, without trusting a caller-controlled boolean/property or duck-typed `validate_record` method.
6. The parallel `evaluate_dataset_provenance(...)` path previously returned `PASS` for matching local registry hashes even when the declared role was validation/holdout. It now returns `BLOCKED` with `DATASET_EXTERNAL_TRUST_UNAUTHENTICATED` for matching `UNTOUCHED_VALIDATION`/`FRESH_HOLDOUT` datasets; actual identity/content mismatches remain `FAIL`.
7. `ResearchRecord.validate()` previously accepted a caller-constructed `ResearchProvenanceResult(PASS, ...)` for validation/holdout roles. It now rejects such records until an authenticated external trust provider is implemented. This prevents a manually claimed `PASS` from being serialized into the research-record ledger.

## Findings

- Integrity checks and chain verification are implemented.
- Pin authenticity, publisher identity, durable independent storage, and verifier/publisher permission separation are not implemented by this path.
- The comparison gate now fails closed for validation/holdout roles even if a caller supplies an object claiming `has_authenticated_external_trust_root = True`; it does not call that object's `validate_record` method. This closes the property/duck-typing bypass as well as the mapping-only false-trust path; it does not create or authenticate an external trust root.
- Dataset provenance and research-record construction now also fail closed for matching validation/holdout hashes when there is no independently authenticated trust provider. Local integrity checks still run first so observed content or identity contradictions remain visible as `FAIL`.
- A caller-generated digest, environment variable, label, or pin stored next to the ledger is not sufficient evidence of an independent trust root.
- The inspected code and synthetic tests do not demonstrate that a real holdout has been independently frozen or authenticated.

## Fail-closed disposition

Until an independently controlled trust source is selected and its identity/signature is verified by the surrounding workflow, both dataset-provenance evaluation and the comparison gate block `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT` even when local hashes match; research records for those roles cannot be accepted as `PASS`. The prerequisite remains unresolved; no holdout may be described as independently authenticated.

## Required decision and implementation criteria

A follow-up implementation requires a concrete trust-source decision before coding. Acceptable design candidates include a signed attestation with a verified issuer/signing identity or a separately administered immutable registry. The chosen contract must bind the attestation to the exact manifest revision, dataset ID/fingerprint, ledger tip, and record count as applicable; define key/identity rotation and revocation behavior; and record source identity, payload digest, verification result, and verification time.

Adversarial tests must fail closed for missing/invalid signatures, wrong or untrusted identity, revoked identity, replayed attestation, manifest/revision mismatch, ledger-tip/count mismatch, and unavailable trust service. A plain expected-tip string is not an authenticated attestation.

## Scope exclusions

No canonical SP2L geometry, execution/fill semantics, BUY/SELL logic, statistical-edge claim, or production authorization is changed by this audit. No local worktree, MT5 session/account, Strategy A forward test, Strategy B run, merge, or deployment is part of this change.
