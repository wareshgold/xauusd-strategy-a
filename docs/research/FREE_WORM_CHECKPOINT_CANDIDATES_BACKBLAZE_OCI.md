# Free WORM checkpoint provider candidates — Backblaze B2 and OCI

**Status:** PUBLIC-DOCUMENTATION SCREEN — NO PROVIDER SELECTED OR CONFIGURED  
**Reviewed:** 2026-10-31  
**Related PR:** #368, `fix/fresh-holdout-readiness-gate-20261029`  
**Predecessor:** `CLOUDFLARE_R2_GITHUB_CHECKPOINT_ASSESSMENT.md`

## Executive finding

**Backblaze B2 is the strongest free-tier candidate identified so far for a time-bounded WORM checkpoint store.** Its published free allowance includes the first 10 GB of storage, and Backblaze documents Object Lock with Compliance-mode retention. The vendor states Object Lock has no separate feature charge; normal storage charges still apply. The documented Compliance mode cannot be removed or bypassed by users, while Governance mode can be overridden by appropriately capable application keys.

This is materially different from Cloudflare R2: R2's reviewed S3 compatibility table marks S3 Object Lock unsupported.

Backblaze B2 is **not approved**. We have not inspected an actual account, enabled Object Lock, configured retention, demonstrated independent administration, verified exact API behavior for this checkpoint protocol, or executed adversarial integration tests. The free allowance is a capacity allowance, not a promise that every account operation or future usage will remain free.

Oracle Cloud Infrastructure (OCI) Object Storage is a second candidate: Oracle publishes an Always Free allowance of 20 GB combined across Standard, Infrequent Access, and Archive tiers for Always Free-only accounts, plus 50,000 Object Storage API requests/month. Oracle documents bucket-level retention rules that prevent object update/overwrite/delete while the rule applies. The reviewed documentation does not yet establish that the retention rule itself can be made independently undeletable under the exact free-tier configuration, so OCI remains a secondary candidate pending a focused control-plane review.

## 1. Backblaze B2

### Published free tier and feature cost

- The first 10 GB of B2 storage is free.
- The first 10 GB does not require a paid capacity commitment; pricing material describes pay-as-you-go storage after the free allowance.
- Class A, B, and C API transactions are listed as free for pay-as-you-go customers in the current pricing materials reviewed.
- Egress is free up to 3x the average monthly storage amount under the published allowance.
- Backblaze states there is no additional charge for Object Lock itself; normal storage charges still apply to locked data.
- A Backblaze help article states that a B2 account can start with 10 GB free storage and does not require a billing method to begin exploring the service. Confirm current signup requirements at account creation; this research did not create an account.

### Object Lock semantics

Backblaze documents:
- Object Lock must be enabled on the bucket; once enabled, it cannot be disabled.
- Files can receive retention in Governance or Compliance mode.
- Governance retention may be overridden by clients with appropriate application-key capabilities.
- Compliance retention cannot be removed by any user; retention dates may be extended by clients with appropriate capabilities.
- Legal Hold is a separate control and can be removed by a sufficiently authorized user; do not treat Legal Hold alone as equivalent to Compliance retention.
- Default Bucket Retention applies the configured retention to newly uploaded/copied files.
- The documented retention period range is 1–3,000 days.
- Attempts to modify or delete a protected file before retention expiry fail.

### Preliminary assessment

| Requirement | Status | Evidence / remaining work |
|---|---|---|
| Free small-footprint storage | EVIDENCED (published allowance) | First 10 GB free; actual usage must be monitored |
| Object Lock / WORM primitive | EVIDENCED | Compliance mode documented |
| Compliance-mode non-bypass | EVIDENCED (vendor feature semantics) | Must verify effective per-object retention on actual uploaded objects |
| Create-only logical checkpoint key | PARTIAL | S3 conditional writes need exact endpoint/race tests |
| Independent account/admin boundary | OPEN | Need separate account ownership, app-key scope, recovery/admin review |
| Authenticated SP2L receipt | OPEN | B2 response/ETag is not an SP2L signed receipt |
| Anti-truncation across account closure/provider loss | OPEN | Object Lock does not prove account continuity or independent external witness |
| Lost-response reconciliation | OPEN | Requires adapter protocol and fault-injection tests |

### Candidate disposition

**Advance B2 to a controlled technical feasibility review**, subject to operator confirmation that a separately administered B2 account is available or acceptable. Do not enable Object Lock or create a bucket yet. Enabling Object Lock is a one-way bucket setting and retention mistakes can be operationally costly.

The first sandbox test, after explicit approval, should use a disposable bucket with a short, reviewed Compliance retention period and synthetic non-sensitive data only. It should verify upload response, GetObjectRetention, exact duplicate create, different-content collision, overwrite attempt, delete attempt, and independent readback using a separate read-only application key. It must also prove which account administrators can change bucket settings, keys, lifecycle, and account status.

## 2. Oracle Cloud Infrastructure Object Storage

### Published Always Free allowance

Oracle's current Always Free documentation states:
- Always Free-only accounts: 20 GB combined across Standard, Infrequent Access, and Archive tiers.
- 50,000 Object Storage API requests per month.
- For paid accounts or accounts still using Free Trial credits, the allowance is presented as 10 GB Standard + 10 GB Infrequent Access + 10 GB Archive, plus 50,000 requests. Do not conflate this display with the 20 GB combined allowance for Always Free-only accounts.
- If a Free Trial ends and usage exceeds the Always Free limit, Oracle warns that objects may be deleted to bring usage within the limit. Keep the proposed dataset well below the limit and verify account state.

### Retention primitive

Oracle's security documentation says bucket-level retention rules can provide WORM behavior: objects and object metadata cannot be updated, overwritten, or deleted while the retention rule applies. The documentation distinguishes indefinite and time-bound retention rules.

### Open questions

- Can the retention rule itself be locked against deletion or weakening in the exact Object Storage/free-tier configuration?
- Which IAM principals can create, modify, or delete retention rules, buckets, keys, and the tenancy?
- Can runtime upload permissions be separated from retention-policy administration and account recovery?
- Does the chosen retention configuration remain available after trial expiry or account state transitions?
- Which API preconditions provide atomic create-only and conditional tip updates?

### Candidate disposition

Keep OCI as a secondary candidate. Its published free storage is attractive, but the exact control-plane protection for the retention policy must be proven before it can be treated as a WORM trust anchor.

## 3. Relative decision

| Candidate | Free allowance | WORM evidence | Current disposition |
|---|---:|---|---|
| Backblaze B2 | First 10 GB free | Compliance-mode Object Lock documented; no separate Object Lock fee | **First candidate for controlled feasibility review** |
| OCI Object Storage | 20 GB combined Always Free-only allowance; 50,000 requests/month | Bucket retention rules documented; retention-rule admin lock still OPEN | Secondary candidate |
| Cloudflare R2 | 10 GB-month Standard free tier | S3 Object Lock unsupported in reviewed compatibility documentation | Not suitable as sole WORM anchor |
| GitHub Immutable Releases | Included subject to GitHub plan/repository limits | Assets immutable while release exists, but release deletion remains possible | Artifact/attestation complement only |

## 4. Provider-neutral synthetic acceptance tests

These are specifications only; no test was executed by this document.

1. **Create-once:** two concurrent create-only writes for the same logical identity/sequence; at most one first creation.
2. **Exact replay:** duplicate with identical canonical request digest is reconciled by authoritative read and classified EXACT_REPLAY.
3. **Conflicting replay:** same identity/sequence but different digest is CONFLICT; never overwrite.
4. **Lost response:** request may have committed but client timed out; classify UNKNOWN until authoritative read reconciles.
5. **Stale tip:** conditional compare-and-swap against an old ETag/generation must fail and force reread.
6. **Compliance retention:** retrieve per-object retention metadata and prove it is Compliance mode with the expected expiry.
7. **Overwrite/delete denial:** attempt overwrite and delete using the runtime application key and a separate ordinary administrator key; both must fail before expiry.
8. **Policy administration:** prove which distinct principal can alter retention policy, bucket, account, app keys, and recovery settings.
9. **Independent verification:** read checkpoint and verify receipt/request binding from a separate machine and identity.
10. **Provider outage/account loss:** document and test the fail-closed response; do not infer acknowledgement from a timeout or missing object.

A passing storage primitive test does not prove a complete SP2L checkpoint protocol. The adapter must still define canonical serialization, stable request identity, receipt authentication, monotonic tip semantics, replay/conflict handling, and recovery.

## 5. Next gate

Before any provider integration:
1. Operator confirms an available or acceptable independent provider account.
2. Establish account owner/admin and runtime application-key separation.
3. Review region, retention duration, account continuity, billing/usage alerts, export/recovery, and legal requirements.
4. Approve a disposable synthetic-only sandbox test.
5. Run adversarial tests and retain immutable evidence outside the runtime administrator's control.

If no independent administration boundary can be demonstrated, Fresh Holdout remains BLOCKED. No provider selection, adapter, runtime integration, production authorization, or trading behavior is changed by this note.

## 6. Primary vendor sources

### Backblaze
- B2 pricing and free allowance: https://help.backblaze.com/hc/en-us/articles/217667478-Understanding-B2-Pricing-Structure
- B2 transaction pricing: https://www.backblaze.com/cloud-storage/transaction-pricing
- Object Lock FAQ (Compliance vs Governance; no additional Object Lock fee): https://help.backblaze.com/hc/en-us/articles/360052973274-Object-Lock-FAQs
- Enable Object Lock / Legal Hold: https://help.backblaze.com/hc/en-us/articles/1260804731990-Object-Lock-Legal-Hold

### Oracle Cloud Infrastructure
- Always Free Object Storage allowance: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Object Storage security and WORM retention rules: https://docs.oracle.com/en-us/iaas/Content/Security/Reference/objectstorage_security.htm
- Object Storage overview: https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm

### Previously screened
- Cloudflare R2 S3 API compatibility: https://developers.cloudflare.com/r2/api/s3/api/
- GitHub Immutable Releases: https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases
