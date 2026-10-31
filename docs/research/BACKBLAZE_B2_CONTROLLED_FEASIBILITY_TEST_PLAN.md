# Backblaze B2 controlled feasibility test plan

**Status:** TEST PLAN ONLY — NOT EXECUTED  
**Candidate:** Backblaze B2  
**Related PR:** #368  
**Prerequisite research note:** `FREE_WORM_CHECKPOINT_CANDIDATES_BACKBLAZE_OCI.md`  
**Scope:** Disposable, synthetic-only storage experiment. No SP2L production data, credentials, live trading data, or Fresh Holdout data.

## 1. Decision boundary

B2 is an experimental candidate, not a selected provider or approved trust anchor. This plan defines how to test it and how to reject it. A passing test authorizes only the next engineering review; it does not authorize Factory integration, Fresh Holdout, production, or trading.

Do not create an account, bucket, key, or paid resource as part of this plan. Account creation and sandbox provisioning require explicit operator approval after reviewing ownership, billing, region, retention, and recovery implications.

## 2. Preconditions before provisioning

Record evidence for each item before creating a bucket:

- [ ] A provider account can be administered independently of the Factory runtime operator/credentials.
- [ ] Account owner, administrators, recovery contacts, and MFA are documented.
- [ ] Runtime identity can be restricted to the minimum bucket/object operations needed.
- [ ] A separate read-only verifier identity can read objects and retention metadata but cannot write, overwrite, delete, or change policy.
- [ ] The exact principals able to create/revoke application keys, change bucket settings, change lifecycle, alter retention defaults, and close/recover the account are documented.
- [ ] Region and data residency are acceptable.
- [ ] A short Compliance retention duration has been reviewed against the irreversible bucket Object Lock setting and operational consequences.
- [ ] Usage/billing visibility and alerting are available; the test remains comfortably within the published free allowance.
- [ ] Synthetic test payloads contain no personal, financial, trading, credential, or proprietary data.

**Stop condition:** If independent administration cannot be demonstrated, do not provision the sandbox. Record B2 as unsuitable for the required trust-anchor role.

## 3. Disposable sandbox design

Use one disposable bucket dedicated to this experiment. Enable Object Lock only after confirming the exact irreversible consequences. Use a short, explicitly approved Compliance retention period and a small synthetic dataset.

Identities:
- **Provisioning/admin identity:** used only for bucket setup and controlled administration; never stored in the runtime.
- **Runtime test identity:** minimum required object operations; no bucket administration, key administration, retention-policy administration, or account recovery.
- **Read-only verifier identity:** independent credentials; read object bytes, metadata, and retention state only.
- **Adversarial admin test identity:** a separately documented ordinary administrative principal, if available, to test whether Compliance retention can be bypassed through normal account-level permissions. Do not use the account master key as a routine test credential.

Never place credentials in Git, test fixtures, logs, screenshots, or committed evidence. Record only key identifiers and redacted permission summaries.

## 4. Required test cases

Every test records: test ID, UTC timestamp, bucket/region, object key, identity class, request parameters (with secrets removed), HTTP/API result, authoritative follow-up read, expected result, actual result, and evidence digest.

| ID | Test | Expected result | Failure disposition |
|---|---|---|---|
| B2-01 | Enable Object Lock on disposable bucket | Bucket reports Object Lock enabled; setting is treated as irreversible | Stop; do not use a valuable bucket |
| B2-02 | Upload synthetic object with explicit Compliance retention | Upload succeeds; authoritative retention read reports Compliance mode and exact reviewed expiry | Reject until semantics are explained |
| B2-03 | Read object and retention using read-only verifier | Exact bytes/digest and retention metadata match; no mutation permissions | Reject if verifier can mutate or cannot independently verify |
| B2-04 | Two concurrent create-only writes for same key, same bytes | At most one creates; loser reconciles by read and identifies exact replay | Reject if silent overwrite or ambiguous success |
| B2-05 | Create-only write for existing key with different bytes | Conflict/precondition failure; original bytes unchanged | Immediate reject if replacement occurs |
| B2-06 | Runtime identity attempts overwrite before expiry | Denied; original bytes and retention unchanged | Immediate reject if mutation succeeds |
| B2-07 | Runtime identity attempts delete before expiry | Denied; object remains readable with same retention | Immediate reject if deletion succeeds |
| B2-08 | Ordinary admin identity attempts bypass/delete before expiry | Compliance-protected object remains protected under documented semantics | Reject trust-anchor claim if ordinary admin bypasses it |
| B2-09 | Runtime identity attempts bucket/retention/key administration | Denied | Reject if runtime can weaken its own controls |
| B2-10 | Read-only verifier attempts write/delete/policy change | Denied | Reject if verifier is not read-only |
| B2-11 | Simulate lost upload response after request submission | Client marks outcome UNKNOWN; authoritative read reconciles exact object or confirms absence; no blind retry overwrite | Reject if timeout is treated as proof of commit |
| B2-12 | Repeat same logical identity with different canonical digest | Conflict; no overwrite; incident evidence retained | Reject if conflicting replay is accepted |
| B2-13 | Stale conditional tip update (if protocol uses a tip object) | Stale precondition fails; caller rereads and reconciles | Do not implement tip protocol until atomic semantics proven |
| B2-14 | Attempt lifecycle/policy change that would remove protected test object before expiry | Denied or demonstrably unable to remove Compliance-protected version | Reject if lifecycle/admin path defeats retention |
| B2-15 | Independent machine/account session reads object and verifies digest/retention | Same object bytes and metadata; verifier does not depend on runtime credentials | Reject independent-verification claim if not reproducible |

For create-only and concurrency behavior, test the exact API endpoint and headers intended for the adapter. Do not infer atomicity from a generic S3 compatibility claim. Capture both concurrent request outcomes and then perform an authoritative read.

## 5. Evidence and reproducibility

Store a test manifest containing:
- provider and API endpoint/version;
- account/tenant and bucket identifiers (non-secret);
- region;
- test plan revision and test-run ID;
- synthetic object keys, content digests, byte lengths;
- identity class and redacted permission summaries;
- request/response status and relevant headers with secrets removed;
- authoritative object version, ETag/checksum, and retention metadata;
- UTC timestamps from the test host;
- test outcome and reason;
- hashes of raw evidence files.

Preserve raw responses where safe, but redact authorization headers, access keys, account recovery data, and personal information. Keep a second evidence copy outside the runtime identity's write/delete authority. A Git commit alone is not an independent WORM witness.

## 6. Pass, fail, and inconclusive rules

**PASS for primitive feasibility** requires all of the following:
1. Compliance retention is confirmed by authoritative per-object readback.
2. Runtime and read-only identities cannot overwrite/delete protected objects before expiry.
3. Ordinary administrative paths tested cannot bypass Compliance retention.
4. Create-only concurrency has one winner and deterministic duplicate/conflict reconciliation.
5. Lost-response behavior is fail-closed and reconciled by authoritative read.
6. Runtime cannot administer keys, bucket policy, retention, or account recovery.
7. Independent verifier reproduces byte and retention verification.
8. Evidence is complete, hashed, and independently preserved.
9. Cost, free-tier usage, region, and account continuity are acceptable.

**FAIL** if any safety-critical mutation, bypass, permission-separation, or ambiguous-acknowledgement condition fails. Do not average critical failures into a score.

**INCONCLUSIVE** if a test cannot be executed, API semantics are ambiguous, evidence is missing, or a provider permission path cannot be inspected. Inconclusive is not a pass; retain BLOCKED status and either gather evidence or evaluate another provider.

## 7. After a pass

A pass permits a separate provider-neutral adapter design review only. That review must still define and test canonical serialization, stable request identity, authenticated SP2L receipts, monotonic checkpoint/tip semantics, exact replay/conflict handling, lost-response recovery, independent witness/anti-truncation, provider outage behavior, and account-loss recovery.

No real Factory checkpoint, Fresh Holdout dataset, production credential, or trading process may use the sandbox as a trust anchor without a later explicit approval and separate acceptance gate.

## 8. Candidate replacement rule

If B2 fails or remains inconclusive after a bounded review, stop investing in B2 integration. Preserve the failure evidence and run the same provider-neutral acceptance plan against the next candidate (currently OCI), adapting only provider-specific API details. Do not weaken acceptance criteria to make a candidate pass.

## 9. Current disposition

**B2: CANDIDATE — TEST PLAN READY — NOT PROVISIONED — NOT TESTED.**  
**Fresh Holdout: BLOCKED.**  
**Production/trading authorization: NOT GRANTED.**
