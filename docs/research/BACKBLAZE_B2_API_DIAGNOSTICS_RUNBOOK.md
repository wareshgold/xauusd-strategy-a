# Backblaze B2 API diagnostics — operator runbook

**Status:** READ-ONLY DIAGNOSTIC SCRIPT; NOT A KEY-CREATION OR STORAGE INTEGRATION  
**Bucket:** sp2l-factory-evidence  
**Bucket ID:** 0bd958e97ddd990eae1f0a1c  
**Prefix reserved for later test work:** factory/

## Purpose

The operator previously encountered a failure during b2_create_key after successful account authorization. The earlier script did not preserve the HTTP response body reliably, so the actual B2 error code was not captured.

This change adds a diagnostic-only PowerShell script. It:
1. Authorizes locally entered Master Application Key credentials.
2. Reads the v4 authorization capability envelope.
3. Reads metadata for the one known bucket using b2_list_buckets.
4. Reports the Object Lock configuration only if the API returns it.

It does **not** create, list, or delete application keys; upload or delete files; or modify bucket settings.

## Important API version correction

The current Backblaze Native API v4 schema uses different field names for two different operations:

- b2_create_key: bucketIds (plural array) for bucket restrictions.
- b2_list_buckets: bucketId (singular string) to filter the bucket listing.

The prior troubleshooting statement that v4 b2_create_key should use singular bucketId was incorrect. Do not apply that suggestion. The earlier key-creation payload already used the documented v4 bucketIds field, so the exact cause of its failure remains undetermined until an HTTP/API error is captured.

## Run

From the repository root in Windows PowerShell 5.1 or later:

    Set-ExecutionPolicy -Scope Process Bypass
    .\scripts\research\diagnose_b2_evidence_bucket.ps1

Enter the Master Application Key ID and secret only into the local PowerShell prompts. The secret prompt is hidden.

## Expected output

The script reports:
- Authorization pass/fail.
- Whether the authorization response includes writeKeys, listBuckets, and readBucketRetentions.
- Whether the expected bucket ID resolves to the expected bucket name.
- Object Lock and default-retention readback, when authorized and returned.
- A sanitized HTTP status and B2 error code/message when a request fails.

It never prints the Master Application Key secret, Basic Authorization value, authorization token, or account ID. Do not paste secrets or full terminal transcripts containing credentials into chat.

## Safety and interpretation

- A successful diagnostic does not prove that b2_create_key will succeed.
- The script deliberately does not call b2_create_key.
- A returned writeKeys=true only confirms that the current authorization envelope advertises that capability; it is not a reason to expose the Master key to Runtime.
- A failed bucket read may reflect an authorization or account/API issue; retain the sanitized error for diagnosis.
- No key should be created until the precise prior failure is understood and the request schema has been reviewed against the current vendor API.

## Vendor references

- [b2_authorize_account v4](https://www.backblaze.com/apidocs/b2-authorize-account)
- [b2_list_buckets v4](https://www.backblaze.com/apidocs/b2-list-buckets)
- [b2_create_key v4](https://www.backblaze.com/apidocs/b2-create-key)
