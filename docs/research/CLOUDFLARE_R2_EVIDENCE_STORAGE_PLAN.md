# Cloudflare R2 evidence storage — research implementation plan

Status: research-only; no credentials, bucket creation, upload, or runner integration performed.

## Intended role

Cloudflare R2 is the proposed remote object store for copies of local Strategy A
Forward Test evidence. The MT5 runner remains local and must continue writing
evidence locally first. Remote storage is a secondary replication target, never
a dependency for order placement or runner availability.

## Initial namespace

- Bucket: \`sp2l-forward-evidence\`
- Prefix: \`forward-test/\`
- Proposed object layout: \`forward-test/<run_id>/<UTC timestamp>_<filename>\`
- Each run should carry a manifest with SHA-256, byte length, source-relative path,
  UTC capture time, and upload status.
- Object names must be unique. The uploader must refuse overwrite and must not
  delete remote objects.

## Credentials and scope

R2 S3 credentials support bucket-scoped Object Read & Write permissions. The
documented token UI scopes these permissions to selected buckets. The current
diagnostics script is read-only and checks a single configured bucket and prefix.

Important limitation: bucket-scoped R2 credentials are not equivalent to a
prefix-scoped authorization policy. A local prefix guard is defense-in-depth,
not a server-side security boundary. Before enabling writes, evaluate Cloudflare
R2 temporary credentials with path restrictions, or use a dedicated bucket for
Forward Test evidence. Never reuse account-admin credentials in the runner.

## Integrity and immutability

- SHA-256 is computed locally before upload and stored in a sidecar manifest.
- Use unique run/object keys and conditional create-only writes where supported;
  never silently overwrite.
- Verify uploaded object size and checksum by reading metadata or downloading
  to a temporary verification path, then compare SHA-256.
- Keep local originals until remote verification succeeds.
- R2's S3 compatibility documentation currently lists S3 Object Lock operations
  as unsupported. Therefore this design does NOT claim WORM/object-lock
  immutability. Append-only naming and conditional writes reduce accidental
  overwrites but do not prevent a sufficiently privileged key holder from
  deleting objects.
- No lifecycle deletion/transition rules are configured by this project.

## Failure behavior

1. Write evidence to local disk first.
2. Queue remote replication work separately.
3. On network/authentication failure, retain local files and record a retryable
   sync failure; never block or alter trading decisions.
4. Retry idempotently using the same object key and create-only semantics.
5. Mark a run remotely complete only after all object checksums and the final
   manifest have been verified.

## Cost notes

Cloudflare's published R2 Standard pricing currently includes 10 GB-month,
1 million Class A requests, and 10 million Class B requests per month; internet
egress is free. Paid Standard storage is listed at USD 0.015 per GB-month.
Actual account billing and limits must be checked before production use.

## Implementation stages

1. Read-only bucket diagnostics (this change).
2. Synthetic local fixture and manifest tests.
3. Explicitly approved write-test to a dedicated test prefix.
4. Upload + metadata/checksum verification and retry tests.
5. Forward Runner integration behind an opt-in flag, local-first.
6. Production use only after user review and operational validation.

## References

- R2 S3 API and credential setup: https://developers.cloudflare.com/r2/get-started/s3/
- R2 token permissions and S3 endpoint: https://developers.cloudflare.com/r2/api/tokens/
- R2 temporary credentials and optional path restrictions: https://developers.cloudflare.com/r2/api/s3/temporary-credentials/
- R2 S3 compatibility (including unsupported Object Lock operations):
  https://developers.cloudflare.com/r2/api/s3/api/
- R2 pricing: https://developers.cloudflare.com/r2/pricing/
- R2 consistency and conditional writes: https://developers.cloudflare.com/r2/reference/consistency/
