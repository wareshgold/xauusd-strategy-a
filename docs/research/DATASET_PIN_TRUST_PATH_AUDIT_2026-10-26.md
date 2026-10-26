# Dataset Pin Trust-Path Audit — 2026-10-26

## Scope and inspected path

This audit follows the current research-branch implementation from manifest construction through pin-ledger verification and comparison-gate consumption. It is a code-path audit only; it does not claim that a production or live holdout workflow has been authenticated.

1. `DatasetManifest.create(...)` computes a deterministic SHA-256 fingerprint from manifest fields. This establishes content consistency, not publisher identity.
2. `DatasetManifestPinLedger.append(manifest)` adds the manifest fingerprint to a hash-chained ledger. `to_json()` serializes it, but the module does not persist it to durable storage or publish an external attestation.
3. `DatasetManifestPinLedger.from_json(..., expected_external_tip_fingerprint=...)` verifies the chain and supplied expected tip. It does not fetch or authenticate the source of that expected tip.
4. `DatasetManifestRegistry(trusted_pins=...)` accepts a caller-provided mapping. The registry validates mapping format and manifest equality, but cannot independently establish that the mapping came from a trusted authority.
5. `evaluate_comparison_validation_gate(..., dataset_manifest_registry=...)` requires a registry for `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT` and checks the upstream research record against the registered manifest. It does not acquire or authenticate the registry's pin source itself.

## Findings

- Integrity checks and chain verification are implemented.
- Pin authenticity, publisher identity, durable independent storage, and verifier/publisher permission separation are not implemented by this path.
- The current gate can only rely on trust established by the caller outside this code. A caller-generated digest, environment variable, label, or pin stored next to the ledger is not sufficient evidence of an independent trust root.
- The inspected code and synthetic tests do not demonstrate that a real holdout has been independently frozen or authenticated.

## Fail-closed disposition

Until an independently controlled trust source is selected and its identity/signature is verified by the surrounding workflow, do not mark a pin as externally trusted and do not treat `FRESH_HOLDOUT` as independently authenticated. Keep the existing provenance gate, but report the external trust-root prerequisite as unresolved.

## Required decision and implementation criteria

A follow-up implementation requires a concrete trust-source decision before coding. Acceptable design candidates include a signed attestation with a verified issuer/signing identity or a separately administered immutable registry. The chosen contract must bind the attestation to the exact manifest revision, dataset ID/fingerprint, ledger tip, and record count as applicable; define key/identity rotation and revocation behavior; and record source identity, payload digest, verification result, and verification time.

Adversarial tests must fail closed for missing/invalid signatures, wrong or untrusted identity, revoked identity, replayed attestation, manifest/revision mismatch, ledger-tip/count mismatch, and unavailable trust service. A plain expected-tip string is not an authenticated attestation.

## Scope exclusions

No canonical SP2L geometry, execution/fill semantics, BUY/SELL logic, statistical-edge claim, or production authorization is changed by this audit. No local worktree, MT5 session/account, Strategy A forward test, Strategy B run, merge, or deployment is part of this change.
