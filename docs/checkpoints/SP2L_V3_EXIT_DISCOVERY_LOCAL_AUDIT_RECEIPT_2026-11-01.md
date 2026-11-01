# SP2L V3 Exit Discovery — Local Artifact Audit Receipt

Date: 2026-11-01

## Audit result

- Status: PASS
- Audit exit code: 0
- Variants: 288
- Frozen entry signals: 462
- Trade rows: 133,056
- Manifest SHA-256: `bea79456196e6e08b7186b1000eaec787d5ba6d697db0dd5c45bbb3322e49452`

## Local evidence location

`D:\\Mirzaei\\Private\\1\\sp2l-evidence\\development\\v3-exit-discovery-20261101\\SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_EVIDENCE_MANIFEST.json`

The manifest was generated and audited on the user's local Windows environment. Its bytes and the underlying local Discovery artifacts were not uploaded to this repository. The SHA-256 above is the user-reported digest of that local manifest and is recorded as an audit receipt, not as an independently re-hashed repository artifact.

## Scope and interpretation

The PASS records successful artifact-integrity auditing for the 288-variant, 462-signal, 133,056-row Discovery run. It does not establish statistical significance, out-of-sample performance, execution realism, canonical exit geometry, or production readiness. The Discovery results remain exploratory and in-sample. No exit variant is promoted to canonical.

The underlying M1 dataset has known gaps; no missing bars were synthesized. M1 OHLC proxy limitations, absent spread/slippage/commission modeling, and ambiguous trades remain applicable.

## Audit implementation provenance

Audit implementation: `scripts/audit_v3_discovery_artifacts.py`  
Implementation branch: `research/v3-discovery-artifact-audit-20261101`  
Tested implementation commit: `3deebf6e3c3c75e652aaa31f61fdd8f31b2aa3bc`  
Related implementation PR: #379 (Draft; not merged)

This receipt supplements the status snapshot dated 2026-11-01. It does not replace the local manifest or its source artifacts.
