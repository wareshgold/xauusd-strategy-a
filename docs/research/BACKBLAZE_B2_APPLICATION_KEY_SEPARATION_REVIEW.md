# Backblaze B2 application-key separation review

**Status:** PUBLIC DOCUMENTATION REVIEW — NO ACCOUNT INSPECTED, NO KEYS CREATED  
**Reviewed:** 2026-10-31  
**Related:** `BACKBLAZE_B2_CONTROLLED_FEASIBILITY_TEST_PLAN.md`  
**Disposition:** ADVANCE TO OPERATOR-APPROVED SANDBOX ONLY IF ACCOUNT OWNERSHIP/ADMIN SEPARATION IS ACCEPTABLE

## 1. Findings from current vendor documentation

Backblaze documents scoped standard application keys that can be restricted by bucket, file-name prefix, capability set, and optional expiry. Standard keys can be revoked independently and continue to work when the master application key is changed. The master application key, by contrast, has complete account access, all capabilities, all buckets, and no prefix or expiry restriction.

The capability model is granular. Relevant capabilities include:
- `writeFiles`: upload and related large-file operations; documentation also lists `b2_hide_file` under this capability.
- `readFiles`, `listFiles`: read object content/metadata and list files.
- `readFileRetentions`: inspect per-file Object Lock retention.
- `writeFileRetentions`: update per-file retention settings.
- `readBucketRetentions` / `writeBucketRetentions`: inspect or alter bucket default retention/Object Lock configuration.
- `deleteFiles`: delete file versions.
- `bypassGovernance`: bypass Governance-mode protection; not applicable as a Compliance-mode bypass.
- `writeKeys`: create application keys. Backblaze explicitly warns that this capability grants full access to the B2 account because the created keys can have unrestricted capabilities.
- `deleteKeys`, `listKeys`: manage or enumerate application keys.

Sources: Backblaze Application Keys and Application Key Capabilities (links below).

## 2. Preliminary least-privilege key design for sandbox testing

This is a proposed test profile, not a verified working configuration. The exact S3-compatible API calls and capability mapping must be validated before use.

| Identity | Candidate permissions | Explicitly exclude |
|---|---|---|
| Runtime uploader | Single sandbox bucket + narrow prefix; only the minimum upload capability set; expiry where operationally practical | `writeKeys`, `deleteKeys`, `writeBucketRetentions`, `writeFileRetentions`, `deleteFiles`, `bypassGovernance`, bucket creation/deletion, lifecycle/policy administration |
| Independent verifier | Single sandbox bucket + test prefix; `readFiles`, `listFiles`, `readFileRetentions` as required | All write, delete, key-management, retention-write, and policy-write capabilities |
| Provisioning/admin | Held outside runtime; used only to create bucket/keys and configure reviewed retention | Never supplied to Factory/runtime, CI, test scripts, or operator automation |

Important qualification: Backblaze's published capability list shows that bucket-restricted keys may include retention-write and governance-bypass capabilities. Therefore, bucket scoping alone is not enough; the capability set itself must be inspected and tested.

The runtime upload path must be checked carefully because `writeFiles` includes `b2_hide_file` in the Native API capability mapping. The sandbox must test whether this or any S3-compatible operation can affect the intended object identity/version under Compliance retention. Do not infer that a key lacking `deleteFiles` is automatically unable to perform every logical hide/replace action.

## 3. What this documentation does and does not prove

**Documented:**
- Runtime credentials can be bucket/prefix scoped and capability-limited.
- A separate read-only application key is supported in principle.
- Standard keys can expire and be revoked without changing the master key.
- Master key is account-wide and highly privileged.
- Key-creation capability `writeKeys` is account-wide in effect and must never be granted to runtime.

**Not proven:**
- Independent human/account administration from the runtime operator. Application keys are not, by themselves, a separate account-owner boundary.
- Whether the exact planned S3 API requests can be performed with a minimal key lacking every retention/policy/key-management capability.
- Whether the selected S3 conditional-write operation behaves atomically under concurrent requests.
- Whether any account-console administrator, recovery path, or account closure operation can defeat the desired independent evidence retention.
- Whether the runtime can exploit `writeFiles`/hide/version semantics to alter the logical checkpoint history.
- Whether the chosen free-tier account and usage remain free for the test.

## 4. Required operator and sandbox evidence

Before provisioning, document:
1. Who owns the Backblaze account and who can sign in to the console.
2. Whether account ownership/admin is independent of the Factory runtime identity and credentials.
3. Which principals can rotate the master key, create/revoke app keys, change account settings, delete buckets, or close/recover the account.
4. The exact capability arrays and bucket/prefix/expiry constraints for each test key.
5. Runtime negative tests for every forbidden capability, including hide, overwrite/new-version, delete-version, retention update, bucket retention update, key creation, and bucket lifecycle changes.
6. Independent verifier negative tests for all mutation operations.
7. Readback of actual per-object Compliance mode and expiry after every upload.

If a truly independent account owner/admin boundary is required but unavailable, B2 cannot be approved as the sole anti-truncation trust anchor even if object-level Compliance retention behaves as documented.

## 5. Decision

The public documentation supports a credible least-privilege sandbox design. It does **not** establish the independent account administration boundary or the exact object/API semantics required by the SP2L checkpoint protocol.

**B2 remains an unselected candidate.** This review supports moving to an operator-approved disposable sandbox only after account ownership/admin separation is explicitly accepted. It does not authorize provisioning, integration, Fresh Holdout, production, or trading.

## 6. Vendor sources

- Application Keys: https://www.backblaze.com/docs/cloud-storage-application-keys
- Application Key Capabilities: https://www.backblaze.com/docs/cloud-storage-application-key-capabilities
- B2 API key listing and capability schema: https://www.backblaze.com/apidocs/b2-list-keys
- Creating and Managing Application Keys: https://help.backblaze.com/hc/en-us/articles/360052129034-Creating-and-Managing-Application-Keys
