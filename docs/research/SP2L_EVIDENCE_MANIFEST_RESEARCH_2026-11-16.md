# SP2L Evidence Manifest — Offline Research Model (2026-11-16)

**Status:** research implementation; local synthetic validation pending  
**Canonical status:** non-canonical; no production caller  
**Runtime boundary:** no filesystem access, hashing, serialization, MT5 calls, broker access, or Runner integration

## Purpose

Provide a typed record that links a scoped history observation to declared evidence artifacts and capture provenance. The record is intended to make later evidence review reproducible: what was captured, under which declared account/session/server/time scope, by which capture method/tool version, and which exact artifact bytes are referenced.

## Model

- `EvidenceManifestRecord` records an opaque manifest ID, record time, opaque account/session references, server and requested interval, declared time basis/source, package and terminal build metadata, capture method/tool version, observation IDs, and artifact records.
- `EvidenceArtifactRecord` records an artifact ID/role, locator, byte length, and SHA-256 digest.
- Validation is deterministic and pure: required fields, tuple shapes, unique observation/artifact IDs, nonnegative integer byte length, and 64-hex-character digest shape are checked.
- A zero-byte artifact is allowed; its digest is still a declared SHA-256 value.
- Artifact order is preserved as supplied. No sorting or canonical serialization is imposed.

## Exact hash meaning

`byte_sha256` is intended to mean SHA-256 over the exact byte sequence of the referenced artifact, with no text decoding, newline conversion, row sorting, field selection, or semantic normalization. This module does not compute or verify that digest or byte length. It does not establish that a locator exists or that the artifact at that locator is immutable.

This is deliberately different from the external row-payload fingerprints in the stability model. Their algorithm and canonicalization remain unresolved.

## Deferred decisions

The following are intentionally not defined:
- JSON/YAML or other manifest serialization and canonical byte representation;
- manifest self-hash/signature, chain-of-custody signing, or trusted timestamping;
- artifact storage scheme, retention, immutability, or path normalization;
- raw MT5 row serialization, ordering, field selection, or semantic fingerprints;
- how API observations map into artifact roles beyond operator-declared labels;
- account identity verification itself or broker archive completeness.

No manifest field or successful validation may set `history_completeness_verified=True`. A valid record means only that its declared structure is internally well-formed; it does not authenticate its claims.

## Synthetic validation scope

The test module covers valid records, missing/blank provenance, duplicate IDs, invalid tuple shapes, invalid hashes, invalid/negative byte lengths, zero-byte artifacts, and the explicit boundary that locators/digests are accepted as declarations without filesystem verification.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification is part of this model.
