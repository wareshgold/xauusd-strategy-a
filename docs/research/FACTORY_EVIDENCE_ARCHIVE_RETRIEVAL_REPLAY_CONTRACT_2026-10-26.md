# Factory Evidence Archive, Retrieval, and Replay Contract — 2026-10-26

Status: first local content-addressed adapter and verification interface implemented; no provider-grade durable archive, archive-record manifest index, replay runner, or trust root is implemented or implied.

## Purpose

Define the minimum evidence lifecycle needed to independently retrieve and replay a Factory provenance decision. This contract is separate from source-rule resolution and does not make a research result canonical, validation-safe, or production-eligible.

## Assurance vocabulary

Every consumer must keep these claims distinct:

1. **Fingerprint-consistent** — retrieved bytes match a recorded digest under a specified digest and canonicalization rule.
2. **Retrievable** — the exact referenced bytes can be fetched from the declared archive location.
3. **Replay-consistent** — replaying a pinned evaluator/policy over the exact archived inputs reproduces the expected decision fingerprint and status.
4. **Issuer-authenticated** — a separate trusted mechanism verifies who issued an attestation and that it covers these exact artifacts and policy revision.

No one level implies the next. A successful replay is not issuer authentication. An unkeyed digest is not a signature. A URL or object key is not proof of immutability or availability.

## Required archive manifest

A future implementation must define a versioned manifest with, at minimum:

- manifest_schema_revision;
- stable archive_record_id;
- creation timestamp in UTC and explicit clock/source semantics;
- each artifact's logical role, schema revision, content digest algorithm, canonicalization revision, digest, byte length, and immutable locator;
- exact artifact roles for test specification, research job, run identity, execution receipt, evidence bundle, research audit, readiness snapshot, dataset-provenance result, and provenance decision;
- evaluator/policy revision and code revision required for replay;
- dataset manifest fingerprint and dataset-role declaration where applicable;
- replay result fingerprint/status when replay has been performed;
- declared assurance level and unresolved limitations.

The manifest itself must be serialized under a versioned canonicalization rule and have its own digest. Changing artifact bytes, roles, locator metadata, or policy identity must change the appropriate digest or manifest revision. A mutable locator may be retained as a convenience but must not be the sole identity of an artifact.

## Implemented first increment\n\n`src/strategy_factory/evidence_archive.py` now defines a versioned manifest, artifact descriptors, a storage adapter protocol, explicit retrieval outcomes, and pre-parse SHA-256/byte-length verification. The adapter contract distinguishes `ARTIFACT_NOT_FOUND` from `ARCHIVE_UNAVAILABLE`; invalid manifests, undeclared roles, length mismatches, and digest mismatches return no artifact bytes. `EvidenceArchiveManifest.from_dict(...)` checks schema and digest algorithm and verifies the declared manifest fingerprint. `FileSystemContentAddressedStore` writes bytes under a SHA-256 content locator using create-if-absent publication, supports idempotent repeated writes, and verifies stored bytes on reads. The manifest carries `CONTENT_DIGEST_ONLY_NOT_DURABLE_NOT_AUTHENTICATED` assurance scope and rejects attempts to relabel itself as authenticated.\n\nTests cover both an in-memory fake and a temporary local filesystem. The local adapter persists across object re-instantiation and avoids overwriting an existing content-addressed path, but it is not WORM storage and does not protect against a privileged local actor, media loss, deletion, or host failure. There is still no archive-record manifest index/commit protocol or replay evaluator. The adapter is a local implementation, not a selected external provider.\n\n## Write and retrieval behavior

The archive API should expose explicit outcomes rather than collapsing failures into PASS:

- STORED_AND_VERIFIED;
- ALREADY_PRESENT_MATCHING_DIGEST;
- DIGEST_MISMATCH;
- ARTIFACT_NOT_FOUND;
- ARCHIVE_UNAVAILABLE;
- SCHEMA_UNSUPPORTED;
- MANIFEST_INVALID;
- POLICY_OR_EVALUATOR_UNAVAILABLE.

Write semantics must be idempotent for the same archive-record identity and exact manifest digest. A conflicting manifest for the same immutable identity must be rejected rather than silently overwritten. Retrieval must verify byte length and digest before parsing. Missing or unavailable evidence must remain unavailable; the system must not reconstruct or infer missing source artifacts.

Storage retention, immutability/WORM properties, access control, backup, deletion policy, and service-level availability remain provider-specific requirements to be decided before implementation. Do not claim those guarantees from an ordinary object URL or local file path alone.

## Replay behavior

Replay must:

1. retrieve every required artifact by the manifest's immutable identity;
2. verify the digest and schema revision of every artifact before parsing;
3. require the exact evaluator/policy revision named by the manifest, or return POLICY_OR_EVALUATOR_UNAVAILABLE;
4. run the evaluator without substituting current defaults or current datasets;
5. compare the recomputed status, reasons, input-fingerprint mapping, and decision fingerprint to the archived decision;
6. emit a separate replay record containing input manifest digest, evaluator/policy revision, replay timestamp, result, and mismatch reasons.

Replay results should be one of REPLAY_MATCH, REPLAY_MISMATCH, REPLAY_BLOCKED_MISSING_INPUT, REPLAY_BLOCKED_POLICY_UNAVAILABLE, or REPLAY_BLOCKED_SCHEMA_UNSUPPORTED. A replay mismatch must not rewrite the original archived decision or its evidence.

## Independent trust root

This contract deliberately does not select a signing provider, key-management system, or separately administered registry. Before claiming issuer authentication, the owner/security owner must select and document a trust root and verification policy that binds at least:

- issuer identity and key/certificate identity;
- artifact-manifest digest;
- dataset manifest fingerprint/revision;
- evaluator/policy revision;
- issuance time and expiry/revocation policy;
- anti-replay identifier and signature/attestation format.

Missing, invalid, expired, revoked, untrusted, stale, or mismatched attestations must fail closed. A caller-supplied boolean, self-declared issuer string, or recomputed unkeyed hash is insufficient.

## Dataset-role and certification gates

Until independent dataset trust is implemented, UNTOUCHED_VALIDATION and FRESH_HOLDOUT remain blocked by the existing fail-closed gates. Archiving or replaying a development result must not promote it to validation/holdout or production eligibility. A replay only establishes reproducibility under the pinned inputs and evaluator.

## Acceptance tests required before implementation is considered complete

- exact manifest serialization/fingerprint is deterministic and tampered manifest payloads are rejected;\n- local content-addressed writes are idempotent and readable after reopening the adapter;\n- retrieval verifies content digest and byte length before returning bytes;\n- missing and unavailable storage outcomes are distinct;\n- unsupported schema, undeclared roles, duplicate roles, and false assurance scope are rejected;
- each artifact digest/length mismatch is rejected;
- missing and unavailable artifacts remain distinct blocked outcomes;
- duplicate write with identical digest is idempotent;
- conflicting write cannot overwrite an existing immutable record;
- unsupported schema/evaluator revision blocks replay without falling back to current defaults;
- replay of unchanged artifacts yields REPLAY_MATCH;
- changed artifact, policy, role, or decision yields REPLAY_MISMATCH or an explicit blocked status;
- replay does not mutate the original archive record;
- an unsigned archive cannot report issuer-authenticated assurance;
- trust-root tests cover invalid signature, wrong issuer, expired/revoked identity, replayed attestation, and key/policy rotation.

## Explicit non-goals

This proposal does not choose an archive vendor, signing service, key, trust-root owner, retention duration, or deployment target. It does not define SP2L geometry, P-Gap, AB=CD anchors/tolerance, fill semantics, trade execution, canonical strategy rules, or production BUY/SELL decisions. Those decisions require their own source or owner confirmation.
