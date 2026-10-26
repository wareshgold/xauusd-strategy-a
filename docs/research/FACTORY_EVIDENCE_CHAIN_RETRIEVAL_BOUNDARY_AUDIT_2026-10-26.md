# Research Evidence Chain Retrieval-Boundary Audit — 2026-10-26

## Scope

Read-only source audit of the run, evidence, snapshot, audit, provenance, record, bundle, acceptance, quality, and certification path at commit `4264d26f2191a58f39b12b6fe92fce6cac46efbd`.

## Findings

### Internal consistency

`ResearchRunIdentity.fingerprint` hashes run identity and parameters. `EvidenceLedger.record` resolves the run in its in-memory ledger and checks the evidence run fingerprint. `bind_research_audit` validates and binds the run, snapshot, and evidence. `ResearchRecord` validates its own fingerprint and checks supplied component relationships. Statistical/stability evidence and the bundle bind to the research record and its upstream evidence fingerprints. These are useful consistency and tamper-detection checks when the original trusted inputs are available.

### Provenance decision is not independently replay-verifiable

`ResearchProvenanceResult` contains only `status` and `reasons`; it has no input fingerprints or decision fingerprint. `evaluate_research_provenance` evaluates the spec, job, run, execution receipt, evidence, audit, snapshot, and dataset provenance. However, `ResearchRecord.from_components` receives only the result and checks that its status is `PASS`; it cannot independently replay the decision against the original inputs. A caller can construct `ResearchProvenanceResult(status=PASS, reasons=())` directly. The record constructor still checks the supplied record components, but it cannot prove this PASS was produced by `evaluate_research_provenance`.

Adding an unkeyed hash to the result alone would improve deterministic integrity, not authenticate the evaluator or prevent a caller from recomputing a forged hash.

### Fingerprints do not make source artifacts retrievable

`ResearchRecord` stores identifiers and fingerprints for dataset, evidence, snapshot, and audit, but not the complete original dataset bytes, execution receipt, spec/job, or a durable retrieval locator and policy for each artifact. In-memory registries are not by themselves durable retrieval or independent source authentication.

The current design is best described as deterministic cross-object consistency checking over supplied objects—not an independently replayable, durable evidence archive or authenticated issuance chain.

## Recommended next implementation boundary

Define an immutable provenance-decision record binding schema and policy revision; run, spec, job, receipt, evidence, audit, snapshot, and dataset-provenance fingerprints; status and stable reason codes; artifact identifiers; and a documented retrieval/retention contract. Record creation should verify the decision binds the exact same components. Add adversarial tests for manually constructed PASS results, cross-run/cross-dataset reuse, missing artifacts, and fingerprint mismatches. Treat digests as integrity only; independent authenticity requires a separately selected trust root and verification policy.

## Decision and limits

Audit only; no code change claims provenance is authenticated or replayable. No canonical SP2L geometry, dataset role, execution semantics, MT5 configuration, runner, or forward-test evidence was changed.
