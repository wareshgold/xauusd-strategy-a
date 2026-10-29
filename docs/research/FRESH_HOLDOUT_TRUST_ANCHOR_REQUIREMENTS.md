# Fresh Holdout trust-anchor requirements

**Status:** DESIGN REQUIREMENTS ONLY — NOT A PRODUCTION AUTHORIZATION  
**Scope:** Strategy Factory Fresh Holdout -> Forward provenance boundary  
**Current PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`

## Finding

The Factory now recomputes readiness snapshots from supplied Manifest, Passport, and Source Ledger objects; binds the accepted Holdout result through ForwardGateResult and DemoForwardSession; and checks internal identities/fingerprints before the runtime runner is called.

These checks detect inconsistency between the supplied objects. They do **not** establish who created those objects or prove that the evidence came from an independently controlled source. SHA-256 fingerprints are integrity identifiers, not digital signatures. Frozen dataclasses and self-consistent fingerprints are not an authenticity boundary against a caller able to construct Python objects.

Repository search on 2026-10-29 found no existing Ed25519/signature/attestation implementation under `src/strategy_factory`. No signing key, trusted public-key registry, external attestation service, or key-rotation policy is currently established by this work. Therefore no cryptographic authenticity claim is made.

## Required trust model before any production authorization

1. **Independent trust root:** pin an externally controlled public key or equivalent trust anchor. The verifier and trust root must not be supplied by the same untrusted caller as the evidence.
2. **Signed evidence envelope:** verify a detached signature over a canonical, versioned envelope that binds at minimum:
   - strategy ID and frozen strategy revision;
   - Manifest revision and readiness snapshot fingerprint;
   - Source Ledger fingerprint and source-evidence identifiers;
   - Fresh Holdout dataset ID, role, content SHA-256, artifact ID, and byte size;
   - research run, execution receipt, evidence, audit and accepted-record fingerprints;
   - source event-ledger digest, byte size, and event sequence boundary;
   - issuer/key ID, creation time, expiry/revocation metadata, and schema version.
3. **Independent verification:** perform signature verification and revocation/expiry checks at the Holdout-to-Forward boundary and again before runtime execution. The caller must not be able to inject a permissive verifier or replace the trust root in the same request.
4. **Artifact re-hash:** read the actual immutable artifact and recompute its digest at the point of use; do not trust a digest string alone.
5. **Fail closed:** missing signature, unknown/revoked key, unsupported schema, expired envelope, digest mismatch, or identity mismatch must block the transition before any adapter/runner invocation.
6. **Auditability:** retain the verified envelope, signer/key ID, verifier version, trust-root revision, verification result, and artifact digest in an append-only evidence record.
7. **Key lifecycle:** define offline/private-key custody, rotation, revocation, recovery, and incident response before deploying signing. Never place a private signing key in source control or a caller-controlled payload.
8. **Adversarial tests:** test absent, malformed, altered, expired, unknown-key, revoked-key, wrong-artifact, replayed-envelope, and mismatched-strategy signatures. Each must be rejected before the downstream runner is called.

## Explicit non-goals

- This document does not resolve SP2L source questions or define canonical P-Gap, AB=CD, fill, or execution rules.
- It does not claim a profitable edge or canonical readiness.
- It does not enable real Fresh Holdout, MT5 forward execution, live orders, or production BUY/SELL decisions.
- A test-only signer, caller-provided public key, shared secret embedded in code, or a self-signed envelope without an independently pinned trust root does not satisfy this requirement.

## Release gate

Until the trust model above is implemented, independently reviewed, and covered by adversarial tests, the Fresh Holdout -> Forward -> Runtime chain remains **research-only / BLOCKED for production authorization**. The current source-backed readiness and provenance checks remain useful defense in depth, but must not be described as cryptographic authentication.
