# SP2L Evidence Artifact Verification — Research (2026-11-16)

**Status:** offline filesystem verifier authored; local synthetic validation pending  
**Canonical status:** non-canonical; no production caller  
**Scope:** exact-byte file existence/readability/length/SHA-256 verification for manifest artifacts

## Design decision: caller-resolved paths

The manifest's `locator` field is an opaque declaration. This verifier does not invent URI parsing, relative-path roots, path traversal rules, or locator-to-filesystem mapping. The caller must explicitly provide a mapping:

`artifact_id -> local filesystem path`

This makes the resolution decision visible and separate from verification.

## Verification behavior

For every manifest artifact, the verifier:
1. opens the supplied path in binary read mode;
2. confirms the opened object is a regular file;
3. streams bytes in 1 MiB chunks into SHA-256 while counting exact bytes;
4. compares file-descriptor metadata before and after reading to detect ordinary concurrent file changes;
5. compares observed byte length and SHA-256 against the manifest declaration.

The verifier never decodes text, normalizes line endings, parses CSV/JSON, sorts rows, or hashes semantic content. Every artifact receives an independent result. Overall success requires every declared artifact to verify.

## Outcomes

Report-level outcomes:
- `INVALID_MANIFEST`
- `INVALID_PATH_MAPPING`
- `ARTIFACTS_NOT_ALL_VERIFIED`
- `ALL_ARTIFACTS_VERIFIED`

Per-artifact outcomes:
- `PATH_NOT_SUPPLIED`
- `MISSING_PATH`
- `NOT_REGULAR_FILE`
- `READ_ERROR`
- `FILE_CHANGED_DURING_READ`
- `BYTE_LENGTH_MISMATCH`
- `SHA256_MISMATCH`
- `VERIFIED_EXACT_BYTES`

## Limits and safety boundary

- The caller controls path resolution; this layer does not constrain paths to a designated root.
- The verifier reads local files but does not modify them.
- Before/after metadata comparison detects ordinary concurrent changes, but is not an atomic snapshot, lock, immutable-storage guarantee, or defense against all adversarial filesystem races.
- A matching digest proves only that the bytes read from the supplied path match the declared length and digest. It does not prove who created the file, when it was captured, whether its contents faithfully represent MT5 history, or whether the manifest declaration is trusted.
- It does not verify manifest self-hash/signatures, provenance claims, history completeness, or observation-to-artifact semantic correspondence.
- It is not integrated with history recovery, MT5, a broker, an account worker, or the active Runner.

## Validation

Synthetic tests use temporary files and exact binary payloads, including NUL bytes and CRLF, empty files, length/digest mismatches, missing paths, directories, invalid mappings, and opaque locators. Local test execution is pending.
