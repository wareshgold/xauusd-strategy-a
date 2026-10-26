# Research Certification Display-Path Audit — 2026-10-26

## Scope

Read-only audit of the current Factory dashboard and report modules after the certification-ledger scope label was introduced on commit `2aadda5c6ebbfb5b3efb76ec47e747602470cc4c`.

## Findings

- `scripts/factory_dashboard.py` renders worker telemetry, job lifecycle, station state, and worker-journal integrity. It does not import or consume `ResearchCertificationLedger`, `ResearchCertification`, `LedgerReport`, or `build_ledger_report`, and it does not render `certified`, `production_eligible`, `certification_fingerprint`, or `verification_scope`.
- `src/strategy_factory/ledger_report.py` is a report for the separate experiment research ledger. It verifies a hash chain against caller-supplied expected tip and record count; it does not read the research certification ledger or assert certification authenticity.
- `src/strategy_factory/research_certification_ledger.py` serializes its explicit `verification_scope=SELF_CONSISTENT_FINGERPRINT_ONLY_NOT_AUTHENTICATED` marker. The marker describes the actual assurance level; it is not an authentication mechanism.
- Therefore, in the inspected paths, no existing Factory dashboard/report consumer was found that presents a certification-ledger entry as independently authenticated. Generic worker state labels such as `VERIFIED` are telemetry status values, not research-certificate status.

## Decision

No dashboard code change is warranted in this step: there is no certification-ledger display path to correct, and adding a new certification UI would create a new consumer rather than audit an existing one.

If a certification view is introduced later, it must display the verification scope verbatim and must not map self-consistent hashes to "authenticated", "trusted", "holdout passed", or production authorization. An authenticated certification requires an owner-selected external trust root and verification policy; neither is selected or implemented by this audit.

## Limits

This was a source-level audit of the named dashboard and report modules on the stated commit, not proof that arbitrary external consumers or downstream forks do not exist. No strategy rules, dataset roles, MT5 configuration, runner, or forward-test evidence were changed.


## Issuance-boundary follow-up

The certification object itself now carries `assurance_scope=SELF_CONSISTENT_EVIDENCE_CHAIN_NOT_AUTHENTICATED`, and validation rejects any different scope value. The certification-ledger entry binds and preserves that exact scope alongside its own `verification_scope=SELF_CONSISTENT_FINGERPRINT_ONLY_NOT_AUTHENTICATED`. This prevents accidental scope promotion in serialized records; it does not authenticate the caller or make a self-hashed, manually constructed object unforgeable. A selected external trust root and verified attestation are still required for issuer authentication.


## Follow-up: assurance scope propagation

On the follow-up branch revision, `UnifiedResearchQuality` now carries the explicit scope `SELF_CONSISTENT_EVIDENCE_CHAIN_NOT_AUTHENTICATED` inside its fingerprinted payload. Validation rejects scope promotion even if a caller recomputes the unkeyed fingerprint, and `ResearchCertification` checks that scope before consuming the quality result. This reduces ambiguity in the model contract but does not authenticate the evaluator or signer. CI results must be checked against the exact resulting HEAD before treating this follow-up as verified.
