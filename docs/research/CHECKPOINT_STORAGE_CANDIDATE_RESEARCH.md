# Checkpoint storage candidate research

**Status:** PUBLIC-DOCUMENTATION REVIEW — CANDIDATES NOT SELECTED  
**Reviewed:** 2026-10-31  
**Related controls:** `INDEPENDENT_CHECKPOINT_PROVIDER_EVALUATION.md` and `FRESH_HOLDOUT_TRUST_ANCHOR_REQUIREMENTS.md`

## Purpose and scope

This note screens three managed object-storage services as possible **storage primitives** for independently retained audit checkpoints:

1. Amazon S3 with Versioning and Object Lock.
2. Azure Blob Storage with immutable storage/WORM.
3. Google Cloud Storage with a locked bucket retention policy.

These are not complete checkpoint services. Public documentation establishes useful storage features, but does not by itself establish the SP2L-specific protocol: canonical request identity, atomic uniqueness for (audit identity, sequence), authoritative conflict reconciliation, authenticated checkpoint receipts, independent administration in our deployment, or crash-safe recovery. No candidate is selected or approved.

The review is limited to public vendor documentation. No account, tier, region, configuration, role assignment, service contract, or controlled fault-injection environment has been inspected.

## Public-documentation comparison

| Capability | Amazon S3 | Azure Blob Storage | Google Cloud Storage |
|---|---|---|---|
| Strong read-after-write | Documented for object PUT/DELETE and related metadata reads | Documented strong consistency after insert/update; subsequent reads/lists return latest update | Documented strong global consistency for object read-after-write and object listing |
| Conditional create / no-overwrite primitive | `If-None-Match: *` for supported writes; conflicting existing key returns 412; concurrent delete can yield 409 | Conditional headers and ETag-based optimistic concurrency; If-Match mismatch returns 412. Exact create-only operation needs endpoint-specific validation | `ifGenerationMatch=0` succeeds only when no live object exists; failed precondition returns 412 |
| Compare-and-swap primitive | `If-Match` on ETag for supported writes | `If-Match` on ETag | Generation/metageneration match preconditions |
| WORM / retention | Object Lock with Governance or Compliance mode; requires Versioning | Immutable storage with time-based retention and legal holds; container- and version-level modes | Bucket retention policy; locked policy cannot be removed or shortened |
| Important deletion / overwrite nuance | Object Lock protects a specific version; simple DELETE can add an unprotected delete marker and hide the protected version | Container WORM can prohibit overwrite; protected append writes are a special explicitly enabled mode. Version-level WORM has versioning and overwrite semantics that need configuration-specific review | Locked retention protects objects from deletion/replacement until retention expiry; bucket policy lock is irreversible |
| Provider-documented receipt protocol for this use case | Not established by reviewed storage docs | Not established by reviewed storage docs | Not established by reviewed storage docs |
| Independent admin separation in our deployment | Not evaluated | Not evaluated | Not evaluated |

## Candidate A — Amazon S3

### Documented strengths

- S3 documents strong read-after-write consistency for object PUT and DELETE operations, including object metadata reads.
- Conditional writes support `If-None-Match` to prevent overwriting an existing key and `If-Match` to condition writes on an ETag. S3 documents 412 precondition failures and 409 conflict behavior for certain concurrent operations.
- Object Lock provides WORM retention. In Compliance mode, a protected object version cannot be overwritten or deleted by any user, including the account root user, during the retention period.

### Material caveats

- Object Lock requires Versioning and applies to object versions. It does not prevent a new version or a delete marker from being added over a protected version. A simple DELETE can make the object appear deleted by adding a delete marker. The proposed design must prevent or independently detect this.
- Governance mode is bypassable by principals with the relevant permission; it is not equivalent to Compliance mode.
- Conditional object writes and strong consistency are useful primitives, but the reviewed documentation does not define our logical checkpoint receipt, stable request-ID behavior, audit-identity/sequence uniqueness, or lost-response reconciliation.
- Account, organization, root, IAM, retention, and break-glass roles would need a concrete separation review.

### Preliminary evidence status

- P2/P3 primitive support: **PARTIAL** — conditional create/update and strong consistency are documented, but SP2L logical uniqueness and conflict reconciliation remain unimplemented.
- P5 retention primitive: **PARTIAL** — strong version retention exists, but delete-marker behavior and version selection require an explicit design and tests.
- P1/P6/P8/P9/P10/P11/P12: **OPEN** for the actual deployment and protocol.

## Candidate B — Azure Blob Storage

### Documented strengths

- Azure documents strong consistency: after insert/update, subsequent read/list operations return the latest update.
- ETag-based optimistic concurrency supports conditional updates; an If-Match mismatch returns HTTP 412. Blob leases provide a separate pessimistic write-coordination primitive.
- Immutable storage supports time-based retention and legal holds. Container-level WORM documentation describes protected append writes for append blobs when the relevant setting is enabled.

### Material caveats

- The reviewed concurrency documentation says default behavior is last-writer-wins if no concurrency strategy is specified; the adapter must always use explicit conditions.
- Container-level protected append writes are a specialized mode with policy/configuration constraints. It must not be assumed that ordinary blob upload semantics provide append-only checkpoint behavior.
- Version-level WORM, account/container inheritance, versioning, overwrite behavior, and policy lock must be evaluated for the exact chosen account and container configuration.
- Azure Blob Storage documentation does not establish an SP2L checkpoint receipt protocol or provider-side uniqueness for our logical request identity.
- Microsoft Entra role separation, subscription/tenant administration, break-glass access, immutable-policy administration, and independent evidence export remain to be demonstrated.

### Preliminary evidence status

- P2/P3 primitive support: **PARTIAL** — ETag conditions and strong consistency are documented; create-only semantics and the exact atomic operation must be verified against the selected API.
- P5 retention primitive: **PARTIAL** — WORM features are documented; selected policy scope, append mode, versioning, and administrator exceptions need proof.
- P1/P6/P8/P9/P10/P11/P12: **OPEN** for the actual deployment and protocol.

## Candidate C — Google Cloud Storage

### Documented strengths

- Cloud Storage documents strong global consistency for object read-after-write and object listing.
- The JSON API supports `ifGenerationMatch=0` to create an object only if no live version exists; a failed precondition returns 412. Generation and metageneration preconditions can be used for conditional updates.
- Bucket Lock can permanently lock a retention policy; after locking, the retention period cannot be reduced or the policy removed. Objects under the policy cannot be deleted or replaced until their retention period is satisfied.

### Material caveats

- Locking a bucket retention policy is irreversible. Retention duration, bucket lifecycle, project lien, billing/account continuity, and legal/compliance responsibility require explicit review before use.
- Bucket Lock protects retained objects; it does not by itself define the latest-checkpoint protocol, logical uniqueness, authenticated receipt, or lost-response resolution.
- The documented create-only generation precondition is a promising primitive, but same-sequence conflict comparison and authoritative tip selection must be implemented and fault-tested.
- Project, organization, IAM, billing, key-management, and emergency administration must be separated from the runtime and local audit administrators.

### Preliminary evidence status

- P2/P3 primitive support: **PARTIAL** — generation preconditions, strong consistency, and object listing are documented; SP2L-level uniqueness and conflict reconciliation remain unimplemented.
- P5 retention primitive: **PARTIAL** — locked retention is documented; deployment-level access and recovery controls remain unverified.
- P1/P6/P8/P9/P10/P11/P12: **OPEN** for the actual deployment and protocol.

## Cross-candidate design implications

A plausible pattern to investigate is an immutable checkpoint object under a deterministic key derived from the audit identity and sequence, created with a provider's atomic create-only precondition. On a duplicate response, the adapter would read the authoritative object and compare the complete immutable request digest; an exact match could be classified as a replay, while a different digest must be surfaced as a conflict. A separate latest-tip pointer would require a conditional compare-and-swap against the prior generation/ETag.

This is a **candidate design pattern only**, not an approved protocol. It still needs:
- canonical serialization and stable request identity;
- exact provider-specific conditional-write mapping;
- authoritative list/read and monotonic revision rules;
- receipt authenticity and retention;
- delete-marker/version-hiding protection;
- independent administration and audit export;
- crash/retry reconciliation for commit-before-response-loss;
- controlled R1–R8 fault-injection tests.

Object storage's successful HTTP response, ETag, generation number, or request ID must not automatically be treated as a cryptographically authenticated SP2L receipt. The adapter must define and verify the evidence needed for the trust boundary.

## Current screening conclusion

All three candidates expose useful documented primitives. None is proven suitable for the SP2L control from this documentation-only screen. No ranking or provider recommendation is justified yet.

The next evidence-gathering step is to identify which provider environments the operator can actually administer with a separate security boundary, then complete P1–P12 for only those candidates. If no independent administrative boundary can be established, do not proceed to adapter implementation.

## Primary vendor sources

### Amazon S3
- [S3 data consistency model](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [Conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)
- [Enforce conditional writes on buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes-enforce.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Object Lock considerations and delete markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html)

### Azure Blob Storage
- [Immutable storage overview](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
- [Manage concurrency in Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/concurrency-manage)
- [Container-level WORM policies and protected append writes](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-container-level-worm-policies)
- [Version-level WORM policies](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-version-level-worm-policies)

### Google Cloud Storage
- [Cloud Storage consistency](https://docs.cloud.google.com/storage/docs/consistency)
- [Request preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions)
- [Objects: insert API](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/insert)
- [Bucket Lock](https://docs.cloud.google.com/storage/docs/bucket-lock)
- [Lock retention policy API](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets/lockRetentionPolicy)

## Explicit non-claims

This note does not select a provider, establish a production security posture, implement an adapter, prove remote durability or authenticated receipts, resolve canonical SP2L geometry, authorize Fresh Holdout, or permit Forward/Runtime/MT5/production BUY/SELL execution.
