# Fresh Holdout trust-anchor requirements

**Status:** PARTIAL IMPLEMENTATION — NOT A PRODUCTION AUTHORIZATION  
**Scope:** Strategy Factory Fresh Holdout -> Forward provenance boundary  
**Current PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`

## Finding

The Factory recomputes readiness snapshots from supplied Manifest, Passport, and Source Ledger objects; binds the accepted Holdout result through ForwardGateResult and DemoForwardSession; and checks internal identities/fingerprints before the runtime runner is called.

A first cryptographic primitive now exists in `src/strategy_factory/trust_anchor.py`. It verifies Ed25519 signatures over canonical JSON, checks expiry and a key-revocation list, compares independently assembled expected identity bindings, re-hashes the artifact at verification time, and resolves public keys only from a fixed system keyring path (Linux: `/etc/sp2l/trust/holdout-ed25519-keyring.json`; Windows: `C:/ProgramData/SP2L/trust/holdout-ed25519-keyring.json`). The verifier fails closed if the envelope, artifact, keyring, or trusted key is missing or invalid. The repository contains no private signing key.

**Current boundary behavior:** the signed envelope binds the exact pre-transition source event-ledger prefix (SHA-256, byte size, event-count boundary, and persisted-vs-in-memory source type). A changed or corrupt prefix is rejected before the transition event is appended. The session carries those signed fields and the persisted journal path, and checks them again during runtime signature verification. For `persisted_jsonl`, runtime re-reads and validates the current journal, verifies the exact signed prefix bytes/hash/size/event boundary, and permits later valid appended events. The path is included in signed bindings, but the file is not yet sourced from an independently controlled journal service; `in_memory` remains synthetic-only and does not provide persisted-prefix verification. The later Forward Gate separately records the post-Holdout-event ledger snapshot. The verifier runs before Holdout-to-Forward event append and again at runtime preflight and immediately before runner invocation. A new system-path audit (`verification-audit.jsonl`) records successful verification phases in a locked, fsynced, hash-chained JSONL ledger. Holdout-to-Forward consumes an exact signed-envelope SHA-256 only once. If consumption succeeds but the first transition append fails without changing the journal, one explicit recovery audit record permits a retry candidate only for the same envelope, same session, and byte-identical signed source-journal boundary. A second recovery record for the same envelope is rejected, even if the boundary is unchanged, so repeated calls cannot manufacture multiple recovery events. If the journal has changed or a recovery record already exists, automatic recovery is blocked for manual reconciliation. A read-only recovery classifier now reports whether no consumption exists, the same-session/same-boundary case is only a recovery candidate, the session/boundary differs, a recovery record already exists, or the audit chain is invalid. It never appends or repairs records, never authorizes automatic recovery, and cannot by itself establish whether transition events completed; that requires a separate journal/lifecycle reconciliation. A separate read-only Holdout-to-Forward lifecycle classifier now checks the journal snapshot against the in-memory ledger and distinguishes absent transition evidence, Holdout completion without a Forward handoff, session mismatch, duplicate transition events, and a recorded handoff. A recorded handoff explicitly does not prove runtime execution. Invalid/unavailable or divergent persisted journals require manual reconciliation; the classifier never retries or mutates the journal. Runtime preflight/dispatch are repeatable and separately audited. Corrupt audit history or an unavailable audit path fails closed. The audit reader also rejects incomplete final JSONL records, duplicate JSON keys, non-canonical record encodings, and boolean values masquerading as integer sequence numbers; it does not append to or normalize an invalid chain. The hash chain is tamper-evident against ordinary edits, not a substitute for independent backups or a separately controlled trust root; privileged filesystem access could rewrite the entire chain.

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
5. **Replay protection:** durable one-time consumption of the signed envelope at Holdout-to-Forward and signed pre-transition event-ledger boundary binding are implemented. The Holdout -> Forward preparation now holds the journal's shared OS sidecar lock from pre-transition boundary capture through evidence consumption, lifecycle appends, and gate/session preparation; internal appends use a thread-bound lock token to avoid nested OS-lock acquisition. A cross-platform test verifies a cooperating writer cannot enter the critical section until preparation returns, and stale writers fail closed after acquiring the released lock. This serializes cooperating journal writers but is not a distributed transaction across the separate Trust Audit and journal files. If the journal is modified by a writer that bypasses the shared-lock contract, or if a failure occurs after the envelope is consumed, the system fails closed and manual reconciliation may still be required. Failure-injection coverage now records the expected partial states: (a) consumption followed by a failed first append with an unchanged journal is only a single-use recovery candidate after fresh verification; (b) failure after `COMPLETED`, including during gate or session preparation, leaves `COMPLETED` only and requires manual reconciliation; (c) failure after durable `HANDOFF_ACCEPTED` leaves both transition events but does not prove the caller received the result or that runtime executed. The lifecycle classifier is diagnostic only and never retries. No cross-file atomicity is claimed. Independent control of the journal source/path and independently retained anti-truncation evidence remain outstanding.
6. **Auditability:** retain the verified envelope, signer/key ID, verifier version, trust-root revision, verification result, and artifact digest in an append-only evidence record.
7. **Adversarial tests:** cover absent/malformed/altered signatures, expired and not-yet-valid envelopes, unknown/revoked keys, wrong artifact bytes, replay, unsupported schema, and mismatched strategy/revision. Each must be rejected before downstream adapter/runner invocation.

## Deployment review checkpoint — independent trust root (2026-10-29)

### Code-review result

The verifier does not accept a public key or keyring path through its public function arguments, and it resolves a fixed OS-specific path. This prevents the evidence caller from selecting an alternate trust root through the verifier API. **It does not prove that the configured keyring is independently controlled on a deployed host.** The current implementation reads the fixed path as an ordinary file; it does not itself attest owner identity, write ACLs/mode, symlink/reparse-point status, service-account separation, or change-monitoring coverage. Those properties must be established by host provisioning and independently reviewed evidence, not inferred from a passing unit test.

### Required provisioning evidence — not yet supplied

Do not authorize Fresh Holdout -> Forward -> Runtime until an operator who is independent of the evidence producer records and a reviewer verifies all of the following:

- [ ] The production public keyring is provisioned at the documented OS path by a separately authorized deployment identity; no private signing key is present on the runtime host or in source control.
- [ ] The runtime service identity has read-only access to the keyring and cannot replace, rename, delete, or change its parent directory; the evidence-producing identity cannot change the trust root.
- [ ] Owner, ACL/mode, parent-directory permissions, symlink/reparse-point handling, and the actual resolved file identity are inspected using platform-appropriate controls. Any policy for these properties is enforced by deployment controls or a reviewed verifier change; a fixed pathname alone is not proof.
- [ ] Keyring version/revision and SHA-256 are recorded in an independently retained deployment receipt, with operator, reviewer, timestamp, host identity, and provisioning procedure/version.
- [ ] Key addition, revocation, rotation, emergency replacement, backup/recovery, and incident response are rehearsed. Revocation data is protected at the same trust level as the keys.
- [ ] A negative test on the provisioned host demonstrates that the runtime identity cannot modify the keyring or its parent directory, and an unauthorized keyring replacement causes verification to fail closed.
- [ ] The journal source and audit directory are separately controlled, and anti-truncation evidence is retained outside the same administrative boundary.

The receipt must contain evidence/results, not only checkboxes or a statement that provisioning was completed. Do not include private key material or sensitive credentials in the receipt.

### Artifact-consumption boundary

A successful verification hashes the artifact at verification time, but the current bridge still passes control to an injected runner after a path-based check. This review has **not** established that the runner consumes the same immutable bytes if the path changes immediately after verification. Before production authorization, either pass a pinned/read-only artifact handle or immutable content-addressed artifact identity through to the consumer, or demonstrate an equivalent enforced storage/locking design with a race-injection test. A second hash check narrows but does not mathematically eliminate a path replacement race.

## Anti-truncation checkpoint design review — proposal only (2026-10-29)

### Finding

The local JSONL audit validates a contiguous sequence and hash chain starting from the all-zero genesis digest. This detects edits, deletion, or reordering when a later retained entry still commits to the missing history. It cannot independently detect whole-file deletion, rollback to an older valid prefix, or replacement with a newly constructed valid chain, because the verifier has no independently retained expected tip. The local file is therefore not an anti-truncation trust anchor.

### Minimum external checkpoint contract — not implemented

A future checkpoint adapter must be separately designed and reviewed. At minimum, after each successful audit append it must publish a signed or service-authenticated checkpoint to a trust domain whose write/delete permissions are independent from the runtime identity and local audit-directory administrators. The checkpoint record should bind:

- schema/version and checkpoint sequence;
- audit identity and environment/host identity;
- latest audit entry sequence and entry_sha256 chain tip;
- exact audit file identity and byte size at checkpoint time;
- UTC checkpoint time and verifier/writer build identity;
- previous checkpoint digest or monotonic service-side revision;
- authenticated publisher identity and remote receipt/acknowledgement.

The checkpoint store must reject rollback/replay and provide a way to retrieve the latest independently retained checkpoint. A local copy of the checkpoint beside the audit file does not satisfy independence. Do not implement a home-grown signature or assume a timestamp alone prevents rollback.

### Draft machine-readable contract — not wired into runtime

A provider-neutral JSON Schema draft is stored at `docs/research/schemas/independent-audit-checkpoint-v1.schema.json`. It describes the proposed request and receipt envelopes and rejects undeclared top-level fields. It is a design artifact only: the runtime does not load it, no adapter validates receipts against it, and the provider-specific authentication payload is intentionally unresolved. The canonical serialization used to derive request IDs, receipt authentication/verification, revision semantics, and service consistency must be specified and tested before this schema can be considered an implementation contract.

### Proposed adapter boundary and receipt contract — design only

Keep provider-specific code outside the trust-audit writer. The future integration should depend on a narrow adapter contract with these semantic operations (names are illustrative, not an existing API):

- `publish_checkpoint(request) -> acknowledged_receipt`: durably create or idempotently confirm one checkpoint.
- `read_latest_checkpoint(audit_identity) -> checkpoint | unavailable`: return the authoritative latest checkpoint from the independent trust domain; never silently fall back to a local cache.
- `verify_receipt(request, receipt) -> verified | reject`: validate service identity/authentication, request binding, revision, and acknowledgement.

A request must be deterministic and include a schema version, stable request ID, audit identity, environment identity, audit sequence, entry digest, previous checkpoint digest/revision, local audit byte size, and writer build/version. The stable request ID must be derived from canonical serialization of the immutable request fields; timestamps or retry counters must not make a retry look like a new logical request. The authenticated receipt must bind the request ID and digest, accepted checkpoint revision, accepted tip sequence/digest, service identity, and server-side acknowledgement time. Exact serialization, authentication mechanism, retention guarantees, and service consistency model must be selected and reviewed for the chosen provider before implementation.

Required state model:

- **UNANCHORED:** local audit may exist, but no valid independent receipt confirms its current tip. It cannot authorize a lifecycle transition.
- **PUBLISH_PENDING:** a local append has occurred and checkpoint publication is in progress. No downstream authorization is permitted.
- **ANCHORED:** the independent service has acknowledged the exact current tip, and the receipt has been validated and retained.
- **CONFLICT / UNKNOWN:** timeout, mismatched receipt, stale revision, divergent tip, or ambiguous service result. Block and require a read-after-write reconciliation; never infer success from a timeout.

Do not collapse `PUBLISH_PENDING` or `CONFLICT / UNKNOWN` into success. The adapter must define how the caller learns that an operation committed despite a lost response, and how an idempotent retry retrieves the original receipt. If the selected service cannot provide a reliable authoritative read and conflict detection, it is unsuitable for this control.

### Design review checklist before implementation

- Select the independent trust domain and identify which operators can write/delete checkpoints versus administer the runtime host and local audit directory.
- Document availability policy, consistency/read-after-write behavior, retention/immutability, backup, incident recovery, authentication, key rotation, and audit export.
- Decide the transaction boundary between local append and remote acknowledgement; document crash recovery at every boundary without claiming atomicity across them.
- Threat-model malicious rollback by a privileged local administrator, remote credential compromise, service outage, replay, duplicate request, lost response, clock skew, and disaster recovery.
- Specify whether a checkpoint is required after every audit record or at a coarser cadence. Any batching creates a documented unanchored window and must not authorize protected transitions within that window.
- Keep provider credentials out of source control, artifact payloads, and logs; use the platform's supported secret/identity mechanism only after the deployment model is chosen.

This proposal intentionally does not choose a vendor, credential mechanism, endpoint, or retention product. No provider can be selected responsibly from the current code evidence alone.

### Required fail-closed behavior and recovery

- Before trusting an existing audit, compare its validated sequence/tip with the latest independently retrieved checkpoint and verify the recorded byte-size/file-prefix binding.
- If the audit is shorter than the checkpoint, its tip differs, the remote checkpoint is unavailable when policy requires it, or checkpoint history is stale/ambiguous, block Fresh Holdout -> Forward -> Runtime and require manual reconciliation.
- If audit append succeeds locally but external checkpoint publication fails, report an explicit uncertain state. Do not silently treat the event as fully anchored, retry a non-idempotent lifecycle transition, or delete the local record to “roll back.”
- Define idempotency by a stable checkpoint request ID derived from the audit identity, sequence, and entry digest. A retry may confirm the same checkpoint, but must not create a conflicting checkpoint for the same sequence.
- Recovery must compare independently retained checkpoints and local audit history; it must never rebuild a missing historical prefix from the current file alone.

### Acceptance tests required before claiming anti-truncation protection

1. Delete the whole local audit after at least one externally acknowledged checkpoint: startup/append must fail closed.
2. Restore an older, internally valid audit prefix: checkpoint comparison must fail closed.
3. Replace the audit with a different, internally valid chain at the same or lower sequence: checkpoint comparison must fail closed.
4. Simulate checkpoint service timeout after local append: surface an uncertain/unanchored state and prevent downstream authorization.
5. Replay a prior checkpoint request and attempt a conflicting digest at the same sequence: service/adapter must reject the conflict and remain idempotent for the exact same request.
6. Verify the runtime identity and local audit administrator cannot alter or delete remote checkpoint history; retain independent test evidence.

No external checkpoint adapter, service integration, remote retention policy, or deployment evidence is present in this PR at this checkpoint. These requirements are a design gate, not a claim of implemented protection.

## Explicit non-goals

- This implementation does not resolve SP2L source questions or define canonical P-Gap, AB=CD, fill, or execution rules.
- It does not claim a profitable edge or canonical readiness.
- It does not enable real Fresh Holdout, MT5 forward execution, live orders, or production BUY/SELL decisions.
- A test-only signer, caller-provided public key, shared secret embedded in code, or self-signed envelope without an independently pinned trust root does not satisfy this requirement.

## Release gate

Although signature verification, one-time envelope consumption, and hash-chained verification audit are now wired and covered by tests, the system trust store/audit directory have not been provisioned or independently reviewed here; independent journal-source control and recovery after a mutated or partially completed transition remain incomplete; and the complete provenance envelope is not yet bound. Fresh Holdout -> Forward -> Runtime remains **research-only / BLOCKED for production authorization**. These controls are defense-in-depth groundwork, not production authorization.


### Synthetic idempotency contract tests — not an adapter

The schema test suite now includes a deliberately small in-memory model for the documented replay boundary: within one audit identity, the same sequence and same entry digest is classified as an exact replay; the same identity and sequence with a different entry digest is classified as a conflict. It also checks that a different audit identity does not collide solely because its sequence matches.

These are synthetic contract tests only. They do not define canonical request serialization, derive or verify `request_id`, establish remote uniqueness/transaction guarantees, resolve lost-response behavior, or implement a checkpoint service. Those remain open design and integration requirements. No Fresh Holdout authorization may rely on this test model.

### Synthetic timeout and acknowledgement boundary tests — not recovery logic

The schema test suite now includes a negative authorization predicate for synthetic observations. It asserts that a pending publication, timeout/unknown result, conflict, unverified receipt, or receipt whose request binding does not match cannot pass the test-only authorization predicate. The sole positive fixture requires an acknowledged publication together with a verified receipt and matching request binding.

This is deliberately not a publication state machine, retry algorithm, read-after-write implementation, or production authorization hook. It does not decide how an authoritative service lookup resolves a lost response, what consistency guarantees are sufficient, how receipt authentication is performed, or whether a remote acknowledgement is durable under a provider's failure model. Those decisions remain blocked on provider selection and an independently reviewed adapter contract. The positive fixture is a logical contract example only; it is not evidence that any real service has acknowledged or retained a checkpoint.

### Provider recovery acceptance matrix — proposal only

This matrix defines evidence to collect when a concrete checkpoint provider and adapter have been selected. It is not a provider-independent implementation specification: exact retry, lookup, consistency, and revision semantics must be mapped to the selected provider's documented guarantees before these cases become executable integration tests.

| Case | Injected condition | Required safety observation | Provider-specific question / evidence |
|---|---|---|---|
| R1 — timeout before remote commit | Publish request times out and authoritative lookup finds no checkpoint | State remains unanchored/unknown; protected transition is blocked | How is absence distinguished from delayed visibility or lookup failure? |
| R2 — commit with lost response | Service commits, but acknowledgement is dropped | No success is inferred from timeout; protected transition stays blocked until authoritative reconciliation verifies the exact request and tip | Can lookup prove the committed request identity and return its original authenticated receipt? |
| R3 — exact retry | Retry the immutable logical request after R2 | No second logical checkpoint is created; only the exact original checkpoint may be confirmed | What is the provider's idempotency-key scope, retention window, and duplicate-request response? |
| R4 — conflicting same sequence | Same audit identity and sequence are submitted with a different entry digest | Conflict is surfaced; neither payload is silently accepted as equivalent | Is uniqueness enforced atomically by the service, and what durable conflict evidence is returned? |
| R5 — lookup unavailable | Publish result is ambiguous and authoritative lookup is unavailable | Remain unknown/unanchored; no local cache or timeout heuristic can authorize | What outage policy and retry/backoff limits apply without weakening the gate? |
| R6 — stale or divergent lookup | Lookup returns a checkpoint behind the local tip, or a different tip/revision | Block; preserve both local and remote evidence for reconciliation | What consistency guarantee, monotonic revision, and anti-rollback property does the service provide? |
| R7 — acknowledgement/receipt mismatch | Receipt has wrong request binding, sequence, digest, byte size, service identity, or authentication | Reject receipt and block | How is service identity and receipt authenticity independently verified? |
| R8 — crash after acknowledgement | Service acknowledges, process crashes before persisting receipt locally | Restart must not assume success from local absence; reconcile with authoritative service before any protected action | Can the service retrieve the original receipt by stable request identity after restart and across retention boundaries? |

#### Required test evidence for each case

- Immutable input request bytes/fields and their independently computed test-fixture digest; do not treat the current draft `request_id` field as canonically derived.
- Provider, service/API version, environment, adapter build, test timestamp, and authenticated service identity.
- Fault-injection point and whether the remote service committed, did not commit, or left the result indeterminate, established from provider-side evidence rather than inferred from the client exception.
- Raw response/receipt or sanitized provider-side lookup evidence, plus verification outcome. Secrets and credentials must never enter test artifacts.
- Local audit sequence/tip/byte-size before and after the case, and explicit record of whether any downstream transition or runner invocation was attempted.
- Independent reviewer sign-off that the provider's documented consistency, idempotency, retention, authentication, and conflict semantics actually cover the tested case.

#### Promotion rule

Do not convert this matrix into passing integration tests by mocking the provider's desired answer. First select a provider and document its guarantees; then implement a narrow adapter; then run fault-injection tests against a controlled provider environment and retain independent evidence. A mocked adapter may test caller handling, but cannot prove remote uniqueness, durability, read-after-write consistency, receipt authenticity, or independent administrative control.

Until R1–R8 are demonstrated against the selected service, timeout/lost-response recovery remains unresolved. In particular, no test-only `ACKNOWLEDGED` fixture is evidence of a real checkpoint, and no Fresh Holdout, Forward, Runtime, or production authorization may rely on this proposal.

