# External Pin Trust-Root Readiness — 2026-10-26

## Repository inspection result

Read-only GitHub API inspection of `wareshgold/xauusd-strategy-a` on 2026-10-26 found:

- Repository rulesets endpoint returned an empty list (`[]`).
- Releases endpoint returned an empty list (`[]`).
- Three existing tags were listed, including `SP2L_SAFE_CHECKPOINT_2026-09-20_SOURCE_RESOLUTION` and `SP2L_SAFE_CHECKPOINT_2026-09-20_SOURCE_FEATURE_LAYER`.
- The listed branches returned `protected: false` in the branch inventory response. This does not establish that every possible repository-level control is absent, but no protected ruleset was exposed by the inspected endpoint.

## Decision

Do not treat the current research branch, its ordinary files, or a pin value stored alongside a ledger as an independent trust root. Existing checkpoint tags are not automatically suitable: their provenance, immutability controls, signer identity, and administrative separation must be independently established before using one to authenticate holdout pins.

No external pin provider has been wired into code because the current read-only evidence does not establish an independently administered trust channel. Adding a boolean, environment variable, or self-declared source label would not solve authenticity.

## Minimum conditions before trust-root activation

1. Select an independently controlled source for the expected ledger tip (for example, a signed attestation whose signing identity and issuer are verified, or a separately administered immutable registry).
2. Define who can publish/update pins and who can change the verifier; separate those permissions where practical.
3. Verify the source's cryptographic signature/attestation and bind the verified payload to the exact ledger tip and manifest revision.
4. Test missing, invalid, wrong-identity, revoked/untrusted, replayed, and mismatched-tip cases.
5. Record the trust-source identity, verification result, payload digest, and verification time as audit evidence. Do not let a caller-provided string alone mark a source as trusted.

## Scope and current state

This is a readiness assessment, not an assertion that a trust root is active. The pin ledger currently checks chain integrity and a caller-supplied expected tip; it does not authenticate the caller or external source. Fresh Holdout must remain blocked unless the surrounding workflow independently supplies and verifies the trust anchor.
