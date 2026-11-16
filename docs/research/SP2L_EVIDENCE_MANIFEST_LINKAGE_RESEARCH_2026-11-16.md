# SP2L Evidence Manifest ↔ History Observation Linkage (2026-11-16)

**Status:** offline research implementation; local synthetic validation pending  
**Canonical status:** non-canonical; no production caller  
**Runtime boundary:** no filesystem access, artifact reads, hashing, serialization, MT5 calls, or Runner integration

## Purpose

Check whether a valid manifest record declares the same account/session/server, interval, time basis/source, package version, and terminal build as one or more supplied history observations, and whether those observation IDs are listed in that manifest.

## Deterministic outcomes

- `INVALID_MANIFEST`: manifest record fails its own structural validator.
- `INVALID_OBSERVATION`: no observations, wrong container/type, invalid underlying completeness evidence, malformed digest shape, or duplicate observation IDs.
- `OBSERVATION_NOT_LISTED`: a supplied observation ID is absent from the manifest's declared ID tuple.
- `SCOPE_MISMATCH`: any compared declared scope field differs.
- `LINKED_FOR_DECLARED_SCOPE`: every supplied observation is valid, listed, and matches all compared scope fields.

The function accepts a non-empty subset of the manifest's observation IDs. It does not require the supplied tuple to contain every observation listed by the manifest.

## Explicit limits

This is metadata linkage, not artifact linkage. The model does not establish that:
- artifact locators exist or point to the claimed bytes;
- byte lengths or SHA-256 digests are true;
- an artifact contains the observation it is declared to represent;
- the manifest itself is immutable, signed, or trusted;
- the observations are complete or atomic.

Artifact roles remain operator-declared strings; this layer does not invent required role names or infer a mapping from roles to MT5 API calls. A linked result cannot set `history_completeness_verified=True`.

## Validation

Synthetic tests cover matching and mismatching account/session/server/time scopes, observation membership, invalid evidence, and duplicate IDs. Local validation is pending.
