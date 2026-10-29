# Fresh Holdout trust-anchor requirements

**Status:** PARTIAL IMPLEMENTATION — NOT A PRODUCTION AUTHORIZATION  
**Scope:** Strategy Factory Fresh Holdout -> Forward provenance boundary  
**Current PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`

## Finding

The Factory recomputes readiness snapshots from supplied Manifest, Passport, and Source Ledger objects; binds the accepted Holdout result through ForwardGateResult and DemoForwardSession; and checks internal identities/fingerprints before the runtime runner is called.

A first cryptographic primitive now exists in `src/strategy_factory/trust_anchor.py`. It verifies Ed25519 signatures over canonical JSON, checks expiry and a key-revocation list, compares independently assembled expected identity bindings, re-hashes the artifact at verification time, and resolves public keys only from a fixed system keyring path (Linux: `/etc/sp2l/trust/holdout-ed25519-keyring.json`; Windows: `C:/ProgramData/SP2L/trust/holdout-ed25519-keyring.json`). The verifier fails closed if the envelope, artifact, keyring, or trusted key is missing or invalid. The repository contains no private signing key.

**Important limitation:** this primitive is not yet wired into the Holdout-to-Forward transition or runtime preflight. The verifier now runs at the Holdout-to-Forward boundary before the event journal is appended, and again at runtime immediately before the injected runner is invoked. It still does not implement replay protection, create an append-only verification audit, or bind every provenance field listed below. Therefore the existing Factory chain must not be considered cryptographically authenticated.

SHA-256 fingerprints are integrity identifiers, not digital signatures. Frozen dataclasses and self-consistent fingerprints do not establish who created evidence or prove that it came from an independently controlled source.

## Remaining requirements before production authorization

1. **Independent trust root:** provision the keyring outside source control, under operating-system/service-account write controls. The evidence caller must not be able to replace the registry or choose a different trust root.
2. **Complete signed evidence envelope:** bind at minimum:
   - strategy ID and frozen strategy revision;
   - Manifest revision, readiness snapshot fingerprint, and Source Ledger fingerprint/evidence identifiers;
   - Fresh Holdout dataset ID, role, content SHA-256, artifact ID, and byte size;
   - research run, execution receipt, evidence, audit and accepted-record fingerprints;
   - source event-ledger digest, byte size, and event sequence boundary;
   - issuer/key ID, creation time, expiry/revocation metadata, and schema version.
3. **Independent verification:** the verifier is now called at Holdout-to-Forward and twice along the runtime path (session preflight and immediately before runner invocation). Expected bindings are assembled from the source record/session objects, not copied from the signed envelope. Caller injection of a permissive verifier or alternate trust root is prohibited.
4. **Key lifecycle and revocation:** revoked-key rejection is implemented and tested through the system keyring's `revoked_key_ids` list. Still define operational key custody, rotation, recovery, and incident response. Never place a private signing key in source control or a caller-controlled payload.
5. **Replay protection:** bind a unique evidence ID and event-sequence boundary and enforce a durable replay policy.
6. **Auditability:** retain the verified envelope, signer/key ID, verifier version, trust-root revision, verification result, and artifact digest in an append-only evidence record.
7. **Adversarial tests:** cover absent/malformed/altered signatures, expired and not-yet-valid envelopes, unknown/revoked keys, wrong artifact bytes, replay, unsupported schema, and mismatched strategy/revision. Each must be rejected before downstream adapter/runner invocation.

## Explicit non-goals

- This implementation does not resolve SP2L source questions or define canonical P-Gap, AB=CD, fill, or execution rules.
- It does not claim a profitable edge or canonical readiness.
- It does not enable real Fresh Holdout, MT5 forward execution, live orders, or production BUY/SELL decisions.
- A test-only signer, caller-provided public key, shared secret embedded in code, or self-signed envelope without an independently pinned trust root does not satisfy this requirement.

## Release gate

Although signature verification is now wired at both boundaries and revocation rejection is tested, the system trust store has not been provisioned or independently reviewed here, replay protection and append-only verification audit remain absent, and the complete provenance envelope is not yet bound. Fresh Holdout -> Forward -> Runtime remains **research-only / BLOCKED for production authorization**. The verifier primitive is defense-in-depth groundwork, not a completed trust boundary.
