# Candidate Lab — Verified Dataset Identity Contract

Date: 2026-10-11

## Scope

This change hardens the existing development-only Candidate Lab execution boundary. It does not implement or infer SP2L geometry, resolve source meaning, create production BUY/SELL decisions, or claim statistical edge.

## Required dataset identity

- A candidate plan must declare a SHA-256 as 64 lowercase hexadecimal characters.
- `run_candidate_matrix` requires an explicit local dataset artifact path.
- The runner hashes the raw artifact bytes and fails closed if the hash differs from the plan.
- The runner passes the same verified immutable `bytes` snapshot to each candidate adapter, along with the candidate.
- The runner re-hashes the artifact after each adapter call and at completion; mutation or read failure aborts the matrix.
- The adapter must execute only against the supplied byte snapshot and return an observation bound to the same candidate, plan, dataset SHA, execution fingerprint, geometry fingerprint, and source-resolution fingerprint.
- The runner explicitly rejects adapter results that alter either the declared geometry fingerprint or source-resolution fingerprint.
- This is a contract boundary, not cryptographic proof that a custom adapter's internal logic actually consumed the supplied bytes. Adapter-specific ingestion must be reviewed and tested before any real historical run.

## Research and data boundaries

- Candidate plans remain limited to immutable `DEVELOPMENT` datasets.
- Candidate ranking remains descriptive and does not select a canonical winner.
- No Untouched Validation, Fresh Holdout, or Forward dataset may be used for candidate optimization.
- Source resolution and frozen geometry remain blocked until source-confirmed rules and explicit fingerprints exist. Placeholder fingerprints in unit fixtures are test-only and are not research authorization.
- Synthetic fixtures verify software behavior only; they are not XAUUSD performance evidence.

## Local validation required

After pulling the commit, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_candidate_lab.py
.\.venv\Scripts\python.exe -m pytest -q
```

Record the actual local results. No passing result is claimed for this revision until those commands run successfully in the user's checkout.

Preserve untracked runtime artifacts and cache directories. Do not run the default Synthetic E2E again, repair/replay runtime journals, change the Forward Runner, alter Holdout data, or change canonical geometry as part of this step.
