# Independent checkpoint provider evaluation

**Status:** RESEARCH EVALUATION TEMPLATE — NO PROVIDER SELECTED  
**Related design:** `FRESH_HOLDOUT_TRUST_ANCHOR_REQUIREMENTS.md`  
**Scope:** Evidence required before implementing an independent audit-checkpoint adapter.

## Purpose and decision boundary

Use this document to evaluate concrete provider/deployment candidates against the anti-truncation requirements. It is a comparison template, not a vendor recommendation, implementation contract, security certification, or authorization to run Fresh Holdout.

Do not assign a candidate a passing status from marketing material, a mock, a unit test, or an unverified operator statement. A requirement is **EVIDENCED** only when the cited provider documentation and/or controlled test evidence directly supports the exact guarantee in the proposed deployment configuration. Otherwise mark it **OPEN** or **NOT SUPPORTED**.

No provider, cloud, private server, credential mechanism, retention tier, or deployment topology is selected by this document.

## Mandatory evaluation dimensions

| ID | Dimension | Evidence required | Fail-closed acceptance condition |
|---|---|---|---|
| P1 | Administrative independence | Identity/role matrix showing who can write, delete, administer, and recover remote checkpoints versus who administers the runtime host and local audit directory | No single runtime/local-audit administrator can silently rewrite or erase the independently retained checkpoint history |
| P2 | Atomic uniqueness and idempotency | Provider-specific documentation and controlled tests for uniqueness scope, atomic conditional create, duplicate request handling, conflict response, and idempotency retention | Same logical request is safely confirmable; same identity/sequence with a different digest is rejected |
| P3 | Authoritative latest read | API contract and tests showing how the latest checkpoint is selected, including pagination/version semantics and consistency guarantees | A read can identify the authoritative latest revision; unavailable, stale, or ambiguous reads never authorize |
| P4 | Read-after-write and lost response | Controlled fault-injection evidence for commit-before-response-loss, then lookup/retry using the same immutable request identity | The original committed checkpoint and authenticated receipt can be reconciled without creating a second logical checkpoint |
| P5 | Rollback and deletion resistance | Retention/immutability controls, privileged-role analysis, deletion/restore behavior, and adversarial tests | Runtime and local-audit administrators cannot roll back or erase the independent history within the stated threat model |
| P6 | Receipt authenticity and service identity | Documented authentication/signature mechanism, trust distribution, rotation/revocation, and negative verification tests | Receipt authenticity and service identity are independently verifiable and bind the exact request and accepted checkpoint |
| P7 | Revision monotonicity and conflict visibility | API semantics for revisions/ETags/generations/sequence numbers and tests for concurrent writers and stale reads | Revisions cannot be silently rolled back or mistaken for the latest accepted state; conflicting tips are observable |
| P8 | Durability and retention | Explicit durability/retention commitments, deletion/expiry behavior, backup and disaster-recovery documentation | Retention covers the required audit lifetime; expiry or loss cannot silently downgrade the gate |
| P9 | Export and independent auditability | Evidence that checkpoint history, access events, administrative changes, and receipts can be exported and independently reviewed | Required evidence remains retrievable outside the provider's ordinary application path |
| P10 | Availability and outage policy | Service availability model, outage behavior, rate limits, retry guidance, regional/dependency failure modes | When service guarantees cannot be established, the system remains unanchored/unknown and blocks protected transitions |
| P11 | Identity and secret handling | Supported workload identity or secret delivery, least-privilege policy, rotation/revocation and incident procedures | Credentials are not stored in source control, audit payloads, artifacts, or logs; compromised credentials can be revoked |
| P12 | Operational separation and recovery | Named operator/reviewer roles, change control, restore drills, incident escalation, and evidence retention | Recovery cannot be performed solely by the evidence producer without independent review and retained proof |

## Evidence grading

Use one status per dimension:

- **EVIDENCED** — exact guarantee is supported by versioned provider documentation and/or reproducible controlled tests for the candidate configuration.
- **PARTIAL** — some relevant evidence exists, but scope, failure mode, role separation, or deployment applicability is incomplete.
- **OPEN** — evidence has not been collected or reviewed.
- **NOT SUPPORTED** — provider behavior or deployment constraints do not satisfy the acceptance condition.

Every EVIDENCED or PARTIAL entry must cite:
1. Source title, version/date, exact section or API operation.
2. Candidate service/tier/region/configuration and API version.
3. Test ID, timestamp, adapter/build version, environment, and authenticated service identity (for test evidence).
4. Observed result and retained sanitized response/receipt.
5. Independent reviewer and review date.

A documentation statement is not a substitute for a fault-injection test where the requirement concerns actual failure behavior. A test result is not a substitute for contractual or documented retention/durability guarantees.

## Candidate record template

Create one copy of this record per concrete candidate. Do not compare different tiers or deployment configurations as if they were the same candidate.

- Candidate name and exact service/tier:
- Deployment model and region:
- API/service version:
- Proposed independent administrative boundary:
- Runtime identity:
- Local audit administrator:
- Remote checkpoint administrator:
- Evidence producer:
- Independent reviewer:
- Data retention requirement:
- Expected checkpoint frequency:
- Recovery/export requirement:
- Known dependencies and outage policy:

| ID | Status | Evidence reference(s) | Reviewer notes / unresolved gap |
|---|---|---|---|
| P1 | OPEN | — | |
| P2 | OPEN | — | |
| P3 | OPEN | — | |
| P4 | OPEN | — | |
| P5 | OPEN | — | |
| P6 | OPEN | — | |
| P7 | OPEN | — | |
| P8 | OPEN | — | |
| P9 | OPEN | — | |
| P10 | OPEN | — | |
| P11 | OPEN | — | |
| P12 | OPEN | — | |

## Disqualifying conditions

Reject a candidate for this control if any of the following is true:

- The runtime identity or local audit administrator can modify/delete the only remote checkpoint history.
- The service cannot distinguish exact replay from a conflicting digest at the same audit identity and sequence.
- The service cannot provide an authoritative latest-checkpoint read, or its consistency/rollback behavior is undocumented and untestable.
- A lost publish response cannot be reconciled safely without guessing or creating a second logical checkpoint.
- Receipts cannot be authenticated and bound to the immutable request and accepted checkpoint.
- Required checkpoint history can expire, be deleted, or be restored to an older state without independently detectable evidence.
- The deployment requires local-cache fallback or treats timeout as success.
- Credentials or private signing material must be embedded in source, test fixtures, or audit records.
- Administrative separation cannot be demonstrated and independently reviewed.

## Selection and implementation gate

A candidate may be recommended for a controlled adapter prototype only when P1–P12 have been reviewed, every mandatory safety dimension is EVIDENCED, no disqualifying condition remains, and the independent reviewer accepts the threat model and deployment boundary.

A prototype passing synthetic tests does not establish provider guarantees. Before any production claim, run the R1–R8 provider recovery matrix in `FRESH_HOLDOUT_TRUST_ANCHOR_REQUIREMENTS.md` against a controlled provider environment, retain independent evidence, and review crash/recovery behavior. Keep all protected transitions blocked for any OPEN, PARTIAL, unavailable, stale, or ambiguous checkpoint state.

## Explicit non-claims

This template does not establish that any provider is suitable, does not choose a canonical request serialization or receipt format, does not define a production retry/state machine, and does not enable Fresh Holdout, Forward, Runtime, MT5 execution, or production BUY/SELL decisions.
