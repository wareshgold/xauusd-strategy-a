# Fresh Holdout trust-anchor requirements

**Status:** PARTIAL IMPLEMENTATION — NOT A PRODUCTION AUTHORIZATION  
**Scope:** Strategy Factory Fresh Holdout -> Forward provenance boundary  
**Current PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`

## Finding

The Factory recomputes readiness snapshots from supplied Manifest, Passport, and Source Ledger objects; binds the accepted Holdout result through ForwardGateResult and DemoForwardSession; and checks internal identities/fingerprints before the runtime runner is called.

A first cryptographic primitive now exists in `src/strategy_factory/trust_anchor.py`. It verifies Ed25519 signatures over canonical JSON, checks expiry and a key-revocation list, compares independently assembled expected identity bindings, re-hashes the artifact at verification time, and resolves public keys only from a fixed system keyring path (Linux: `/etc/sp2l/trust/holdout-ed25519-keyring.json`; Windows: `C:/ProgramData/SP2L/trust/holdout-ed25519-keyring.json`). The verifier fails closed if the envelope, artifact, keyring, or trusted key is missing or invalid. The repository contains no private signing key.

**Current boundary behavior:** the signed envelope binds the exact pre-transition source event-ledger prefix (SHA-256, byte size, event-count boundary, and persisted-vs-in-memory source type). A changed or corrupt prefix is rejected before the transition event is appended. The session carries those signed fields and the persisted journal path, and checks them again during runtime signature verification. For `persisted_jsonl`, runtime re-reads and validates the current journal, verifies the exact signed prefix bytes/hash/size/event boundary, and permits later valid appended events. The path is included in signed bindings, but the file is not yet sourced from an independently controlled journal service; `in_memory` remains synthetic-only and does not provide persisted-prefix verification. The later Forward Gate separately records the post-Holdout-event ledger snapshot. The verifier runs before Holdout-to-Forward event append and again at runtime preflight and immediately before runner invocation. A new system-path audit (`verification-audit.jsonl`) records successful verification phases in a locked, fsynced, hash-chained JSONL ledger. Holdout-to-Forward consumes an exact signed-envelope SHA-256 only once. If consumption succeeds but the first transition append fails without changing the journal, an explicit recovery audit record permits retry only for the same envelope, same session, and byte-identical signed source-journal boundary. If the journal has changed, recovery is blocked for manual reconciliation. Runtime preflight/dispatch are repeatable and separately audited. Corrupt audit history or an unavailable audit path fails closed. The hash chain is tamper-evident against ordinary edits, not a substitute for independent backups or a separately controlled trust root; privileged filesystem access could rewrite the entire chain.

SHA-256 fingerprints are integrity identifiers, not digital signatures. Frozen dataclasses and self-consistent fingerprints do not establish who created evidence or prove that it came from an independently controlled source.

## Remaining requirements before production authorization

1. **Independent trust root:** provision the keyring outside source control, under operating-system/service-account write controls. The evidence caller must not be able to replace the registry or choose a different trust root.
2. **Complete signed evidence envelope:** bind at minimum:
   - strategy ID and frozen strategy revision;
   - Manifest revision, readiness snapshot fingerprint, and Source Ledger fingerprint/evidence identifiers;
   - Fresh Holdout dataset ID, role, content SHA-256, artifact ID, and byte size;
   - research run ID/fingerprint, evidence ID/fingerprint, audit fingerprint, accepted-record fingerprint, and a single forward-session ID;
   - source event-ledger prefix SHA-256, byte size, event-count/sequence boundary, source type, and persisted journal path (when applicable), captured before the Holdout-to-Forward transition mutates the journal;
   - issuer/key ID, creation time, expiry/revocation metadata, and schema version.
3. **Independent verification:** the verifier is now called at Holdout-to-Forward and twice along the runtime path (session preflight and immediately before runner invocation). Expected bindings are assembled from the source record/session objects, not copied from the signed envelope. Caller injection of a permissive verifier or alternate trust root is prohibited.
4. **Key lifecycle and revocation:** revoked-key rejection is implemented and tested through the system keyring's `revoked_key_ids` list. Still define operational key custody, rotation, recovery, and incident response. Never place a private signing key in source control or a caller-controlled payload.
5. **Replay protection:** durable one-time consumption of the signed envelope at Holdout-to-Forward and signed pre-transition event-ledger boundary binding are implemented. Recovery is implemented only when the envelope was consumed but the journal remained unchanged before the first transition append; failures after any transition event or other journal mutation still require manual reconciliation. Independent control of the journal source/path and independently retained anti-truncation evidence remain outstanding.
6. **Auditability:** retain the verified envelope, signer/key ID, verifier version, trust-root revision, verification result, and artifact digest in an append-only evidence record.
7. **Adversarial tests:** cover absent/malformed/altered signatures, expired and not-yet-valid envelopes, unknown/revoked keys, wrong artifact bytes, replay, unsupported schema, and mismatched strategy/revision. Each must be rejected before downstream adapter/runner invocation.

## Explicit non-goals

- This implementation does not resolve SP2L source questions or define canonical P-Gap, AB=CD, fill, or execution rules.
- It does not claim a profitable edge or canonical readiness.
- It does not enable real Fresh Holdout, MT5 forward execution, live orders, or production BUY/SELL decisions.
- A test-only signer, caller-provided public key, shared secret embedded in code, or self-signed envelope without an independently pinned trust root does not satisfy this requirement.

## Release gate

Although signature verification, one-time envelope consumption, and hash-chained verification audit are now wired and covered by tests, the system trust store/audit directory have not been provisioned or independently reviewed here; independent journal-source control and recovery after a mutated or partially completed transition remain incomplete; and the complete provenance envelope is not yet bound. Fresh Holdout -> Forward -> Runtime remains **research-only / BLOCKED for production authorization**. These controls are defense-in-depth groundwork, not production authorization.
