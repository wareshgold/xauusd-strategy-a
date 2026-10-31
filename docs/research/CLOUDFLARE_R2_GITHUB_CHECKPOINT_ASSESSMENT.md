# Cloudflare R2 and GitHub checkpoint candidate assessment

**Status:** DOCUMENTATION-ONLY SCREEN — NO PROVIDER SELECTED, NO ADAPTER IMPLEMENTED  
**Reviewed:** 2026-10-31  
**Related PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`

## Executive result

Cloudflare R2 is attractive for a low-cost research checkpoint store, but the reviewed R2 S3-compatibility documentation explicitly marks S3 Object Lock as unsupported, including bucket-level enablement and per-object retention headers. Therefore **R2 is not presently evidenced as a WORM/retention-locked checkpoint store** and must not be treated as an immutable trust anchor.

R2 does document atomic conditional `PutObject` writes using `If-None-Match: *`: for concurrent writes to an absent key, at most one succeeds and the others receive `412 PreconditionFailed`. This is useful for a create-once object primitive, but it does not prevent an authorized bucket administrator from deleting objects or deleting the bucket. It is not equivalent to WORM.

GitHub Immutable Releases protect published release assets and their associated tag from modification or deletion while the immutable release exists, and generate a verifiable release attestation. However, GitHub documents that a release itself can be deleted; the tag may then be deleted too (although the tag name cannot be reused). This is valuable artifact integrity / supply-chain evidence, but does not by itself establish independent anti-deletion retention or a separate administrator boundary from the repository/organization owner.

**Conclusion:** neither R2 alone nor GitHub Immutable Releases alone meets the current independent anti-truncation / retention requirement. They may be useful as complementary evidence replicas, but no composite design is approved by this note.

## 1. Cloudflare R2

### Evidence-supported strengths

- Standard storage Free Tier: 10 GB-month, 1 million Class A operations/month, 10 million Class B operations/month; egress is free. The Free Tier applies to Standard storage.
- R2 documents strong consistency and atomic evaluation of conditional writes.
- `PutObject` supports `If-None-Match: *`; concurrent create-once requests for the same absent key are serialized so at most one succeeds, while the others receive HTTP 412.
- R2 exposes S3-compatible and Workers APIs.

### Disqualifying limitation for sole trust-anchor use

The current R2 S3 API compatibility table marks all of the following unsupported:
- `CreateBucket` with `x-amz-bucket-object-lock-enabled`;
- `PutObject` retention headers `x-amz-object-lock-mode` and `x-amz-object-lock-retain-until-date`;
- object legal hold;
- Object Lock bypass-governance-retention behavior.

The R2 release notes also state that enabling S3 Object Lock at bucket creation is not supported. Therefore do not infer WORM protection from R2 conditional writes, object metadata, lifecycle settings, or a dashboard label. The reviewed public sources do not establish an administrator-proof retention lock for the required checkpoint objects.

### Preliminary evidence status

| Requirement | R2 status | Reason |
|---|---|---|
| Low-cost storage | PARTIAL | Published free tier is useful; usage and billing limits still need operational controls |
| Strong consistency | EVIDENCED | Vendor documents strong consistency |
| Atomic create-once | EVIDENCED | Conditional `PutObject If-None-Match: *` |
| Conditional tip update | PARTIAL | `If-Match` is documented; exact protocol and races need tests |
| WORM / retention lock | NOT SUPPORTED (reviewed S3 API) | Object Lock APIs/headers are marked unsupported |
| Independent administration | OPEN | No account, role, or operator boundary inspected |
| Authenticated SP2L receipt | OPEN | Storage response/ETag is not an SP2L-signed receipt |
| Lost-response reconciliation | OPEN | Requires adapter protocol and fault injection |

**Disposition:** reject R2 as the sole independent immutable checkpoint anchor on current evidence. Keep it as a possible low-cost conditional-write replica or research fixture target only.

## 2. GitHub Immutable Releases

### Evidence-supported strengths

- Once an immutable release is published, its assets cannot be modified or deleted and its associated tag cannot be moved or deleted while that release exists.
- GitHub automatically creates a cryptographically verifiable release attestation binding the tag, commit SHA, and release assets.
- Immutable release support is generally available and can be enabled at repository or organization level.

### Material limitations

- GitHub's documentation explicitly allows deleting an immutable release. After release deletion, its tag can be deleted, although the same tag name cannot be reused.
- Immutable releases protect release assets and tag; they do not make the entire repository, release record, organization, or administrative account undeletable.
- If the same administrators control the source journal, repository, release settings, and release deletion, the independent-administration requirement is not demonstrated.
- GitHub Actions artifacts have retention settings and should not be substituted for immutable release retention.

### Preliminary evidence status

| Requirement | GitHub status | Reason |
|---|---|---|
| Artifact integrity | EVIDENCED (release scope) | Immutable assets and signed release attestation |
| Tag immutability | EVIDENCED while release exists | Tag cannot be moved/deleted while immutable release exists |
| Anti-deletion retention | PARTIAL / NOT ESTABLISHED | Release deletion remains possible |
| Independent administration | OPEN | Depends on separate organization/owner/control boundary |
| Atomic checkpoint uniqueness | NOT ESTABLISHED | Release feature is not a checkpoint CAS protocol |
| Authenticated SP2L receipt | OPEN | GitHub attestation format is not the required SP2L receipt protocol |
| Lost-response reconciliation | OPEN | Requires explicit protocol |

**Disposition:** useful for publishing frozen research artifacts and attestations, but not sufficient as the sole anti-truncation trust anchor.

## 3. Synthetic adapter contract tests — specification only

No live account, credentials, bucket, Worker, GitHub Release, or runtime adapter is created by this research task. The following are test cases to implement against a future provider-neutral fake and, only after operator approval, a selected provider sandbox.

| ID | Scenario | Expected classification / invariant |
|---|---|---|
| R2-SYN-01 | First create with `If-None-Match: *` | One immutable-by-convention object created; record provider response metadata |
| R2-SYN-02 | Exact duplicate create | 412 followed by authoritative read; identical canonical request digest => EXACT_REPLAY |
| R2-SYN-03 | Same logical key, different digest | 412 followed by read; digest mismatch => CONFLICT, never overwrite |
| R2-SYN-04 | Two concurrent create attempts | At most one success; loser must reconcile by read; no double acknowledgement |
| R2-SYN-05 | Timeout after request may have committed | UNKNOWN until authoritative read/retry reconciliation; never infer failure or success from timeout |
| R2-SYN-06 | Negative read while earlier write may still be in flight | Remain UNKNOWN; do not publish a second conflicting write solely from NoSuchKey |
| R2-SYN-07 | Delete by privileged bucket administrator | Demonstrate R2's lack of WORM against this threat; must fail the sole-anchor acceptance gate |
| R2-SYN-08 | Tip pointer CAS with stale ETag | Conditional update rejected; caller re-reads and reconciles; no last-writer-wins acceptance |
| GH-SYN-01 | Verify immutable release attestation | Verify exact tag, commit SHA, and asset digest |
| GH-SYN-02 | Attempt to modify immutable asset/tag | Rejected while release exists |
| GH-SYN-03 | Delete immutable release as authorized admin | Demonstrates release-level deletion remains possible; sole-anchor anti-truncation gate fails |
| CROSS-SYN-01 | Provider receipt absent, malformed, wrong request binding, or digest mismatch | Fail closed; no checkpoint authorization |
| CROSS-SYN-02 | Provider unavailable / conflicting tip / stale tip | UNKNOWN or CONFLICT; no checkpoint authorization |
| CROSS-SYN-03 | Same audit identity and sequence with another digest | CONFLICT; preserve both observations for manual reconciliation |

These are **acceptance-test specifications, not executed tests**. No passing test result is claimed.

## 4. Candidate architecture boundary

A potential future arrangement is:
- GitHub for source-controlled code, test specifications, frozen research artifacts, and release attestations;
- R2 for inexpensive off-site conditional-write replication;
- a separately administered WORM-capable provider or independently controlled retention service for the actual anti-truncation trust anchor.

This is only a decomposition of responsibilities. It is not an approved design or a provider selection. If no independently administered retention-capable service is available, Fresh Holdout remains blocked.

## 5. Primary vendor documentation

### Cloudflare
- R2 pricing / Free Tier: https://developers.cloudflare.com/r2/pricing/
- R2 consistency model and conditional writes: https://developers.cloudflare.com/r2/reference/consistency/
- R2 S3 API compatibility (including unsupported Object Lock features): https://developers.cloudflare.com/r2/api/s3/api/
- R2 release notes (Object Lock unsupported statement): https://developers.cloudflare.com/r2/platform/release-notes/
- R2 API surfaces: https://developers.cloudflare.com/r2/api/

### GitHub
- Immutable Releases: https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases
- Managing releases / deletion behavior: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- Immutable Releases GA announcement: https://github.blog/changelog/2025-10-28-immutable-releases-are-now-generally-available/

## Scope and safety

This is documentation and test-design work only. It does not:
- create or configure a Cloudflare or GitHub resource;
- store credentials, secrets, private keys, or user data;
- implement or invoke a checkpoint provider or runtime adapter;
- claim independent administration, WORM compliance, or production readiness;
- change SP2L geometry, P-Gap, AB=CD, fill semantics, execution rules, or trading behavior;
- authorize Fresh Holdout, Forward, production, or live orders.
