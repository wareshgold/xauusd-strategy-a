# ADR: External Dataset Pin Trust Source — 2026-10-26

- Status: **Proposed; operator/security-owner decision required before implementation**
- Scope: research dataset provenance for `UNTOUCHED_VALIDATION` and `FRESH_HOLDOUT` only.
- Does not define canonical SP2L geometry or trading/execution rules.

## Decision context

The current implementation verifies deterministic manifest fingerprints and a hash-chained pin ledger against an expected tip supplied by its caller. It does not authenticate who issued that expected tip. The repository's read-only trust-root inspection did not establish a separately administered, protected release channel. Therefore no existing pin value may be promoted to an authenticated trust anchor merely because it is present in the repository.

## Options

| Option | Strengths | Risks / requirements | Current disposition |
|---|---|---|---|
| Signed attestation with independently verified issuer | Cryptographically binds a payload to an identified signing identity; can be checked by a verifier without trusting the mutable ledger location | Must choose issuer/identity policy, signing workflow, keyless or key-based verification, revocation/rotation behavior, payload schema, and permissions | **Preferred design candidate**, not yet authorized or wired |
| Separately administered immutable registry | Can separate publication and consumption permissions and retain audit history | Requires a real registry, ownership/access-control evidence, immutable version semantics, availability policy, and an authenticated client | Viable alternative if already operated independently |
| Pin file, environment variable, boolean, or source label in the same mutable repository/workflow | Easy to add | Does not establish independent authenticity; a party able to change the workflow or file may replace both data and pin | Rejected as a trust root |
| Existing repository tag or release without verified protection/identity evidence | Familiar and inspectable | Name or existence alone does not prove immutability, signer identity, or admin separation | Not accepted absent independent control evidence |

## Recommended direction

Proceed with a provider-neutral signed-attestation contract only after the operator/security owner confirms the actual signing identity or issuer and where its trust policy is maintained. Do not assume GitHub release/tag protections or an installed signing service that have not been verified.

The attested payload should bind at minimum:
- attestation schema/version and issuance time;
- dataset ID and exact manifest revision/fingerprint;
- ledger revision, exact tip fingerprint, and pin count;
- immutable artifact identifier and digest when applicable;
- signer/issuer identity and verification-policy identifier.

The verifier must derive trust from a configured, independently administered identity policy—not from a field inside the untrusted payload. Persist the verified attestation and its digest through a durable channel with auditability. Separate publish and verify permissions where practical.

## Required fail-closed tests

- missing attestation or unavailable trust source;
- malformed payload or unsupported schema;
- missing, malformed, or invalid signature;
- wrong, untrusted, expired, or revoked issuer/identity;
- replayed or stale attestation under the selected freshness policy;
- mismatch in dataset ID, manifest revision/fingerprint, artifact digest, ledger tip, or pin count;
- inability to retrieve the durable attestation;
- trust-policy changes and key/identity rotation.

Every failure must leave the holdout gate blocked and must not silently fall back to a caller-provided digest. Tests must use synthetic fixtures and must not imply that a real dataset has been frozen.

## Activation gate

Implementation can begin once the owner identifies the real independent trust channel and confirms its control/permission model. Until then, `FRESH_HOLDOUT` remains blocked from any claim of independently authenticated provenance. Existing hash-chain and registry checks remain integrity controls only.
