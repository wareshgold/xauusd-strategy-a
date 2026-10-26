# Provenance Decision Record Contract — Research Follow-up — 2026-10-26

## Implemented contract in this branch

The `ResearchProvenanceResult` now carries:
- schema revision `RESEARCH-PROVENANCE-DECISION-1`;
- sorted input fingerprints for the test specification, research job, run identity, execution receipt, evidence bundle, research audit, readiness snapshot, and dataset-provenance result on a PASS decision;
- decision status and reason codes;
- a deterministic `decision_fingerprint` over the schema revision, status, reasons, and input-fingerprint mapping.

A PASS result without input fingerprints fails validation. A changed status/reason/input binding without recomputing the digest fails fingerprint validation. Non-PASS results retain reasons and a deterministic decision fingerprint but do not claim a complete successful input binding.

`ResearchRecord.from_components` now validates the provenance decision and requires the decision to bind the exact supplied run, evidence, snapshot, and audit serializations. The research record stores the provenance decision fingerprint as part of its own fingerprinted payload. This prevents accidentally reusing an intact decision for different core components.

## Security and assurance boundary

This is a deterministic integrity and cross-object binding improvement, not evaluator authentication. The digest is unkeyed; a caller able to construct arbitrary objects can recompute a digest. The result therefore does not prove that the official evaluator produced it, nor that a receipt describes a real execution. The execution receipt is still a contract declaration, and artifact availability/authenticity remains a separate concern.

Do not describe this decision record as signed, independently authenticated, or a durable archive. Those properties require a separately selected trust root, verification policy, and artifact retrieval/retention design.

## Tests added

- exact successful provenance produces a valid decision fingerprint and bound input fingerprints;
- changing decision reasons without updating the fingerprint is rejected;
- the decision binds execution receipt and dataset-provenance inputs;
- a manually constructed unbound PASS cannot be accepted by `ResearchRecord.from_components`;
- a decision generated for one run cannot be reused for a different run;
- non-PASS provenance remains rejected by the research record.

## Next boundary

If independent replay is required, persist the canonical input artifacts and their schema/version in a durable, content-addressed store; then add a replay function that loads the exact artifacts, reruns the policy revision, and compares the resulting decision fingerprint. Independent issuer authenticity still requires a trusted signature/attestation or separately administered trust root. No unkeyed hash or caller-supplied boolean can substitute for it.

## Scope exclusions

No SP2L geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, execution rule, dataset-role policy, production BUY/SELL decision, MT5 configuration, live runner, or forward-test artifact was changed.
